"""
Default settings for entire application
"""
import datetime

DEBUG = True
SECRET_KEY = 'super-secret-key'
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=365)

# Set up errors to be emailed
ERROR_SMTP_ENABLED = False
ERROR_SMTP_HOST = '127.0.0.1'
ERROR_SMTP_USER = 'admin'
ERROR_SMTP_PASS = 'hunter2'
ERROR_SMTP_FROM = 'app@ig_review.foo'
ERROR_SMTP_TO = ['admin@example.com']
ERROR_SMTP_SUBJECT = 'ig_review error'
ERROR_SMTP_SECURE = ()

# STORAGE_ROOT specifies an absolute root dir.
# If it's None, we'll use the flask instance directory.
# Relative paths for below settings will be relative to ROOT_DIR.
STORAGE_ROOT = None

# If below paths are relative, they will be relative to STORAGE_ROOT
# Where to store images that are in review
IMAGES_REVIEW_DIR = 'images/review'
# Where to store images that should be mailed
IMAGES_SEND_DIR = 'images/send'
# Flat file for user login
USER_STORAGE_FILE = 'users.ini'

CELERY_BROKER_URL = 'amqp://guest@localhost'
CELERY_BACKEND_URL = 'rpc://'

# How often to scrape in minutes
SCRAPE_IG_INTERVAL = 60

### Below isn't used

MAIL_DEFAULT_SENDER = 'info@overholt.com'
MAIL_SERVER = 'smtp.postmarkapp.com'
MAIL_PORT = 25
MAIL_USE_TLS = True
MAIL_USERNAME = 'username'
MAIL_PASSWORD = 'password'

SECURITY_POST_LOGIN_VIEW = '/'
SECURITY_PASSWORD_HASH = 'plaintext'
SECURITY_PASSWORD_SALT = 'password_salt'
SECURITY_REMEMBER_SALT = 'remember_salt'
SECURITY_RESET_SALT = 'reset_salt'
SECURITY_RESET_WITHIN = '5 days'
SECURITY_CONFIRM_WITHIN = '5 days'
SECURITY_SEND_REGISTER_EMAIL = False