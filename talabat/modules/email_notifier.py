import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from modules.config_loader import load_config

def send_failure_email(to_email, status_code):
    config = load_config()

    subject = "Token Refresh Failed"
    body = f"Failed to refresh the access token. Status code: {status_code}"
    
    message = MIMEMultipart()
    message["From"] = config["gmail_user"]
    message["To"] = to_email
    message["Subject"] = subject

    message.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(config["gmail_user"], config["gmail_password"])
        server.sendmail(config["gmail_user"], to_email, message.as_string())
        server.quit()
        print("Failure email sent successfully.")
    except Exception as e:
        print(f"Failed to send email: {e}")
