from fastapi import APIRouter, Depends, Response, Cookie
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.services.auth_service import AuthService
from app.schemas.auth import RegisterRequest, LoginRequest, RefreshRequest

router = APIRouter(prefix="/auth", tags=["Authentication"])


@router.post("/register")
async def register(data: RegisterRequest, db: AsyncSession = Depends(get_db)):
    service = AuthService(db)
    return await service.register(data)


@router.post("/login")
async def login(
    data: LoginRequest,
    tenant_slug: str,
    response: Response,
    db: AsyncSession = Depends(get_db),
):
    service = AuthService(db)
    result = await service.login(data, tenant_slug)

    response.set_cookie(
        key="refresh_token",
        value=result["refresh_token"],
        httponly=True,
        max_age=7 * 24 * 60 * 60,
        samesite="lax",
    )

    return {
        "access_token": result["access_token"],
        "token_type": result["token_type"],
        "user": result["user"],
    }


@router.post("/refresh")
async def refresh(
    db: AsyncSession = Depends(get_db),
    refresh_token: str | None = Cookie(default=None),
):
    if not refresh_token:
        from fastapi import HTTPException, status
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="No refresh token provided",
        )
    service = AuthService(db)
    return await service.refresh(refresh_token)


@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie("refresh_token")
    return {"message": "Logged out successfully"}