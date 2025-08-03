# config.py

class Config:
    SECRET_KEY = 'your_secret_key_here'
    SQLALCHEMY_DATABASE_URI = 'sqlite:///db/smartqueue.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Flask-Mail Configuration
    MAIL_SERVER = 'smtp.gmail.com'
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USERNAME = 'your_email@gmail.com'     # Enter your email here
    MAIL_PASSWORD = 'your_email_password'      # Enter your app password here (NOT real password)
    MAIL_DEFAULT_SENDER = 'your_email@gmail.com'
