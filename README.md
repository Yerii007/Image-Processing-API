# Image Processing API

A Flask-based backend API for user-authenticated image uploads and
processing. This API allows users to register/login, upload images, and
retrieve processed results (grayscale + resize). It also uses Celery
workers with Redis to handle background tasks and cleanup of old files.

## Features

-   User registration and login with JWT authentication
-   Upload images (PNG, JPG, JPEG, GIF)
-   Image processing pipeline: converts to grayscale and resizes to
    800x600
-   Background processing with Celery and Redis (optional synchronous
    mode for development)
-   Automatic cleanup of old image files
-   Health check endpoint

## Tech Stack

-   Python 3.11
-   Flask + Flask-JWT-Extended
-   SQLAlchemy (DeclarativeBase)
-   Marshmallow for validation
-   Pillow (PIL) for image processing
-   Celery + Redis for asynchronous tasks
-   Pytest for testing

## Setup Instructions

1.  **Clone the repository**

``` bash
git clone <your-repo-url>.git
cd ImageProcessingAPI
```

2.  **Create a virtual environment and install dependencies**

``` bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
```

3.  **Set environment variables** (or create a `.env` file)

``` bash
export SECRET_KEY="your-secret-key"
export JWT_SECRET_KEY="your-jwt-secret-key"
export DATABASE_URL="sqlite:///image_processor.db"
export CELERY_BROKER_URL="redis://localhost:6379/0"
export CELERY_RESULT_BACKEND="redis://localhost:6379/0"
```

4.  **Run the Flask app**

``` bash
python app.py
```

The app will run on `http://127.0.0.1:5000`.

5.  **Run Celery worker (optional)**

``` bash
celery -A celery_app.celery worker --loglevel=info
```

6.  **Run tests locally**

``` bash
pytest -q
```

## API Endpoints

### Health Check

`GET /health`\
Returns status of the API and DB connection.

### Auth

-   `POST /api/register` -- Register new user\
    JSON: `{ "name": "username", "password": "password" }`

-   `POST /api/login` -- Login user\
    JSON: `{ "name": "username", "password": "password" }`

Both return JWT access token.

### Images

-   `POST /api/upload` (auth required) -- Upload and process an image
    (multipart/form-data)
-   `GET /api/images` (auth required) -- List user's images
-   `GET /api/images/<image_id>` (auth required) -- Get status of an
    image
-   `GET /api/images/<image_id>/result` (auth required) -- Download
    processed image

## Running with Docker

This repository can be containerized. Example `Dockerfile` and
`.dockerignore` can be added. Build the image:

``` bash
docker build -t image-processing-api .
docker run -p 5000:5000 image-processing-api
```

To run Celery and Redis together, use `docker-compose.yml`
(recommended).

## Testing

Pytest tests are included in the `tests/` folder. Run locally before
building your image:

``` bash
pytest -q
```

Tests include:

-   User registration/login
-   Image upload and status retrieval
-   Model serialization
-   Utility methods

## License

MIT License (or your chosen license)
