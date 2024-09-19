from agency.tasks import send_html_email



def send_email_function(html_content, text_content, to_email, mail_subject):
    data = {
        "html_content": html_content,
        "email_body": text_content,
        "to_email": to_email,
        "email_subject": mail_subject,
    }
    
    send_html_email.delay_on_commit(data)