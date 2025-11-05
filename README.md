# Africa Soko Backend

This repository contains the backend service for the Africa Soko e-commerce platform, built with Python and FastAPI.

## Features

*   **Authentication:** Secure user registration and login using JWT, including Google OAuth.
*   **Database Migrations:** Using Alembic to manage database schema changes.

## Technologies Used

*   **Framework:** [FastAPI](https://fastapi.tiangolo.com/)
*   **Database:** [PostgreSQL](https://www.postgresql.org/)
*   **ORM/Data Validation:** [SQLModel](https://sqlmodel.tiangolo.com/) (built on SQLAlchemy and Pydantic, with `asyncpg` for async support)
*   **Migrations:** [Alembic](https://alembic.sqlalchemy.org/)
*   **Authentication:** [python-jose](https://python-jose.readthedocs.io/) for JWT tokens, `passlib` for password hashing, and [httpx](https://www.python-httpx.org/) for Google OAuth.
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

## API Endpoints

### Authentication

#### `POST /auth/signup`

*   **Description:** Registers a new user.
*   **Request Body:**
    ```json
    {
        "email": "user@example.com",
        "username": "newuser",
        "password": "securepassword",
        "is_admin": false
    }
    ```
*   **Responses:**
    *   `200 OK`: User successfully registered. Returns `UserRead` object.
    *   `400 Bad Request`: Email already registered.
    *   `403 Forbidden`: Cannot create an admin user directly via this endpoint.

#### `POST /auth/admin-create`

*   **Description:** Creates a new admin user. Requires an existing admin's authentication token.
*   **Request Body:**
    ```json
    {
        "email": "admin@example.com",
        "username": "newadmin",
        "password": "securepassword",
        "is_admin": true
    }
    ```
*   **Headers:**
    *   `Authorization: Bearer <admin_access_token>`
*   **Responses:**
    *   `200 OK`: Admin user successfully created. Returns `UserRead` object.
    *   `400 Bad Request`: Email already registered.
    *   `403 Forbidden`: Not authorized (if the token is not from an admin user).

#### `POST /auth/login`

*   **Description:** Authenticates a user and returns an access token.
*   **Request Body:**
    ```json
    {
        "email": "user@example.com",
        "password": "securepassword"
    }
    ```
*   **Responses:**
    *   `200 OK`: Authentication successful. Returns `Token` object.
    *   `400 Bad Request`: Invalid credentials.

#### `POST /auth/login/google`

*   **Description:** Authenticates a user using Google OAuth token. If the user does not exist, a new user account is created.
*   **Request Body:**
    ```json
    {
        "token": "google_id_token_string"
    }
    ```
*   **Responses:**
    *   `200 OK`: Authentication successful. Returns `Token` object.
    *   `400 Bad Request`: Invalid Google token.

## Environment Variables

The following environment variables are used to configure the application. They should be placed in a `.env` file in the project root.

| Variable                      | Description                                           |
| ----------------------------- | ----------------------------------------------------- |
| `APP_NAME`                    | The name of the application.                          |
| `APP_ENV`                     | The application environment (e.g., `development`).    |
| `APP_PORT`                    | Port on which the FastAPI app will run.               |
| `DEBUG`                       | Toggles debug mode.                                   |
| `SECRET_KEY`                  | A secret key for signing JWTs. **Change this!**       |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Expiry time for access tokens in minutes.             |
| `POSTGRES_USER`               | Username for the PostgreSQL database.                 |
| `POSTGRES_PASSWORD`           | Password for the PostgreSQL database.                 |
| `POSTGRES_DB`                 | The name of the database.                             |
| `POSTGRES_HOST`               | Hostname of the database server.                      |
| `POSTGRES_PORT`               | Port for the database connection.                     |
| `DATABASE_URL`                | Full database connection URL.                         |
| `GOOGLE_USER_DEFAULT_PASSWORD`| Default password for Google OAuth users.              |
