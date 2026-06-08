from datetime import datetime, timezone
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_

from app.api.deps import get_db, get_current_user
from app.core.security import (
    create_access_token,
    create_refresh_token,
    hash_refresh_token,
    verify_password,
)
from app.core.config import get_settings
from app.models.user import User
from app.models.refresh_token import RefreshToken
from app.schemas.user import UserCreate, UserResponse, TokenResponse, RefreshTokenRequest
from app.services.user_service import UserService

router = APIRouter()


@router.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    user_in: UserCreate, session: AsyncSession = Depends(get_db)
) -> User:
    user_service = UserService(session)
    return await user_service.create_user(user_in)


@router.post("/login", response_model=TokenResponse)
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: AsyncSession = Depends(get_db),
) -> TokenResponse:
    user_service = UserService(session)
    user = await user_service.get_user_by_email(form_data.username)
    
    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")

    access_token = create_access_token(user.id)
    raw_refresh, hashed_refresh = create_refresh_token()
    
    # Store refresh token
    import datetime as dt
    settings = get_settings()
    expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=settings.refresh_token_expire_days)
    
    db_token = RefreshToken(
        user_id=user.id,
        token_hash=hashed_refresh,
        expires_at=expires,
        created_at=dt.datetime.now(dt.timezone.utc),
    )
    session.add(db_token)
    await session.commit()

    return TokenResponse(access_token=access_token, refresh_token=raw_refresh)


@router.post("/refresh", response_model=TokenResponse)
async def refresh_token(
    request: RefreshTokenRequest, session: AsyncSession = Depends(get_db)
) -> TokenResponse:
    hashed_token = hash_refresh_token(request.refresh_token)
    
    result = await session.execute(
        select(RefreshToken)
        .where(
            and_(
                RefreshToken.token_hash == hashed_token,
                RefreshToken.revoked_at.is_(None),
                RefreshToken.expires_at > datetime.now(timezone.utc),
            )
        )
    )
    db_token = result.scalar_one_or_none()
    
    if not db_token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired refresh token",
        )
        
    user_service = UserService(session)
    user = await user_service.get_user(db_token.user_id)
    
    if not user or not user.is_active:
        raise HTTPException(status_code=401, detail="User not active or deleted")

    # Revoke old token
    db_token.revoked_at = datetime.now(timezone.utc)
    
    # Create new tokens
    access_token = create_access_token(user.id)
    raw_refresh, new_hashed_refresh = create_refresh_token()
    
    settings = get_settings()
    import datetime as dt
    expires = dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=settings.refresh_token_expire_days)
    
    new_db_token = RefreshToken(
        user_id=user.id,
        token_hash=new_hashed_refresh,
        expires_at=expires,
        created_at=dt.datetime.now(dt.timezone.utc),
    )
    
    session.add(db_token)
    session.add(new_db_token)
    await session.commit()

    return TokenResponse(access_token=access_token, refresh_token=raw_refresh)


@router.post("/logout")
async def logout(
    request: RefreshTokenRequest,
    current_user: User = Depends(get_current_user),
    session: AsyncSession = Depends(get_db),
) -> dict:
    hashed_token = hash_refresh_token(request.refresh_token)
    result = await session.execute(
        select(RefreshToken).where(RefreshToken.token_hash == hashed_token)
    )
    db_token = result.scalar_one_or_none()
    
    if db_token and db_token.user_id == current_user.id:
        db_token.revoked_at = datetime.now(timezone.utc)
        session.add(db_token)
        await session.commit()
        
    return {"message": "Successfully logged out"}
