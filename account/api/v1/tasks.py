from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template

from HabbitBackend.celery import app


@app.task(name="send_reset_password_otp_to_user_email_task")
def send_reset_password_otp_to_user_email_task(
    user_email: str, token: str
) -> None:  # pragma: no cover
    template = get_template("account/api/v1/templates/resetpassword.html")

    html_content = template.render({"otp": token})

    text_content = (
        f"Use the following OTP to complete your password reset {token}. "
        "OTP is valid for 5 minutes"
    )

    subject, from_email, to = "Reset Password OTP", settings.EMAIL_HOST_USER, user_email
    msg = EmailMultiAlternatives(subject, text_content, from_email, [to])
    msg.attach_alternative(html_content, "text/html")
    msg.send()
