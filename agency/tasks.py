from celery import shared_task
from django.core.mail import EmailMultiAlternatives, send_mail
from core import settings

# celery -A core worker -l INFO -P solo # -P solo - For windows
# RUN THIS ON WINDOWS - pip install eventlet
# celery -A core.celeryapp worker --loglevel=info -P eventlet

@shared_task(bind=True)
def task_func(self):
    for i in range(10):
        print(i)
    return "Done"


@shared_task(bind=True)
def send_email_func(self, mail_subject, message, to_email):
    
    # mail_subject = "ANOTHER CELERY EMAIL"
    # message = "This is another Email from Celery worker"
    # to_email = "o3cloudng@gmail.com"

    send_mail(
        subject = mail_subject,
        message = message,
        from_email= settings.EMAIL_HOST_USER,
        recipient_list = [to_email],
        fail_silently = True
    )
    return "Done"

@shared_task(bind=True)
def send_html_email(self, data):
    # subject = "CELERY HTML EMAIL"
    # print("SENDING HTML EMAIL...")
    # html_content = render_to_string("Emails/test_email.html", {
    #     "user_name":"Olumide", 
    #     "password":"Password"
    #     })
    # text_content = strip_tags(html_content)

    # data = {
    #     "html_content": html_content,
    #     "email_body": text_content,
    #     "to_email": to_email,
    #     "email_subject": mail_subject,
    # }

    message = EmailMultiAlternatives(
        data["email_subject"], # Email Subject
        data["email_body"], # Email body
        settings.DEFAULT_FROM_EMAIL, # Sender Email Address
        [data["to_email"]] # Receiver Email Address
        )
    html_content = data["html_content"]

    message.attach_alternative(html_content, "text/html")
    message.send()
    return "Done"
