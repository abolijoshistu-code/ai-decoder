import os
import smtplib
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from dotenv import load_dotenv

load_dotenv()

class EmailService:
    def __init__(self):
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.email_user = os.getenv("EMAIL_USER")
        self.email_pass = os.getenv("EMAIL_PASS")
        self.sender_display = "AI Jargon Decoder"

    def send_daily_term(self, term_data, subscribers):
        """Sends the daily decode to a list of subscribers via SMTP."""
        if not subscribers:
            logging.info("No subscribers found. Skipping email.")
            return

        # --- FIX: Ensure variable name is 'html_body' ---
        html_body = f"""
        <html>
        <head>
            <style>
                .container {{ font-family: 'Georgia', serif; color: #1a1a1a; padding: 20px; background-color: #fcfcfc; }}
                .card {{ max-width: 600px; margin: 0 auto; background: #ffffff; padding: 40px; border: 1px solid #efefef; border-radius: 12px; }}
                .label {{ text-transform: uppercase; letter-spacing: 2px; font-size: 10px; color: #64748b; margin-bottom: 10px; }}
                .analogy {{ background: #f8fafc; padding: 20px; border-left: 4px solid #1a1a1a; font-style: italic; margin: 25px 0; }}
            </style>
        </head>
        <body class="container">
            <div class="card">
                <p class="label">Daily Jargon Decode</p>
                <h1 style="font-size: 28px; margin-top: 0;">{term_data['title']}</h1>
                <p style="font-size: 16px; color: #475569;">{term_data['summary']}</p>
                
                <hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;">
                
                <p><strong>The Explanation:</strong><br>{term_data['explanation']}</p>
                
                <div class="analogy">
                    "{term_data['analogy']}"
                </div>
                
                <p><small style="color: #64748b;"><strong>Practical Example:</strong> {term_data['example']}</small></p>
                
                <footer style="margin-top: 40px; font-size: 11px; color: #94a3b8; text-align: center; border-top: 1px solid #eee; padding-top: 20px;">
                    Sent by the AI Simplified Pipeline. <br>
                    To unsubscribe, please reply to this email.
                </footer>
            </div>
        </body>
        </html>
        """

        try:
            # Create a secure connection
            logging.info(f"Connecting to SMTP server {self.smtp_server}...")
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()  # Upgrade to TLS encryption
                server.login(self.email_user, self.email_pass)
                
                for recipient in subscribers:
                    msg = MIMEMultipart("alternative")
                    msg["Subject"] = f"Daily AI Decode: {term_data['title']}"
                    msg["From"] = f"{self.sender_display} <{self.email_user}>"
                    msg["To"] = recipient
                    
                    # --- FIX: Reference the correct variable name 'html_body' ---
                    msg.attach(MIMEText(html_body, "html"))
                    
                    server.send_message(msg)
                    logging.info(f"Successfully mailed: {recipient}")
                    
            logging.info(f"SMTP Batch Complete. Total: {len(subscribers)}")
            
        except Exception as e:
            logging.error(f"SMTP Critical Failure: {str(e)}")
            # Do not raise here so the pipeline can finish its log