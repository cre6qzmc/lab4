from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import logging
import time
import json
from datetime import datetime

from database import get_db, engine
import models
import schemas
from auth import get_password_hash, verify_password

# Настройка структурированного логирования
class JSONFormatter(logging.Formatter):
    def format(self, record):
        log_entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "module": record.module,
            "function": record.funcName,
            "line": record.lineno
        }
        if hasattr(record, 'user_login'):
            log_entry['user_login'] = record.user_login
        if hasattr(record, 'event_type'):
            log_entry['event_type'] = record.event_type
        return json.dumps(log_entry)

# Настройка логгера
logger = logging.getLogger("auth_api")
logger.setLevel(logging.INFO)

handler = logging.StreamHandler()
handler.setFormatter(JSONFormatter())
logger.addHandler(handler)

# Создание таблиц
def create_tables():
    max_retries = 5
    for i in range(max_retries):
        try:
            models.Base.metadata.create_all(bind=engine)
            logger.info("Database tables created successfully", extra={'event_type': 'database_setup'})
            break
        except Exception as e:
            logger.warning(f"Failed to create tables (attempt {i+1}/{max_retries}): {e}", extra={'event_type': 'database_retry'})
            if i < max_retries - 1:
                time.sleep(5)
            else:
                logger.error("Failed to create tables after all retries", extra={'event_type': 'database_error'})
                raise

create_tables()

app = FastAPI(
    title="Auth API",
    description="MVP для регистрации и аутентификации пользователей",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://frontend:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/register", response_model=schemas.UserResponse)
async def register(user: schemas.UserCreate, db: Session = Depends(get_db)):
    try:
        # Хэширование пароля
        hashed_password = get_password_hash(user.password)
        
        # Создание пользователя
        db_user = models.User(login=user.login, password_hash=hashed_password)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        
        # Логирование успешной регистрации
        logger.info(
            f"User registered successfully: {user.login}",
            extra={
                'event_type': 'user_registered',
                'user_login': user.login,
                'user_id': db_user.id
            }
        )
        
        return {"message": "user создан", "user_id": db_user.id}
        
    except IntegrityError:
        db.rollback()
        logger.error(
            f"Registration failed - duplicate login: {user.login}",
            extra={
                'event_type': 'registration_failed',
                'user_login': user.login,
                'reason': 'duplicate_login'
            }
        )
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Login already exists"
        )
    except ValueError as e:
        logger.error(
            f"Registration failed - validation error: {str(e)}",
            extra={
                'event_type': 'registration_failed', 
                'user_login': user.login,
                'reason': 'validation_error',
                'details': str(e)
            }
        )
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except Exception as e:
        db.rollback()
        logger.error(
            f"Registration failed - server error: {str(e)}",
            extra={
                'event_type': 'registration_failed',
                'user_login': user.login,
                'reason': 'server_error'
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.post("/api/login")
async def login(login_data: schemas.LoginRequest, db: Session = Depends(get_db)):
    try:
        # Поиск пользователя
        user = db.query(models.User).filter(models.User.login == login_data.login).first()
        
        if not user:
            logger.warning(
                f"Login failed - user not found: {login_data.login}",
                extra={
                    'event_type': 'login_failed',
                    'user_login': login_data.login,
                    'reason': 'user_not_found'
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login or password"
            )
        
        # Проверка пароля
        if not verify_password(login_data.password, user.password_hash):
            logger.warning(
                f"Login failed - invalid password for: {login_data.login}",
                extra={
                    'event_type': 'login_failed',
                    'user_login': login_data.login,
                    'reason': 'invalid_password'
                }
            )
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid login or password"
            )
        
        # Успешный логин
        logger.info(
            f"User logged in successfully: {login_data.login}",
            extra={
                'event_type': 'login_success',
                'user_login': login_data.login,
                'user_id': user.id
            }
        )
        
        return {
            "message": "Login successful",
            "user_id": user.id,
            "login": user.login
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(
            f"Login failed - server error: {str(e)}",
            extra={
                'event_type': 'login_failed',
                'user_login': login_data.login,
                'reason': 'server_error'
            }
        )
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error"
        )

@app.get("/")
async def root():
    return {"message": "Auth API is running"}

@app.get("/health")
async def health_check():
    return {"status": "healthy"}