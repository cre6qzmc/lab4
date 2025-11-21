import os
from passlib.context import CryptContext
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

pwd_context = CryptContext(
    schemes=[os.getenv("HASH_SCHEME", "argon2")],
    argon2__time_cost=int(os.getenv("ARGON2_TIME_COST", 2)),
    argon2__memory_cost=int(os.getenv("ARGON2_MEMORY_COST", 102400)),
    argon2__parallelism=int(os.getenv("ARGON2_PARALLELISM", 8))
)

def get_password_hash(password: str) -> str:
    hash_result = pwd_context.hash(password)
    logger.info(f"Password hashed successfully with scheme: {pwd_context.default_scheme}")
    return hash_result

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)