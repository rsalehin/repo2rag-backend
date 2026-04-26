# MyProject

## Authentication Module
The auth module uses JWT tokens for stateless authentication.
It checks the `Authorization` header on every request.
Token expiry is set to 15 minutes.

## Database Layer
We use PostgreSQL with connection pooling via `psycopg2`.
All queries go through a custom ORM defined in `src/db/models.py`.

## Configuration
Environment variables are loaded from `.env` using `python-dotenv`.
The main config file is `config/settings.py`.

## Logging
The app uses structured logging with `structlog`.
Logs are shipped to Elasticsearch in production.

## API Endpoints
- `POST /api/login` – returns JWT token
- `GET /api/users` – list users (requires admin role)
- `POST /api/data` – create a new record

## Error Handling
Global exception handler catches all unhandled exceptions.
Returns a standard JSON error with error code and message.