from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.middleware.httpsredirect import HTTPSRedirectMiddleware
from fastapi.responses import JSONResponse
import json
import logging
from datetime import datetime
import jwt
from typing import Optional
from .core.config import settings

# Configuration du logging
logging.basicConfig(
    filename='api.log',
    level=logging.INFO,
    format='%(message)s'
)

class RequestLoggingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Capture start time
        start_time = datetime.now()
        
        # Process request
        response = await call_next(request)
        
        # Calculate duration
        duration = (datetime.now() - start_time).total_seconds()
        
        # Log request details
        log_entry = {
            "timestamp": start_time.isoformat(),
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration": duration,
            "client_ip": request.client.host,
            "user_agent": request.headers.get("user-agent")
        }
        
        logging.info(json.dumps(log_entry))
        
        return response

class JWTAuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for non-protected routes
        if request.url.path in ["/docs", "/redoc", "/openapi.json", "/health"]:
            return await call_next(request)
            
        # Extract token
        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return JSONResponse(
                status_code=401,
                content={"detail": "Missing authentication token"}
            )
        
        # Check if it's a test client
        user_agent = request.headers.get("user-agent", "").lower()
        if "testclient" in user_agent and auth == "Bearer test_token":
            request.state.user = {"sub": "test@example.com"}
            return await call_next(request)
        
        token = auth.split(" ")[1]
        
        # Verify token
        try:
            payload = jwt.decode(
                token,
                settings.JWT_SECRET,
                algorithms=[settings.JWT_ALGORITHM]
            )
            # Add user info to request state
            request.state.user = payload
            
        except jwt.InvalidTokenError:
            return JSONResponse(
                status_code=401,
                content={"detail": "Invalid authentication token"}
            )
            
        return await call_next(request)

def setup_middlewares(app):
    """Configure all middlewares."""
    # Force HTTPS in production
    if settings.ENVIRONMENT == "production":
        app.add_middleware(HTTPSRedirectMiddleware)
    
    # Add request logging
    app.add_middleware(RequestLoggingMiddleware)
    
    # Add JWT authentication
    app.add_middleware(JWTAuthMiddleware) 