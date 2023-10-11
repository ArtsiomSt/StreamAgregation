from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from .config import Settings

settings = Settings()

email_config = ConnectionConfig(
    MAIL_USERNAME=settings.email_host_user,
    MAIL_PASSWORD="ehebvpurfligbhnb",
    MAIL_FROM=settings.email_host_user,
    MAIL_PORT=465,
    MAIL_SERVER="smtp.yandex.ru",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
    VALIDATE_CERTS=True,
    TIMEOUT=15,
)


def get_available_params(params: dict, available_params: list[str]) -> dict:
    result = {}
    for param_key, param_value in params.items():
        if param_key in available_params and param_value is not None:
            result[param_key] = param_value
    return result


async def send_email_notification(recipients_list: list[str], body: str, subject: str = "Stream Started") -> None:
    message = MessageSchema(
        subject=subject,
        recipients=recipients_list,
        body=body,
        subtype=MessageType.plain,
    )
    fast_mail = FastMail(email_config)
    await fast_mail.send_message(message)
