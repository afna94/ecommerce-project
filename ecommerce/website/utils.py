from django.core.mail import send_mail
from django.conf import settings

def send_otp_email(email, otp):
    send_mail(
        subject="Your OTP Code",
        message=f"""
        Your OTP for registration is: {otp}

        This OTP is valid for 10 minutes only.
        Do not share this OTP with anyone.
        """,
        from_email=settings.EMAIL_HOST_USER,
        recipient_list=[email]
    )