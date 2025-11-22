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

### 6. Seed Initial Data (Roles, Permissions, Admin User)

After migrations, seed the initial roles and permissions, and create a super administrator.

1.  **Seed Roles and Permissions**:
    ```bash
    python -m app.seeders.rbac_seeders
    ```
    This script will create default roles (admin, vendor, customer) and permissions, and link them. It's designed to run only once.

    ```bash
    python -m scripts.create_super_admin
    ```
    Follow the prompts to create your initial super admin user. This user will have the 'admin' role.

---

## Running with Docker (Full Stack)

To run the entire application (FastAPI backend + PostgreSQL database) using Docker Compose, simply run:

```bash
docker-compose up --build
```

This command will:
1.  Build the backend image.
2.  Start the PostgreSQL database container.
3.  Start the FastAPI backend container.

The API will be available at `http://localhost:8000` (or `http://127.0.0.1:8000`).
The interactive API documentation will be at `http://localhost:8000/docs`.

**Note:** The "Start the Database" section above is primarily for when you want to run the Python application locally (e.g., for debugging) but use a Dockerized database.

---

## Deployment

This project is configured for deployment on [Render](https://render.com/). The infrastructure is defined in the `render.yaml` file.

### Render Configuration

The `render.yaml` file defines:
-   **Web Service (`africa-soko-backend`):** The FastAPI application, built from the `Dockerfile`.
-   **Database (`africa-soko-db`):** A managed PostgreSQL database.

### Environment Variables on Render

When deploying to Render, the following environment variables are automatically handled or need to be configured:

-   `PORT`: Set to `8000`.
-   `DATABASE_URL`: Automatically provided by Render when linking the web service to the database.
-   `POSTGRES_...`: Database connection details are automatically injected from the linked database.
-   `SECRET_KEY`: Should be generated and set in the Render dashboard or defined to be auto-generated in `render.yaml`.
-   `GOOGLE_USER_DEFAULT_PASSWORD`: Should be generated/set for default passwords for Google OAuth users.

To deploy, simply connect your GitHub repository to Render, and it should automatically detect the `render.yaml` file (Blueprint).

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

## API Endpoints Documentation

### Addresses

All endpoints under this section require authentication.

---

### `POST /addresses/`

Create a new address for the current user.

**Request Body:**

```json
{
  "full_name": "John Doe",
  "phone_number": "+1234567890",
  "street": "123 Main St",
  "city": "Anytown",
  "state": "CA",
  "country": "USA",
  "postal_code": "12345",
  "latitude": 34.0522,
  "longitude": -118.2437,
  "is_default": true
}
```

**Responses:**

-   **201 Created:** Address created successfully.

    ```json
    {
      "id": 1,
      "user_id": 1,
      "created_at": "2023-10-27T10:00:00Z",
      "full_name": "John Doe",
      "phone_number": "+1234567890",
      "street": "123 Main St",
      "city": "Anytown",
      "state": "CA",
      "country": "USA",
      "postal_code": "12345",
      "latitude": 34.0522,
      "longitude": -118.2437,
      "is_default": true
    }
    ```

---

### `GET /addresses/`

Get all addresses for the current user.

**Response:**

-   **200 OK:** A list of addresses.

    ```json
    [
      {
        "id": 1,
        "user_id": 1,
        "created_at": "2023-10-27T10:00:00Z",
        "full_name": "John Doe",
        "phone_number": "+1234567890",
        "street": "123 Main St",
        "city": "Anytown",
        "state": "CA",
        "country": "USA",
        "postal_code": "12345",
        "latitude": 34.0522,
        "longitude": -118.2437,
        "is_default": true
      }
    ]
    ```

---

### `GET /addresses/{address_id}`

Get a specific address by ID.

**Response:**

-   **200 OK:** The requested address.
-   **404 Not Found:** If the address does not exist or does not belong to the user.

---

### `PUT /addresses/{address_id}`

Update an address.

**Request Body:**

```json
{
  "full_name": "Jane Doe",
  "is_default": false
}
```

**Responses:**

-   **200 OK:** The updated address.
-   **404 Not Found:** If the address does not exist or does not belong to the user.

---

### `DELETE /addresses/{address_id}`

Delete an address.

**Responses:**

-   **204 No Content:** The address was deleted successfully.
-   **404 Not Found:** If the address does not exist or does not belong to the user.

---

### `POST /addresses/{address_id}/set_default`

Set an address as the default.

**Responses:**

-   **200 OK:** The updated address, now set as default.
-   **404 Not Found:** If the address does not exist or does not belong to the user.

### Authentication

-   `POST /auth/signup`: Register a new user.
-   `POST /auth/login-email`: Login with email and password.
-   `POST /auth`: Authenticate with Google, or refresh token.
-   `POST /auth/refresh_token`: Refresh an access token.
-   `POST /auth/forgot-password`: Send a password reset email.
-   `POST /auth/reset-password`: Reset the user's password.

---

### `POST /auth/signup`

Registers a new user in the system.

**Request Body:**

```json
{
  "email": "user@example.com",
  "password": "a_strong_password",
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890"
}
```

**Responses:**

-   **201 Created:** User created successfully.

    ```json
    {
      "id": "user_id",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "phone_number": "+1234567890",
      "is_active": true,
      "is_superuser": false,
      "is_verified": false,
      "created_at": "2023-10-27T10:00:00Z"
    }
    ```

-   **400 Bad Request:** If the email is already registered.

    ```json
    {
      "detail": "Email already registered"
    }
    ```

---

### `POST /auth/login-email`

Authenticates a user with their email and password.

**Request Body:**

```json
{
  "username": "user@example.com",
  "password": "a_strong_password"
}
```

**Responses:**

-   **200 OK:** Authentication successful.

    ```json
    {
      "access_token": "your_access_token",
      "token_type": "bearer",
      "refresh_token": "your_refresh_token",
      "user": {
        "id": "user_id",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+1234567890"
      }
    }
    ```

-   **401 Unauthorized:** If credentials are incorrect.

    ```json
    {
      "detail": "Incorrect email or password"
    }
    ```

---

### `POST /auth`

Handles different authentication grants: Google OAuth2 and refreshing tokens.

#### 1. Google OAuth2

**Request Body:**

```json
{
  "grant_type": "google",
  "token": "google_id_token"
}
```

**Responses:**

-   **200 OK:** Authentication successful. Returns the same response as email/password login.
-   **400 Bad Request:** If the grant type is invalid or the token is missing.
-   **401 Unauthorized:** If the Google token is invalid.

#### 2. Refresh Token

**Request Body:**

```json
{
  "grant_type": "refresh_token",
  "refresh_token": "your_existing_refresh_token"
}
```

**Responses:**

-   **200 OK:** Token refreshed successfully.

    ```json
    {
      "access_token": "new_access_token",
      "token_type": "bearer"
    }
    ```

-   **401 Unauthorized:** If the refresh token is invalid or expired.

---

### `POST /auth/refresh_token`

Refreshes an access token using a refresh token.

**Request Body:**

```json
{
  "refresh_token": "your_existing_refresh_token"
}
```

**Responses:**

-   **200 OK:** Token refreshed successfully.

    ```json
    {
      "access_token": "new_access_token",
      "token_type": "bearer"
    }
    ```

-   **401 Unauthorized:** If the refresh token is invalid or expired.

---

### `POST /auth/forgot-password`

Initiates the password reset process by sending an email with a reset token.

**Request Body:**

```json
{
  "email": "user@example.com"
}
```

**Response:**

-   **200 OK:** If a user with that email exists, an email will be sent.

    ```json
    {
      "message": "Password reset email sent"
    }
    ```

---

### `POST /auth/reset-password`

Resets the user's password using a valid reset token.

**Request Body:**

```json
{
  "token": "password_reset_token",
  "new_password": "a_new_strong_password"
}
```

**Response:**

-   **200 OK:** Password reset was successful.

    ```json
    {
      "message": "Password reset successful"
    }
    ```

-   **400 Bad Request:** If the token is invalid or expired.

    ```json
    {
      "detail": "Invalid or expired token"
    }
    ```

### Categories

-   `POST /categories/`: Create a new category (admin only).
-   `GET /categories/`: List all categories.
-   `GET /categories/{category_id}`: Get a specific category by ID.
-   `PUT /categories/{category_id}`: Update a category (admin only).
-   `DELETE /categories/{category_id}`: Delete a category (admin only).

### Chats

-   `POST /chats/last_conversation`: Get a summary of the last conversations.
-   `POST /chats/get_conversation`: Get a specific conversation.
-   `POST /chats/send_message`: Send a message in a conversation.

### Location

-   `POST /get_user_locations`: Get all locations for the current user.
-   `POST /add_user_location`: Add a new location for the current user.
-   `POST /delete_user_location`: Delete a user's location.

### Orders

-   `POST /get_orders`: Get all orders for the current user.
-   `POST /checkout_data`: Get checkout data (total, distances).
-   `POST /checkout_confirm`: Confirm a checkout and get an order reference.
-   `POST /place_order`: Place an order.

### Products

-   `POST /products/get_products`: Get a list of products with filters.
-   `GET /products/{product_id}`: Get a single product by ID.
-   `POST /products/`: Create a new product (vendor only).
-   `PUT /products/{product_id}`: Update a product (vendor only).
-   `DELETE /products/{product_id}`: Deactivate (soft delete) a product (vendor only).

### Product Images

-   `POST /products/{product_id}/images`: Add images to a product (vendor only).
-   `GET /products/{product_id}/images`: Get all images for a product.
-   `DELETE /images/{image_id}`: Delete a product image (vendor only).
-   `POST /images/{image_id}/set-main`: Set a product image as the main image (vendor only).

### Reviews

-   `POST /products/{product_id}/reviews`: Create a new review for a product.
-   `GET /products/{product_id}/reviews`: Get all reviews for a product.
-   `PUT /reviews/{review_id}`: Update a review.
-   `DELETE /reviews/{review_id}`: Delete a review.

### Stores

-   `POST /stores/`: Create a new store (vendor only).
-   `GET /stores/`: List all stores.
-   `GET /stores/me`: Get all stores for the current vendor.
-   `GET /stores/{store_id}`: Get a specific store by ID.
-   `PUT /stores/{store_id}`: Update a store (vendor only).

### Stories

-   `POST /post_story`: Post a new story.
-   `POST /get_story`: Get stories from followed users.

### Uploads

-   `POST /upload`: Upload a file.

### User

-   `POST /update_user`: Update the current user's profile.
-   `POST /upload`: Upload a file (duplicate of `/upload`).
-   `POST /get_usernames`: Get a list of all usernames and the current user's profile.

### Vendors

-   `POST /vendors/`: Create a new vendor profile.
-   `GET /vendors/`: List all vendors.
-   `GET /vendors/me`: Get the current user's vendor profile.
-   `GET /vendors/{vendor_id}`: Get a specific vendor by ID.
-   `PUT /vendors/me`: Update the current user's vendor profile.
-   `DELETE /vendors/me`: Delete the current user's vendor profile.

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