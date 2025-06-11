# FastAPI Clean Architecture with MySQL, Redis, and Kafka

A production-ready FastAPI application following Clean Architecture principles, with MySQL for the database, Redis for caching, and Kafka for event streaming.

## Features

- Clean Architecture with clear separation of concerns
- Async database operations with SQLAlchemy 2.0
- JWT Authentication
- Redis for caching
- Kafka for event streaming
- Database migrations with Alembic
- Environment-based configuration
- Type hints and Pydantic models

## Prerequisites

- Python 3.9+
- MySQL 8.0+
- Redis 6.0+
- Apache Kafka 2.8+
- Docker and Docker Compose (optional)

## Setup

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd clean_python
   ```

2. **Create a virtual environment and activate it**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   Copy the example environment file and update the values:
   ```bash
   cp .env.example .env
   ```
   Update the `.env` file with your database credentials and other settings.

5. **Set up the database**
   - Create a MySQL database
   - Update the `DATABASE_URL` and `DATABASE_SYNC_URL` in `.env`

6. **Initialize the database**
   ```bash
   python -m scripts.init_db
   ```

7. **Run database migrations (optional)**
   ```bash
   alembic upgrade head
   ```

## Running the Application

1. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

2. **Access the API documentation**
   - Swagger UI: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc

## Running with Docker (Optional)

1. **Start the services**
   ```bash
   docker-compose up -d
   ```

2. **Initialize the database**
   ```bash
   docker-compose exec app python -m scripts.init_db
   ```

## Project Structure

```
.
├── alembic/                  # Database migration files
├── app/
│   ├── core/                 # Core functionality
│   ├── domain/                # Domain models and interfaces
│   │   ├── entities/          # Pydantic models
│   │   ├── interfaces/        # Abstract repositories
│   │   └── use_cases/         # Business logic
│   ├── infrastructure/        # External implementations
│   │   ├── config/           # Configuration
│   │   ├── database/         # Database setup and models
│   │   ├── kafka/           # Kafka producers/consumers
│   │   └── redis/           # Redis client
│   └── presentation/         # API layer
│       └── api/v1/           # API version 1
│           ├── dtos/         # Data transfer objects
│           └── routers/      # FastAPI routers
├── scripts/                  # Utility scripts
├── tests/                    # Test files
├── .env                      # Environment variables
├── .env.example              # Example environment variables
├── .gitignore
├── alembic.ini              # Alembic configuration
├── docker-compose.yml        # Docker Compose file
├── Dockerfile               # Dockerfile for the application
├── requirements.txt         # Python dependencies
└── README.md               # This file
```

## API Endpoints

### Authentication

- `POST /auth/token`: Get access token
- `POST /auth/register`: Register a new user

### Users

- `GET /users/me`: Get current user
- `GET /users/{user_id}`: Get user by ID
- `PUT /users/{user_id}`: Update user
- `DELETE /users/{user_id}`: Delete user

## Development

### Running Tests

```bash
pytest
```

### Code Formatting

```bash
black .
```

### Linting

```bash
flake8
```

## License

MIT
