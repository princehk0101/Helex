from fastapi import HTTPException

class NotFoundException(HTTPException):
    def __init__(self, detail: str = "Resource not found"):
        super().__init__(status_code=404, detail={"detail": detail, "code": "NOT_FOUND"})

class ForbiddenException(HTTPException):
    def __init__(self, detail: str = "Forbidden"):
        super().__init__(status_code=403, detail={"detail": detail, "code": "FORBIDDEN"})

class UnauthorizedException(HTTPException):
    def __init__(self, detail: str = "Unauthorized"):
        super().__init__(status_code=401, detail={"detail": detail, "code": "UNAUTHORIZED"}, headers={"WWW-Authenticate": "Bearer"})

class BadRequestException(HTTPException):
    def __init__(self, detail: str = "Bad Request"):
        super().__init__(status_code=400, detail={"detail": detail, "code": "BAD_REQUEST"})
