# Africa Soko Backend

This repository contains the backend service for the Africa Soko e-commerce platform, built with Python and FastAPI.

## Features

*   **Authentication:** Secure user registration and login using JWT.
*   **Product Management:** API endpoints for creating, reading, updating, and deleting products.
*   **Order Processing:** Logic for handling customer orders.
*   **User Management:** Endpoints for managing user profiles.
*   **Database Migrations:** Using Alembic to manage database schema changes.

## Technologies Used

*   **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
*   **Database:** [PostgreSQL](https://www.postgresql.org/)
*   **ORM:** [SQLAlchemy](https://www.sqlalchemy.org/) (with `asyncpg` for async support)
*   **Data Validation:** [Pydantic](https://pydantic-docs.helpmanual.io/) (via SQLModel)
*   **Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
*   **Authentication:** [python-jose](https://python-jose.readthedocs.io/) for JWT tokens and `passlib` for password hashing.
*   **Containerization:** [Docker](https://www.docker.com/) & [Docker Compose](https://docs.docker.com/compose/)

---

## Getting Started

### Prerequisites

*   Python 3.10+
*   Docker and Docker Compose
*   An active internet connection

### 1. Clone the Repository

```bash
git clone https://github.com/AZHIK/africa-soko-backend.git
cd africa_soko_backend
```

### 2. Set Up Environment

Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate
# On Windows: venv\Scripts\activate
```

Install the required Python packages:

```bash
pip install -r requirements.txt
```

### 3. Configure Environment Variables

Create a `.env` file by copying the example file:

```bash
cp .env.example .env
```

Review and update the variables in the `.env` file, especially the `SECRET_KEY`. The default database settings are configured to work with the Docker setup below.

### 4. Start the Database

The project uses Docker to run a PostgreSQL database. Make sure Docker is running on your machine.

Start the database service in the background:

```bash
docker-compose up -d db
```

You can check the logs to ensure it started correctly:

```bash
docker-compose logs -f db
```

### 5. Run Database Migrations

Once the database is running, apply the database migrations using Alembic:

```bash
alembic upgrade head
```

---

## Running the Application

To run the FastAPI application locally, use `uvicorn`:

```bash
uvicorn app.main:app --reload --port 8000
```

The API will be available at `http://127.0.0.1:8000/docs`.

## Running Tests

To run the test suite, use `pytest`:

```bash
pytest
```

Make sure your database is configured correctly for the test environment.

## Environment Variables

The following environment variables are used to configure the application. They should be placed in a `.env` file in the project root.

| Variable                      | Description                                           | Default           |
| ----------------------------- | ----------------------------------------------------- | ----------------- |
| `APP_NAME`                    | The name of the application.                          | `Ecommerce Backend` |
| `APP_ENV`                     | The application environment (e.g., `development`).    | `development`     |
| `APP_PORT`                    | Port on which the FastAPI app will run.               | `8000`            |
| `DEBUG`                       | Toggles debug mode.                                   | `True`            |
| `SECRET_KEY`                  | A secret key for signing JWTs. **Change this!**       | `your_secret_key` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiry time for access tokens in minutes.             | `60`              |
| `POSTGRES_USER`               | Username for the PostgreSQL database.                 | `postgres`        |
| `POSTGRES_PASSWORD`           | Password for the PostgreSQL database.                 | `postgres`        |
| `POSTGRES_DB`                 | The name of the database.                             | `ecommerce`       |
| `POSTGRES_HOST`               | Hostname of the database server.                      | `localhost`       |
| `POSTGRES_PORT`               | Port for the database connection.                     | `5432`            |
