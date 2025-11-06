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

2.  **Create Super Administrator**:
    ```bash
    python -m scripts.create_super_admin
    ```
    Follow the prompts to create your initial super admin user. This user will have the 'admin' role.

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

### Categories

#### `POST /categories/`

*   **Description:** Creates a new category. Requires admin authentication.
*   **Request Body:**
    ```json
    {
        "name": "Electronics",
        "slug": "electronics",
        "description": "Electronic gadgets and devices",
        "parent_id": null
    }
    ```
*   **Responses:**
    *   `200 OK`: Category successfully created. Returns `CategoryRead` object.
    *   `400 Bad Request`: Parent category not found.
    *   `403 Forbidden`: Not authorized.

#### `GET /categories/`

*   **Description:** Lists all categories.
*   **Responses:**
    *   `200 OK`: Returns a list of `CategoryRead` objects.

#### `GET /categories/{category_id}`

*   **Description:** Retrieves a single category by ID.
*   **Responses:**
    *   `200 OK`: Returns a `CategoryRead` object.
    *   `404 Not Found`: Category not found.

#### `PUT /categories/{category_id}`

*   **Description:** Updates an existing category. Requires admin authentication.
*   **Request Body:**
    ```json
    {
        "name": "Updated Electronics",
        "description": "All kinds of updated electronic gadgets"
    }
    ```
*   **Responses:**
    *   `200 OK`: Category successfully updated. Returns `CategoryRead` object.
    *   `400 Bad Request`: Parent category not found.
    *   `403 Forbidden`: Not authorized.
    *   `404 Not Found`: Category not found.

#### `DELETE /categories/{category_id}`

*   **Description:** Deletes a category. Requires admin authentication.
*   **Responses:**
    *   `204 No Content`: Category successfully deleted.
    *   `403 Forbidden`: Not authorized.
    *   `404 Not Found`: Category not found.

### Products

#### `GET /products/`

*   **Description:** Lists active products with optional filters (store_id, category_id, min_price, max_price, search).
*   **Query Parameters:** `store_id`, `category_id`, `min_price`, `max_price`, `search`, `skip`, `limit`
*   **Responses:**
    *   `200 OK`: Returns a list of `ProductRead` objects.

#### `GET /products/{product_id}`

*   **Description:** Retrieves a single product by ID.
*   **Responses:**
    *   `200 OK`: Returns a `ProductRead` object.
    *   `404 Not Found`: Product not found.

#### `POST /products/`

*   **Description:** Creates a new product. Requires vendor authentication.
*   **Request Body:**
    ```json
    {
        "store_id": 1,
        "category_id": 1,
        "name": "Smartphone X",
        "slug": "smartphone-x",
        "description": "Latest model smartphone",
        "price": 699.99,
        "discount_price": 649.99,
        "stock": 100,
        "is_active": true
    }
    ```
*   **Responses:**
    *   `200 OK`: Product successfully created. Returns `ProductRead` object.
    *   `400 Bad Request`: Category not found.
    *   `403 Forbidden`: Not authorized (user is not a vendor or cannot add to the specified store).

#### `PUT /products/{product_id}`

*   **Description:** Updates an existing product. Requires vendor authentication.
*   **Request Body:**
    ```json
    {
        "price": 679.99,
        "stock": 90
    }
    ```
*   **Responses:**
    *   `200 OK`: Product successfully updated. Returns `ProductRead` object.
    *   `403 Forbidden`: Not authorized.
    *   `404 Not Found`: Product not found.

#### `DELETE /products/{product_id}`

*   **Description:** Deactivates (soft deletes) a product. Requires vendor authentication.
*   **Responses:**
    *   `200 OK`: Product deactivated successfully.
    *   `403 Forbidden`: Not authorized.
    *   `404 Not Found`: Product not found.

### Product Images

#### `POST /products/{product_id}/images`

*   **Description:** Adds a new image to a product. Requires vendor authentication.
*   **Request Body:**
    ```json
    {
        "image_url": "http://example.com/image.jpg",
        "is_main": false
    }
    ```
*   **Responses:**
    *   `200 OK`: Image successfully added. Returns `ImageRead` object.
    *   `403 Forbidden`: Not authorized.
    *   `404 Not Found`: Product not found.

#### `GET /products/{product_id}/images`

*   **Description:** Retrieves all images for a specific product.
*   **Responses:**
    *   `200 OK`: Returns a list of `ImageRead` objects.

#### `DELETE /images/{image_id}`

*   **Description:** Deletes a product image. Requires vendor authentication.
*   **Responses:**
    *   `204 No Content`: Image successfully deleted.
    *   `403 Forbidden`: Not authorized.
    *   `404 Not Found`: Image or associated product not found.

#### `POST /images/{image_id}/set-main`

*   **Description:** Sets a product image as the main image. Requires vendor authentication.
*   **Responses:**
    *   `200 OK`: Image successfully set as main. Returns `ImageRead` object.
    *   `403 Forbidden`: Not authorized.
    *   `404 Not Found`: Image or associated product not found.

### Reviews

#### `POST /products/{product_id}/reviews`

*   **Description:** Creates a new review for a product. Requires user authentication.
*   **Request Body:**
    ```json
    {
        "rating": 5,
        "comment": "Great product, highly recommend!"
    }
    ```
*   **Responses:**
    *   `200 OK`: Review successfully created. Returns `ReviewRead` object.
    *   `400 Bad Request`: User has already reviewed this product.
    *   `404 Not Found`: Product not found.

#### `GET /products/{product_id}/reviews`

*   **Description:** Retrieves all reviews for a specific product.
*   **Query Parameters:** `skip`, `limit`
*   **Responses:**
    *   `200 OK`: Returns a list of `ReviewRead` objects.

#### `PUT /reviews/{review_id}`

*   **Description:** Updates an existing review. Requires user authentication (only the review owner).
*   **Request Body:**
    ```json
    {
        "rating": 4,
        "comment": "It's good, but could be better."
    }
    ```
*   **Responses:**
    *   `200 OK`: Review successfully updated. Returns `ReviewRead` object.
    *   `403 Forbidden`: Not authorized.
    *   `404 Not Found`: Review not found.

#### `DELETE /reviews/{review_id}`

*   **Description:** Deletes a review. Requires user authentication (owner or vendor of the product).
*   **Responses:**
    *   `204 No Content`: Review successfully deleted.
    *   `403 Forbidden`: Not authorized.
    *   `404 Not Found`: Review not found.

### Stores

#### `POST /stores/`

*   **Description:** Creates a new store. Requires vendor authentication.
*   **Request Body:**
    ```json
    {
        "vendor_id": 1,
        "store_name": "My Awesome Store",
        "slug": "my-awesome-store",
        "description": "A store selling awesome things",
        "logo_url": "http://example.com/logo.png"
    }
    ```
*   **Responses:**
    *   `200 OK`: Store successfully created. Returns `StoreRead` object.
    *   `403 Forbidden`: Not authorized (user is not a vendor or cannot create for another vendor).

#### `GET /stores/`

*   **Description:** Lists all stores.
*   **Query Parameters:** `skip`, `limit`
*   **Responses:**
    *   `200 OK`: Returns a list of `StoreRead` objects.

#### `GET /stores/me`

*   **Description:** Retrieves stores owned by the current authenticated vendor.
*   **Responses:**
    *   `200 OK`: Returns a list of `StoreRead` objects.
    *   `403 Forbidden`: User is not a vendor.

#### `GET /stores/{store_id}`

*   **Description:** Retrieves a single store by ID.
*   **Responses:**
    *   `200 OK`: Returns a `StoreRead` object.
    *   `404 Not Found`: Store not found.

#### `PUT /stores/{store_id}`

*   **Description:** Updates an existing store. Requires vendor authentication (only the store owner).
*   **Request Body:**
    ```json
    {
        "description": "An updated description for my awesome store"
    }
    ```
*   **Responses:**
    *   `200 OK`: Store successfully updated. Returns `StoreRead` object.
    *   `403 Forbidden`: Not authorized.
    *   `404 Not Found`: Store not found.

### Vendors

#### `POST /vendors/`

*   **Description:** Creates a new vendor profile for the current authenticated user.
*   **Request Body:**
    ```json
    {
        "user_id": 1,
        "business_name": "My Business Inc.",
        "business_email": "business@example.com",
        "phone_number": "+1234567890",
        "bio": "We sell quality products."
    }
    ```
*   **Responses:**
    *   `200 OK`: Vendor profile successfully created. Returns `VendorRead` object.
    *   `400 Bad Request`: User is already a vendor.
    *   `403 Forbidden`: Cannot create a vendor profile for another user.

#### `GET /vendors/`

*   **Description:** Lists all vendors.
*   **Query Parameters:** `skip`, `limit`
*   **Responses:**
    *   `200 OK`: Returns a list of `VendorRead` objects.

#### `GET /vendors/me`

*   **Description:** Retrieves the vendor profile for the current authenticated user.
*   **Responses:**
    *   `200 OK`: Returns a `VendorRead` object.
    *   `403 Forbidden`: User is not a vendor.
    *   `404 Not Found`: Vendor profile not found.

#### `GET /vendors/{vendor_id}`

*   **Description:** Retrieves a single vendor by ID.
*   **Responses:**
    *   `200 OK`: Returns a `VendorRead` object.
    *   `404 Not Found`: Vendor not found.

#### `PUT /vendors/me`

*   **Description:** Updates the vendor profile for the current authenticated user.
*   **Request Body:**
    ```json
    {
        "bio": "Updated bio for my business."
    }
    ```
*   **Responses:**
    *   `200 OK`: Vendor profile successfully updated. Returns `VendorRead` object.
    *   `403 Forbidden`: User is not a vendor.
    *   `404 Not Found`: Vendor profile not found.

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
