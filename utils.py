import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_email(sender_email, sender_password, recipient_email, subject, body, smtp_server, smtp_port=587):
    """
    Send an email using SMTP.

    Parameters:
        sender_email (str): Sender's email address.
        sender_password (str): Sender's email password.
        recipient_email (str): Recipient's email address.
        subject (str): Email subject.
        body (str): Email body.
        smtp_server (str): SMTP server address.
        smtp_port (int): SMTP server port (default is 587).

    Returns:
        bool: True if email was sent successfully, False otherwise.
    """
    try:
        # Create message container
        msg = MIMEMultipart()
        msg['From'] = sender_email
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach body
        msg.attach(MIMEText(body, 'plain'))

        # Start the SMTP session
        server = smtplib.SMTP(smtp_server, smtp_port)
        server.starttls()  # Start TLS encryption
        server.login(sender_email, sender_password)

        # Send the email
        text = msg.as_string()
        server.sendmail(sender_email, recipient_email, text)
        print('Email sent successfully!')
        return True

    except Exception as e:
        print(f'Error: {e}')
        return False

    finally:
        server.quit()  # Close the SMTP session
        

# Email credentials
sender_email = 'v-maria77@hotmail.com'
sender_password = 'Phong24052001'

# Recipient email address
recipient_email = 'homnaylatest11@gmail.com'

# Email details
subject = 'Mã thay đổi mật khẩu EduSmart'
body = 'Mã của bạn là 93888475.'

# SMTP server configuration
smtp_server = 'smtp-mail.outlook.com'
smtp_port = 587  # Change this if your SMTP server uses a different port

# Send email
send_email(sender_email, sender_password, recipient_email, subject, body, smtp_server, smtp_port)