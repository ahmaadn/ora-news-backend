from fastapi import APIRouter, BackgroundTasks, Body, Depends, Request, status
from fastapi.responses import RedirectResponse
from fastapi_utils.cbv import cbv

from app.api.dependencies.user_manager import UserManager, get_user_manager
from app.core.config import get_settings
from app.schemas.user import VerifyUserUpdate
from app.templates import templates
from app.utils import exceptions
from app.utils.mail import EmailService
from app.utils.token import TokenManager

r = router = APIRouter(tags=["verification"])


@cbv(router)
class Verification:
    user_manager: UserManager = Depends(get_user_manager)

    def __init__(self):
        self.token_manager = TokenManager()

    @r.post("/request-token", status_code=status.HTTP_202_ACCEPTED)
    async def request_verify(
        self,
        background_tasks: BackgroundTasks,
        request: Request,
        email: str = Body(..., embed=True),
    ):
        try:
            user = await self.user_manager.get_by_email(email)
            token = self.token_manager.create_verification_token(user)
        except (
            exceptions.UserNotExistsError,
            exceptions.UserAlreadyVerifiedError,
            exceptions.UserInactiveError,
        ):
            # avoid error
            return

        # ON REQUEST VERIFY TOKEN
        # for debug only
        print(
            f"Verification requested for user {user.id}. ",
            f"Verification token: {token}",
        )
        email_service = EmailService()
        verification_url = (
            f"{request.base_url}api/{get_settings().API_V1_STR}/auth/verify?token={token}"
        )
        email_body = templates.TemplateResponse(
            name="email/verification_email.html",
            context={
                "request": request,
                "user": user,
                "verification_url": verification_url,
            },
        ).body.decode("utf-8")

        # TODO: Save token di DB
        background_tasks.add_task(
            email_service.send_email, "Email Verification", user.email, email_body
        )

    @r.get("/verify")
    async def verify(self, request: Request, token: str):
        try:
            payload = self.token_manager.decode_token(
                token,
                self.token_manager.VERIFICATION_SECRET_KEY,
                [self.token_manager.VERIFICATION_AUDIENCE],
            )
        except exceptions.InvalidVerifyTokenError:
            return RedirectResponse("https://example.com")

        try:
            sub = payload["sub"]
            email = payload["email"]
            user_id = self.user_manager.parse_id(sub)
        except (KeyError, exceptions.InvalidIDError):
            return RedirectResponse("https://example.com")

        try:
            user = await self.user_manager.get_by_email(email)
        except exceptions.UserNotExistsError:
            return RedirectResponse("https://example.com")

        if user_id != user.id:
            return RedirectResponse("https://example.com")

        if user.is_verified:
            return RedirectResponse("https://example.com")

        # Update verify hanya yang verifynya false
        await self.user_manager.update(VerifyUserUpdate(is_verified=True), user, safe=False)
        return RedirectResponse("https://example.com")
