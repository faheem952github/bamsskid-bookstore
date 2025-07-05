from datetime import UTC, datetime

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session
from starlette import status
from starlette.requests import Request

from app.account.models import UserSession, User
from app.account.repository import get_user_by_id
from app.account.request import (
    UserRegisterRequest, UserLoginRequest,
    RefreshTokenRequest, ChangePasswordRequest
)

from app.account.response import (
    RegisterResponse, UserBasicResponse,
    LoginResponse, TokenResponse,
    LogoutResponse, PasswordChangeResponse,
    SuccessResponse
)
from app.account.utils.dependencies import get_current_active_user, get_current_user
from app.account.views import create_user, authenticate_user
from app.core.audit_logs import log_action
from app.core.auth import (
    create_access_token, create_refresh_token,
    decode_token, verify_password, hash_password
)
from app.core.sessions import create_user_session
from config.config import settings
from config.database import get_db
from config.logging_utils import logger

ACCESS_TOKEN_EXPIRY = settings.ACCESS_TOKEN_EXPIRE_MINUTES

auth_router = APIRouter(prefix="/auth", tags=["Authentication"])


# ================== AUTH ROUTES ==================

@auth_router.post("/register", response_model=RegisterResponse)
async def register(user_data: UserRegisterRequest, request: Request, db: Session = Depends(get_db)):
    """Register new user"""
    try:
        logger.info("User are registration.")
        user = create_user(db, user_data, request)
        return RegisterResponse(
            message="User registered successfully",
            data={
                "message": "Registration successful. Please verify your email.",
                "user": UserBasicResponse.model_validate(user)
            }
        )
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )


@auth_router.post("/login", response_model=LoginResponse)
async def login(login_data: UserLoginRequest, request: Request, db: Session = Depends(get_db)):
    """
    User login endpoint with centralized error handling.
    """
    logger.info(f"User puts credentials for Login")

    # Manual validation (optional, already handled by Pydantic)
    if not login_data.username_or_email or not login_data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username or password is missing."
        )

    try:
        # Authenticate
        user = authenticate_user(db, login_data.username_or_email, login_data.password, request)
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password."
            )

        if not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Your account is inactive or disabled."
            )

        # Device info
        device_info = {
            "device": request.headers.get("X-Device", "Unknown"),
            "platform": request.headers.get("X-Platform", "Unknown")
        }

        # Create session
        session = create_user_session(
            user_id=user.id,
            device_info=device_info,
            ip_address=request.client.host,
            user_agent=request.headers.get("User-Agent", ""),
            expires_in_minutes=60 * 24,
            db=db
        )
        # Generate tokens
        access_token = create_access_token({"sub": str(user.id)})
        refresh_token = create_refresh_token({"sub": str(user.id)})

        return LoginResponse(
            message="Login successful",
            data=TokenResponse(
                access_token=access_token,
                refresh_token=refresh_token,
                expires_in=ACCESS_TOKEN_EXPIRY * 60,
                user=UserBasicResponse.model_validate(user)
            )
        )

    except HTTPException as exc:
        raise exc  # Will be handled by middleware

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error occurred during login."
        )


@auth_router.post("/refresh", response_model=TokenResponse)
async def refresh_token(refresh_data: RefreshTokenRequest, db: Session = Depends(get_db)):
    """Refresh access token using a valid refresh token."""

    try:
        # Decode refresh token
        payload = decode_token(refresh_data.refresh_token)
        logger.info(f"User refresh his token user id is ", payload.get("sub"))
        if payload.get("type") != "refresh":
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token"
            )

        # Validate user
        user_id = payload.get("sub")
        if not user_id:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token payload"
            )

        user = get_user_by_id(db, int(user_id))

        if not user or not user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found or inactive"
            )

        # Generate new tokens
        access_token = create_access_token({"sub": str(user.id)})
        new_refresh_token = create_refresh_token({"sub": str(user.id)})

        return TokenResponse(
            access_token=access_token,
            refresh_token=new_refresh_token,
            expires_in=ACCESS_TOKEN_EXPIRY * 60,
            user=UserBasicResponse.model_validate(user)
        )

    except HTTPException as exc:
        raise exc  # handled by your centralized exception middleware

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while refreshing token"
        )


@auth_router.post("/logout", response_model=LogoutResponse)
async def logout(request: Request, current_user: User = Depends(get_current_active_user), db: Session = Depends(get_db)):
    """User logout"""

    try:
        # Get token from Authorization header
        logger.info("User are SignOuting")

        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Missing or invalid authorization token"
            )

        # Invalidate current session
        session = (
            db.query(UserSession)
            .filter(
                UserSession.user_id == current_user.id,
                UserSession.is_active == True,
            )
            .first()
        )

        if not session:
            logger.info("Session not found or already logged out")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Session not found or already logged out"
            )

        session.is_active = False
        db.commit()

        # Log action
        log_action(
            db=db,
            action="LOGOUT",
            resource="Auth",
            user_id=current_user.id,
            request=request
        )

        return LogoutResponse(message="Logged out successfully")

    except HTTPException as exc:
        raise exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Unexpected error during logout"
        )


@auth_router.post("/change-password", response_model=PasswordChangeResponse)
async def change_password(
        password_data: ChangePasswordRequest,
        request: Request,
        current_user: User = Depends(get_current_active_user),
        db: Session = Depends(get_db)
):
    """Change user password"""
    try:
        # Verify current password
        if not verify_password(password_data.current_password, current_user.hashed_password):
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Current password is incorrect"
            )

        # Update password
        current_user.hashed_password = hash_password(password_data.new_password)
        current_user.updated_at = datetime.now(UTC)

        # Invalidate all sessions
        db.query(UserSession).filter(UserSession.user_id == current_user.id).update({"is_active": False})
        db.commit()

        # Log activity
        log_action(
            db=db,
            action="CHANGE_PASSWORD",
            resource="Auth",
            user_id=current_user.id,
            details={"sessions_invalidated": True},
            request=request
        )

        return PasswordChangeResponse(message="Password changed successfully")

    except HTTPException as exc:
        raise exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while changing password"
        )


@auth_router.get("/me", response_model=SuccessResponse[UserBasicResponse])
def get_current_user_route(current_user: User = Depends(get_current_user)):
    """Get current logged-in user details"""
    try:
        if not current_user or not current_user.is_active:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid or inactive user"
            )

        user_response = UserBasicResponse.model_validate(current_user)

        return SuccessResponse(
            message="Current user fetched successfully",
            data=user_response
        )

    except HTTPException as exc:
        raise exc

    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Something went wrong while fetching user"
        )
