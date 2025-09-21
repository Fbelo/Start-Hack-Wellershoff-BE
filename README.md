# Start-Hack-Wellershoff-&-Partners-BE

Backend API for the Wellershoff & Partners application built with FastAPI.

## Features

- FastAPI-based RESTful API
- PostgreSQL database integration with SQLAlchemy ORM
- API key authentication for frontend security
- News scraping capabilities
- WatsonX AI integration
- Portfolio and report management
- User authentication and management

## Prerequisites

- Python 3.10+
- PostgreSQL database
- WatsonX API credentials (optional)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/Fbelo/Start-Hack-Wellershoff-BE.git
   cd Start-Hack-Wellershoff-BE
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the root directory with the following variables:
   ```
   # Database Connection
   POSTGRES_URL="your-postgres-connection-string"
   
   # Watson (optional)
   WATSON_ENDPOINT="your-watson-endpoint"
   WATSON_API_KEY="your-watson-api-key"
   
   # API Security
   FRONTEND_API_KEY="your-frontend-api-key"
   ```

   You can generate a secure API key with:
   ```bash
   python3 -c "import secrets; print(secrets.token_urlsafe(32))"
   ```

## Running the Application

To run the application in development mode:

```bash
uvicorn main:app --reload
```

Or use the `fastapi` command if you have it installed:

```bash
fastapi dev
```

The API will be accessible at http://localhost:8000.

## API Documentation

Once the server is running, you can access the auto-generated API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API Key Authentication

All API endpoints are protected by an API key authentication system. Frontend applications must include this key in the `X-API-Key` header with each request:

```javascript
// Example using fetch API
fetch('https://your-api-url/endpoint', {
  method: 'GET',
  headers: {
    'X-API-Key': 'your-frontend-api-key',
    'Content-Type': 'application/json'
  }
})
```

The API key is defined in the `.env` file and should be securely transferred to the frontend application. For detailed information on implementing this in the frontend, see [API Key Documentation](/app/api/README_API_KEY.md).

## Project Structure

```
.
├── app/
│   ├── api/              # API endpoints
│   │   ├── controllers/  # Route handlers
│   │   ├── schemas/      # Pydantic models
│   │   └── router.py     # API router
│   ├── common/           # Shared utilities
│   │   ├── enums.py      # Enum definitions
│   │   └── security.py   # API security middleware
│   ├── db/               # Database models and connection
│   │   ├── database.py   # Database setup
│   │   └── models.py     # SQLAlchemy models
│   ├── scrapers/         # News scraping functionality
│   │   ├── scripts/      # Scraper scripts
│   │   └── scheduler.py  # Scraper scheduling
│   └── watsonx/          # WatsonX AI integration
├── main.py               # Application entry point
├── requirements.txt      # Python dependencies
└── .env                  # Environment variables
```

## License

[MIT License](LICENSE)