# This will be imported when explicitly requested
# from app.api.router import router

__all__ = ["router"]

def get_router():
    # Lazy import to avoid circular imports
    from app.api.router import router
    return router
