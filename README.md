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

All endpoints under this section require admin privileges, except for the `GET` endpoints.

---

### `POST /categories/`

Create a new category. (Admin only)

**Request Body:**

```json
{
  "name": "Electronics",
  "slug": "electronics",
  "description": "All kinds of electronic gadgets.",
  "parent_id": null
}
```

**Responses:**

-   **200 OK:** Category created successfully.

    ```json
    {
      "name": "Electronics",
      "slug": "electronics",
      "description": "All kinds of electronic gadgets.",
      "parent_id": null,
      "id": 1,
      "created_at": "2023-10-27T10:00:00Z",
      "updated_at": "2023-10-27T10:00:00Z"
    }
    ```

-   **403 Forbidden:** If the user is not an administrator.

---

### `GET /categories/allcategories`

Get all categories.

**Response:**

-   **200 OK:** A list of categories.

    ```json
    [
      {
        "name": "Electronics",
        "slug": "electronics",
        "description": "All kinds of electronic gadgets.",
        "parent_id": null,
        "id": 1,
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T10:00:00Z"
      }
    ]
    ```

---

### `GET /categories/{category_id}`

Get a specific category by ID.

**Response:**

-   **200 OK:** The requested category.
-   **404 Not Found:** If the category does not exist.

    ```json
    {
      "name": "Electronics",
      "slug": "electronics",
      "description": "All kinds of electronic gadgets.",
      "parent_id": null,
      "id": 1,
      "created_at": "2023-10-27T10:00:00Z",
      "updated_at": "2023-10-27T10:00:00Z"
    }
    ```

---

### `PUT /categories/{category_id}`

Update a category. (Admin only)

**Request Body:**

```json
{
  "name": "Digital Electronics",
  "description": "All kinds of digital electronic gadgets."
}
```

**Responses:**

-   **200 OK:** The updated category.
-   **403 Forbidden:** If the user is not an administrator.
-   **404 Not Found:** If the category does not exist.

---

### `DELETE /categories/{category_id}`

Delete a category. (Admin only)

**Responses:**

-   **204 No Content:** The category was deleted successfully.
-   **403 Forbidden:** If the user is not an administrator.
-   **404 Not Found:** If the category does not exist.

### Chats

Endpoints for handling real-time chat between users.

---

### `POST /chats/last_conversation`

Get a summary of the last conversations for a user.

**Request Body:**

```json
{
  "id": "user_id"
}
```

**Response:**

-   **200 OK:** A list of conversation summaries.

    ```json
    [
      {
        "sender_id": "sender_user_id",
        "name": "John Doe",
        "img": "url_to_user_image.jpg",
        "time": "10:30 AM",
        "message": "Hello there!"
      }
    ]
    ```

---

### `POST /chats/get_conversation`

Get the message history for a specific conversation between two users.

**Request Body:**

```json
{
  "id": "current_user_id",
  "target_id": "other_user_id"
}
```

**Response:**

-   **200 OK:** The conversation history.

    ```json
    {
      "status": "success",
      "messages": [
        {
          "sender": "other_user_id",
          "msg_content": "Hi!",
          "msg_type": "text",
          "sent_at": "2023-10-27T10:00:00Z"
        },
        {
          "sender": "current_user_id",
          "msg_content": "Hello! How are you?",
          "msg_type": "text",
          "sent_at": "2023-10-27T10:01:00Z"
        }
      ]
    }
    ```

---

### `POST /chats/send_message`

Send a message to another user.

**Request Body:**

```json
{
  "from": "sender_user_id",
  "to": "receiver_user_id",
  "type": "text",
  "content": "This is a test message."
}
```

**Response:**

-   **200 OK:** Indicates the message was sent successfully.

    ```json
    {
      "status": "success"
    }
    ```

### Location

Endpoints for managing user locations. All endpoints require authentication.

---

### `POST /get_user_locations`

Get all locations for the current user.

**Response:**

-   **200 OK:** A list of the user's locations.

    ```json
    [
      {
        "id": 1,
        "user_id": 123,
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
        "is_default": true,
        "title": "Home",
        "address": "123 Main St, Anytown, CA 12345",
        "coordinates": [34.0522, -118.2437]
      }
    ]
    ```

---

### `POST /add_user_location`

Add a new location for the current user.

**Request Body:**

```json
{
  "location": {
    "full_name": "Work",
    "phone_number": "+0987654321",
    "street": "456 Business Ave",
    "city": "Businesstown",
    "state": "BS",
    "country": "USA",
    "postal_code": "54321",
    "latitude": 34.0523,
    "longitude": -118.2438,
    "is_default": false,
    "title": "Work Office",
    "address": "456 Business Ave, Businesstown, BS 54321",
    "coordinates": [34.0523, -118.2438]
  }
}
```

**Response:**

-   **200 OK:** Indicates the location was added successfully.

    ```json
    {
      "status": "success",
      "message": "Location added successfully."
    }
    ```

---

### `POST /delete_user_location`

Delete a user's location.

**Request Body:**

```json
{
  "location": {
    "id": 1
  }
}
```

**Response:**

-   **200 OK:** Indicates the location was deleted successfully.

    ```json
    {
      "status": "success",
      "message": "Location deleted successfully."
    }
    ```
-   **404 Not Found:** If the location does not exist or does not belong to the user.

### Orders

Endpoints for managing orders. All endpoints require authentication.

---

### `POST /get_orders`

Get all orders for the current user.

**Response:**

-   **200 OK:** A list of the user's orders.

    ```json
    [
      {
        "id": "order_uuid",
        "created_at": "2023-10-27T10:00:00Z",
        "delivered": false,
        "ready": true,
        "host": {
          "username": "store_owner_username",
          "profile_pic": "url_to_profile_pic.jpg",
          "verification": "gold"
        },
        "products": [
          {
            "title": "Product Name",
            "thumbnail": "url_to_product_thumbnail.jpg",
            "amount": 1,
            "attributes": {}
          }
        ]
      }
    ]
    ```

---

### `POST /checkout_data`

Get checkout data, including the total price and shipping distances.

**Request Body:**

```json
{
  "data": [
    {
      "product_id": "1",
      "quantity": 2
    }
  ],
  "location_index": 0
}
```

**Response:**

-   **200 OK:** Checkout data.

    ```json
    {
      "total": 50.00,
      "distances": [0.0, 1.0, 2.0]
    }
    ```

---

### `POST /checkout_confirm`

Confirm a checkout and get an order reference and token.

**Request Body:**

```json
{
  "data": [
    {
      "product_id": "1",
      "quantity": 2
    }
  ],
  "phone": "+1234567890",
  "location_index": 0
}
```

**Response:**

-   **200 OK:** Order reference and token.

    ```json
    {
      "status": "success",
      "order": "order_reference_uuid",
      "token": "checkout_token_uuid"
    }
    ```

---

### `POST /place_order`

Place an order using the reference and token from checkout confirmation.

**Request Body:**

```json
{
  "order_ref": "order_reference_uuid",
  "token": "checkout_token_uuid",
  "cart": [
    {
      "product_id": "1",
      "quantity": 2
    }
  ],
  "location_index": 0
}
```

**Response:**

-   **200 OK:** Indicates the order was placed successfully.

    ```json
    {
      "status": "success",
      "message": "Order(s) placed successfully"
    }
    ```

### Products

Endpoints for managing products.

---

### `POST /products/get_products`

Get a list of products with optional filters.

**Request Body:**

```json
{
  "store_id": 1,
  "category_id": 2,
  "min_price": 10.00,
  "max_price": 100.00,
  "search": "laptop",
  "skip": 0,
  "limit": 20
}
```

**Response:**

-   **200 OK:** A list of products matching the filters.

    ```json
    [
      {
        "id": 1,
        "title": "Laptop",
        "price": 999.99,
        "discount_price": 899.99,
        "stock": 50,
        "unit_type": "Item",
        "description": "A powerful laptop.",
        "category_id": 2,
        "host_id": 1,
        "images": ["url_to_image.jpg"],
        "host": {
          "id": 1,
          "username": "vendor_username",
          "profile_pic": "url_to_profile_pic.jpg",
          "verification": "verified",
          "address": "Store Name"
        },
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T10:00:00Z",
        "average_rating": 4.5
      }
    ]
    ```

---

### `GET /products/{product_id}`

Get a single product by ID.

**Response:**

-   **200 OK:** The requested product.
-   **404 Not Found:** If the product does not exist.

    ```json
    {
      "id": 1,
      "title": "Laptop",
      "price": 999.99,
      "discount_price": 899.99,
      "stock": 50,
      "unit_type": "Item",
      "description": "A powerful laptop.",
      "category_id": 2,
      "host_id": 1,
      "images": ["url_to_image.jpg"],
      "host": {
        "id": 1,
        "username": "vendor_username",
        "profile_pic": "url_to_profile_pic.jpg",
        "verification": "verified",
        "address": "Store Name"
      },
      "created_at": "2023-10-27T10:00:00Z",
      "updated_at": "2023-10-27T10:00:00Z",
      "average_rating": 4.5
    }
    ```

---

### `POST /products/`

Create a new product. (Vendor only)

**Request Body:**

```json
{
  "store_id": 1,
  "category_id": 2,
  "name": "New Gadget",
  "slug": "new-gadget",
  "description": "The latest and greatest gadget.",
  "price": 199.99,
  "discount_price": 179.99,
  "stock": 100,
  "is_active": true
}
```

**Response:**

-   **200 OK:** The newly created product.
-   **403 Forbidden:** If the user is not a vendor or does not own the store.

---

### `PUT /products/{product_id}`

Update a product. (Vendor only)

**Request Body:**

```json
{
  "name": "Updated Gadget",
  "price": 189.99
}
```

**Response:**

-   **200 OK:** The updated product.
-   **403 Forbidden:** If the user is not a vendor or does not own the product's store.
-   **404 Not Found:** If the product does not exist.

---

### `DELETE /products/{product_id}`

Deactivate (soft delete) a product. (Vendor only)

**Response:**

-   **200 OK:** Confirmation message.
-   **403 Forbidden:** If the user is not a vendor or does not own the product's store.
-   **404 Not Found:** If the product does not exist.

    ```json
    {
      "detail": "Product 1 deactivated successfully"
    }
    ```

### Product Images

Endpoints for managing product images.

---

### `POST /products/{product_id}/images`

Add one or more images to a product. (Vendor only)

**Request Body:**

-   This endpoint accepts `multipart/form-data`.
-   The `files` field should contain one or more image files.

**Response:**

-   **200 OK:** A list of the newly created product images.
-   **403 Forbidden:** If the user is not a vendor or does not own the product's store.
-   **404 Not Found:** If the product does not exist.

    ```json
    [
      {
        "image_url": "uuid_filename.jpg",
        "is_main": false,
        "id": 1,
        "product_id": 1
      }
    ]
    ```

---

### `GET /products/{product_id}/images`

Get all images for a product.

**Response:**

-   **200 OK:** A list of images for the specified product.

    ```json
    [
      {
        "image_url": "uuid_filename.jpg",
        "is_main": true,
        "id": 1,
        "product_id": 1
      },
      {
        "image_url": "another_uuid_filename.jpg",
        "is_main": false,
        "id": 2,
        "product_id": 1
      }
    ]
    ```

---

### `DELETE /images/{image_id}`

Delete a product image. (Vendor only)

**Response:**

-   **204 No Content:** The image was deleted successfully.
-   **403 Forbidden:** If the user is not a vendor or does not own the product's store.
-   **404 Not Found:** If the image does not exist.

---

### `POST /images/{image_id}/set-main`

Set a product image as the main image. (Vendor only)

**Response:**

-   **200 OK:** The updated image information.
-   **403 Forbidden:** If the user is not a vendor or does not own the product's store.
-   **404 Not Found:** If the image does not exist.

    ```json
    {
      "image_url": "uuid_filename.jpg",
      "is_main": true,
      "id": 1,
      "product_id": 1
    }
    ```

### Reviews

Endpoints for managing product reviews.

---

### `POST /products/{product_id}/reviews`

Create a new review for a product. Requires authentication.

**Request Body:**

```json
{
  "rating": 5,
  "comment": "This product is amazing!",
  "product_id": 1
}
```

**Response:**

-   **200 OK:** The newly created review.
-   **400 Bad Request:** If the user has already reviewed the product.
-   **404 Not Found:** If the product does not exist.

    ```json
    {
      "rating": 5,
      "comment": "This product is amazing!",
      "id": 1,
      "user_id": 1,
      "product_id": 1,
      "created_at": "2023-10-27T10:00:00Z"
    }
    ```

---

### `GET /products/{product_id}/reviews`

Get all reviews for a product.

**Response:**

-   **200 OK:** A list of reviews for the specified product.

    ```json
    [
      {
        "rating": 5,
        "comment": "This product is amazing!",
        "id": 1,
        "user_id": 1,
        "product_id": 1,
        "created_at": "2023-10-27T10:00:00Z"
      }
    ]
    ```

---

### `PUT /reviews/{review_id}`

Update a review. Requires authentication. Only the user who created the review can update it.

**Request Body:**

```json
{
  "rating": 4,
  "comment": "This product is great, but not perfect."
}
```

**Response:**

-   **200 OK:** The updated review.
-   **403 Forbidden:** If the user is not the owner of the review.
-   **404 Not Found:** If the review does not exist.

---

### `DELETE /reviews/{review_id}`

Delete a review. Requires authentication. Can be deleted by the user who created it or by the vendor who owns the product.

**Response:**

-   **204 No Content:** The review was deleted successfully.
-   **403 Forbidden:** If the user is not authorized to delete the review.
-   **404 Not Found:** If the review does not exist.

### Stores

Endpoints for managing stores.

---

### `POST /stores/`

Create a new store. (Vendor only)

**Request Body:**

```json
{
  "store_name": "My Awesome Store",
  "slug": "my-awesome-store",
  "description": "Selling all the awesome things.",
  "logo_url": "url_to_logo.jpg",
  "vendor_id": 1
}
```

**Response:**

-   **200 OK:** The newly created store.
-   **403 Forbidden:** If the user is not a vendor or is trying to create a store for another vendor.

    ```json
    {
      "store_name": "My Awesome Store",
      "slug": "my-awesome-store",
      "description": "Selling all the awesome things.",
      "logo_url": "url_to_logo.jpg",
      "id": 1,
      "vendor_id": 1,
      "is_verified": false,
      "rating": null,
      "created_at": "2023-10-27T10:00:00Z",
      "updated_at": "2023-10-27T10:00:00Z"
    }
    ```

---

### `GET /stores/`

List all stores.

**Response:**

-   **200 OK:** A list of all stores.

    ```json
    [
      {
        "store_name": "My Awesome Store",
        "slug": "my-awesome-store",
        "description": "Selling all the awesome things.",
        "logo_url": "url_to_logo.jpg",
        "id": 1,
        "vendor_id": 1,
        "is_verified": false,
        "rating": null,
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T10:00:00Z"
      }
    ]
    ```

---

### `GET /stores/me`

Get all stores for the current vendor. (Vendor only)

**Response:**

-   **200 OK:** A list of stores owned by the current vendor.
-   **403 Forbidden:** If the user is not a vendor.

---

### `GET /stores/{store_id}`

Get a specific store by ID.

**Response:**

-   **200 OK:** The requested store.
-   **404 Not Found:** If the store does not exist.

---

### `PUT /stores/{store_id}`

Update a store. (Vendor only)

**Request Body:**

```json
{
  "store_name": "My Even More Awesome Store",
  "description": "Now with more awesome!"
}
```

**Response:**

-   **200 OK:** The updated store.
-   **403 Forbidden:** If the user is not the owner of the store.
-   **404 Not Found:** If the store does not exist.

### Stories

Endpoints for managing stories.

---

### `POST /post_story`

Post a new story. Requires authentication.

**Request Body:**

```json
{
  "id": "user_id",
  "data": {
    "story_url": "url_to_story_media.jpg",
    "post_date": "2023-10-27T10:00:00Z",
    "caption": "Check out my new story!"
  }
}
```

**Response:**

-   **200 OK:** Indicates the story was posted successfully.

    ```json
    {
      "status": "success",
      "message": "Story posted"
    }
    ```

---

### `POST /get_story`

Get stories from followed users. Requires authentication.

**Request Body:**

```json
{
  "id": "current_user_id"
}
```

**Response:**

-   **200 OK:** A list of stories from followed users.

    ```json
    [
      {
        "user_id": "followed_user_id",
        "profile_pic": "url_to_profile_pic.jpg",
        "story_list": [
          {
            "story_url": "url_to_story_media.jpg",
            "post_date": "2023-10-27T10:00:00Z",
            "caption": "A story from a followed user."
          }
        ]
      }
    ]
    ```

### Uploads

Endpoint for file uploads.

---

### `POST /upload`

Upload a file. This is a general-purpose endpoint for uploading files like profile pictures, story media, etc.

**Request Body:**

-   This endpoint accepts `multipart/form-data`.
-   The `file` field should contain the file to upload.

**Response:**

-   **200 OK:** The filename of the uploaded file.

    ```json
    {
      "filename": "uuid_sanitized_filename.jpg"
    }
    ```
-   **500 Internal Server Error:** If there was an error saving the file.

### User

Endpoints for managing user profiles.

---

### `POST /update_user`

Update the current user's profile. Requires authentication.

**Request Body:**

```json
{
  "first_name": "John",
  "last_name": "Doe",
  "phone_number": "+1234567890",
  "profile_pic": "url_to_new_profile_pic.jpg"
}
```

**Response:**

-   **200 OK:** The updated user profile.

    ```json
    {
      "id": "user_id",
      "email": "user@example.com",
      "first_name": "John",
      "last_name": "Doe",
      "phone_number": "+1234567890",
      "profile_pic": "url_to_new_profile_pic.jpg",
      "is_active": true,
      "is_superuser": false,
      "is_verified": false,
      "created_at": "2023-10-27T10:00:00Z"
    }
    ```

---

### `POST /get_usernames`

Get a list of all usernames and the current user's profile. Requires authentication.

**Response:**

-   **200 OK:** A list of all usernames and the current user's profile.

    ```json
    {
      "users": [
        "user1",
        "user2",
        "user3"
      ],
      "current_user": {
        "id": "user_id",
        "email": "user@example.com",
        "first_name": "John",
        "last_name": "Doe",
        "phone_number": "+1234567890",
        "profile_pic": "url_to_profile_pic.jpg"
      }
    }
    ```

### Vendors

Endpoints for managing vendor profiles.

---

### `POST /vendors/`

Create a new vendor profile. Requires authentication.

**Request Body:**

```json
{
  "business_name": "My Business",
  "business_email": "business@example.com",
  "phone_number": "+1234567890",
  "bio": "Selling the best products.",
  "user_id": 1
}
```

**Response:**

-   **200 OK:** The newly created vendor profile.
-   **400 Bad Request:** If the user is already a vendor.
-   **403 Forbidden:** If trying to create a vendor profile for another user.

    ```json
    {
      "business_name": "My Business",
      "business_email": "business@example.com",
      "phone_number": "+1234567890",
      "bio": "Selling the best products.",
      "id": 1,
      "user_id": 1,
      "created_at": "2023-10-27T10:00:00Z",
      "updated_at": "2023-10-27T10:00:00Z"
    }
    ```

---

### `GET /vendors/`

List all vendors.

**Response:**

-   **200 OK:** A list of all vendors.

    ```json
    [
      {
        "business_name": "My Business",
        "business_email": "business@example.com",
        "phone_number": "+1234567890",
        "bio": "Selling the best products.",
        "id": 1,
        "user_id": 1,
        "created_at": "2023-10-27T10:00:00Z",
        "updated_at": "2023-10-27T10:00:00Z"
      }
    ]
    ```

---

### `GET /vendors/me`

Get the current user's vendor profile. Requires authentication.

**Response:**

-   **200 OK:** The current user's vendor profile.
-   **403 Forbidden:** If the user is not a vendor.
-   **404 Not Found:** If the vendor profile does not exist.

---

### `GET /vendors/{vendor_id}`

Get a specific vendor by ID.

**Response:**

-   **200 OK:** The requested vendor profile.
-   **404 Not Found:** If the vendor does not exist.

---

### `PUT /vendors/me`

Update the current user's vendor profile. Requires authentication.

**Request Body:**

```json
{
  "business_name": "My Awesome Business",
  "bio": "We sell the most awesome products."
}
```

**Response:**

-   **200 OK:** The updated vendor profile.
-   **403 Forbidden:** If the user is not a vendor.
-   **404 Not Found:** If the vendor profile does not exist.

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