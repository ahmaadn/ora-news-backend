import datetime
import time

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Request, status
from fastapi_utils.cbv import cbv

from app.api.dependencies.user_manager import UserManager, get_user_manager
from app.schemas.reset_password import ResetPasswordRequest
from app.schemas.user import UserPasswordUpdate, UserResetPasswordUpdate, UserUpdate
from app.templates import templates
from app.utils import exceptions
from app.utils.common import ErrorCode
from app.utils.mail import EmailService
from app.utils.security import PasswordHelper
from app.utils.token import TokenManager

r = router = APIRouter(tags=["password"])


@cbv(router)
class ResetPassword:
    user_manager: UserManager = Depends(get_user_manager)

    def __init__(self):
        self.token_manager = TokenManager()
        self.password_helper = PasswordHelper()

    @r.post("/request-password-change", status_code=status.HTTP_202_ACCEPTED)
    async def request_password_change(
        self, request: Request, background_tasks: BackgroundTasks, data: ResetPasswordRequest
    ):
        try:
            user = await self.user_manager.get_by_email(data.email)
        except exceptions.UserNotExistsError:
            return

        token = self.token_manager.create_forget_password_token(user)

        print(
            f"Reset Token for user {user.id}. ",
            f"token: {token}",
        )
        # SAVE Password
        hash_new_password = self.password_helper.hash(data.new_password)
        expires_at = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(
            seconds=self.token_manager.RESET_PASSWORD_LIFETIME_SECONDS
        )

        await self.user_manager.update(
            user_update=UserResetPasswordUpdate(
                pending_password_hash=hash_new_password,
                password_change_token=token,
                password_change_token_expires_at=expires_at,
            ),
            user=user,
        )

        email_service = EmailService()
        reset_password_url = (
            f"{request.base_url}api/v1/auth/confirm-password-change?token={token}"
        )
        email_body = templates.TemplateResponse(
            name="email/reset_password.html",
            context={
                "request": request,
                "user": user,
                "reset_password_url": reset_password_url,
            },
        ).body.decode("utf-8")  # type: ignore

        background_tasks.add_task(
            email_service.send_email, "Email Reset Password", user.email, email_body
        )

    @r.get("/confirm-password-change", status_code=status.HTTP_202_ACCEPTED)
    async def reset_password(self, token: str):
        def exception_bad_request():
            return HTTPException(
                status.HTTP_400_BAD_REQUEST,
                {
                    "code": ErrorCode.INVALID_RESET_PASSOWORD_TOKEN,
                    "messages": ["Invalid or expired reset password token."],
                },
            )

        try:
            payload = self.token_manager.decode_token(
                token,
                self.token_manager.RESET_PASSWORD_SECRET_KEY,
                [self.token_manager.RESET_PASSWORD_AUDIENCE],
            )
            print(payload)

            print(time.time(), payload["exp"])

        except exceptions.InvalidVerifyTokenError as e:
            raise exception_bad_request() from e

        if (
            payload["exp"] < time.time()
            or payload["aud"] != self.token_manager.RESET_PASSWORD_AUDIENCE
        ):
            raise exception_bad_request()

        # CEK USER
        user = await self.user_manager.get_by_id(self.user_manager.parse_id(payload["sub"]))
        if not user or user.password_change_token != token:
            raise exception_bad_request()

        now = datetime.datetime.now(datetime.timezone.utc)

        if now > user.password_change_token_expires_at:
            raise exception_bad_request()

        user_update = UserPasswordUpdate(
            hashed_password=user.pending_password_hash,
            pending_password_hash=None,
            password_change_token=None,
            password_change_token_expires_at=None,
        )
        await self.user_manager.update(user_update, user)
