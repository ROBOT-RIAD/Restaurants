# import random
# from django.core.mail import send_mail
# from django.conf import settings

# def generate_otp():
#     return str(random.randint(1000, 9999))

# def send_otp(user):
#     otp_code = generate_otp()
#     # OTP.objects.create(user=user, code=otp_code)

#     send_mail(
#         subject="Your OTP Code",
#         message=f"Your OTP is {otp_code}",
#         from_email=settings.EMAIL_HOST_USER,
#         recipient_list=[user.email],
#     )

#     return otp_code
