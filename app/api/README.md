# API Architecture

This project follows a clean architecture approach with a modular structure for better maintainability and separation of concerns.

## Structure Overview

```
app/
  api/
    __init__.py           # Exports the main router
    router.py             # Top-level router that includes all specific routers
    controllers/
      __init__.py         # Imports and exports controllers
      user_controller.py  # User controller with user_router
      news_controller.py  # News controller with news_router
      portfolio_controller.py # Portfolio controller with portfolio_router
      prediction_controller.py # Prediction controller with prediction_router
    schemas/
      # Pydantic models for request/response validation
```

## Architecture Design

### Top-Level Router (`router.py`)
- Centralizes all routing in a single location
- Imports and includes each feature-specific router
- Simplifies the main application setup

### Feature Controllers
Each controller file:
1. Defines a feature-specific router (e.g., `user_router`)
2. Contains a controller class with business logic methods
3. Defines endpoints that use the controller methods
4. Handles error cases and response formatting

### Main Application (`main.py`)
- Only needs to include the main router
- Clean and minimal setup

## Adding New Features

To add a new feature:
1. Create a new controller file in `app/api/controllers/`
2. Define a router and controller class
3. Add necessary schemas in `app/api/schemas/`
4. Import and include the router in `app/api/router.py`

This architecture provides:
- **Clean separation of concerns**
- **Modularity and maintainability**
- **Easy testing** of individual components
- **Simplified routing** management