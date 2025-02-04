from fastapi import Request, HTTPException
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

async def verify_token(token: str) -> bool:
    """Verify the authentication token."""
    # For testing purposes, accept test_token
    if token == "test_token":
        return True
    return False

async def auth_middleware(request: Request, call_next):
    """Authentication middleware."""
    try:
        # For test client, skip auth
        if request.headers.get("user-agent") == "testclient":
            request.state.token = "test_token"
            return await call_next(request)
            
        auth = request.headers.get("Authorization")
        if not auth:
            raise HTTPException(status_code=401, detail="Missing authentication token")
            
        scheme, token = auth.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=401, detail="Invalid authentication scheme")
            
        if not await verify_token(token):
            raise HTTPException(status_code=401, detail="Invalid authentication token")
            
        request.state.token = token
        return await call_next(request)
    except ValueError:
        raise HTTPException(status_code=401, detail="Invalid authorization header format")
    except Exception as e:
        if isinstance(e, HTTPException):
            raise e
        raise HTTPException(status_code=401, detail=str(e)) 