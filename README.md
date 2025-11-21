# Запуск проекта

### Запуск всех сервисов
```bash
docker-compose up --build
```
### Запуск в фоновом режиме
```bash
docker-compose up --build -d
```

# Проверка работоспособности

Frontend: http://localhost:3000 \
API Documentation: http://localhost:8000/docs \
Health Check: http://localhost:8000/health \

# Структура проекта
```bash
auth-project/
│
├── backend/                 # Python FastAPI приложение 
│   ├── alembic/            # Миграции базы данных
│   ├── tests/              # Автотесты
│   ├── main.py             # Точка входа FastAPI
│   ├── models.py           # SQLAlchemy модели
│   ├── schemas.py          # Pydantic схемы валидации
│   ├── auth.py             # Логика аутентификации
│   ├── database.py         # Подключение к БД
│   └── requirements.txt    # Python зависимости
│
├── frontend/               # React TypeScript приложение
│   ├── src/
│   │   ├── components/     # React компоненты
│   │   │   ├── Register.tsx
│   │   │   ├── Login.tsx
│   │   │   └── SuccessPage.tsx
│   │   ├── App.tsx         # Главный компонент
│   │   └── main.tsx        # Точка входа
│   ├── public/images/      # Статические ресурсы
│   └── package.json        # Node.js зависимости
│
├── docker-compose.yml      # Оркестрация контейнеров
├── .env.example           # Пример переменных окружения
└── README.md              # Документация
```

# Архитектурная схема
```pgsql
┌─────────────────┐    HTTP    ┌─────────────────┐    SQL    ┌─────────────────┐
│   Frontend      │ ◄─────────►│    Backend      │ ◄────────►│   Database      │
│                 │            │                 │           │                 │
│ React + TS      │    REST    │ FastAPI +       │   ORM     │ PostgreSQL      │
│ localhost:3000  │   API      │ Python          │ (SQLAlchemy) localhost:5432 │
│                 │            │ localhost:8000  │           │                 │
└─────────────────┘            └─────────────────┘           └─────────────────┘
       │                              │                              │
       │ Docker Container             │ Docker Container             │ Docker Container
       └──────────────────────────────┴──────────────────────────────┘
                              Docker Compose
							  
```
# CURL-запросы
### Регистрация пользователя
```bash
curl -X POST "http://localhost:8000/api/register" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "testuser",
    "password": "Test123!@#"
  }'
```
### Авторизация пользователя
```bash
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{
    "login": "testuser",
    "password": "Test123!@#"
  }'
```
### Проверка здоровья сервиса
```bash
curl "http://localhost:8000/health"
```
### Дублирующий логин
```bash
curl -X POST "http://localhost:8000/api/register" \
  -H "Content-Type: application/json" \
  -d '{"login": "testuser", "password": "Another123!@"}'
```
### Слабый пароль
```bash
curl -X POST "http://localhost:8000/api/register" \
  -H "Content-Type: application/json" \
  -d '{"login": "newuser", "password": "weak"}'
```
### Неверные учетные данные
```bash
curl -X POST "http://localhost:8000/api/login" \
  -H "Content-Type: application/json" \
  -d '{"login": "wronguser", "password": "Wrong123!"}'
```

# Запуск автотестов

```bash
docker-compose exec backend pytest tests/ -v
```

- Успешная регистрация пользователя
- Обработка дублирующих логинов
- Валидация слабых паролей
- Успешная авторизация
- Обработка неверных учетных данных

## Мониторинг логов

```bash
docker-compose logs backend
docker-compose logs frontend
```

## Безопасность: что сделано
- Хэширование паролей - используется Argon2id с автоматической генерацией соли
- Никогда не храним пароли в открытом виде - только хэши в базе данных
- Строгая валидация логинов - 3-32 символа, только латиница/цифры/._-
- Требования к сложности паролей - минимум 8 символов, верхний/нижний регистр, цифры, спецсимволы
- Защита от SQL-инъекций - использование ORM SQLAlchemy с параметризованными запросами
- Уникальные индексы - предотвращение дублирования логинов на уровне базы данных
- Изоляция сервисов - каждый компонент в отдельном Docker контейнере
- "Нелогирование" чувствительных данных - пароли никогда не попадают в логи

