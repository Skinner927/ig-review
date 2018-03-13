"""
Default settings for entire application
"""
import datetime

DEBUG = True
# python -c 'import os; print(os.urandom(24))'
SECRET_KEY = 'super-secret-key'
PERMANENT_SESSION_LIFETIME = datetime.timedelta(days=365)

# Set up errors to be emailed
# Uses logging.handlers.SMTPHandler
ERROR_SMTP_ENABLED = False
ERROR_SMTP_HOST = '127.0.0.1'
ERROR_SMTP_PORT = 587
ERROR_SMTP_USER = 'admin'
ERROR_SMTP_PASS = 'hunter2'
ERROR_SMTP_FROM = 'app@ig_review.foo'
ERROR_SMTP_TO = ['admin@example.com']
ERROR_SMTP_SUBJECT = 'ig_review error'
ERROR_SMTP_SECURE = ()  # See logging.handlers.SMTPHandler

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
LOCKFILE_DIR = 'locks'

CELERY_BROKER_URL = 'amqp://guest:guest@localhost'
CELERY_BACKEND_URL = 'rpc://'

# How often to scrape IG in minutes
SCRAPE_IG_INTERVAL = 60
# How often to send approved images
SEND_IG_APPROVED = 10
# How to login to IG
SCRAPE_IG_USER = 'foobar'
SCRAPE_IG_PASS = 'hunter2'
SCRAPE_IG_FRIENDS = ['joebob22', 'stacy88']
SCRAPE_IG_MAX_PER_FRIEND = 10  # Max number of images to pull per friend
# Where to send approved images to
SEND_IG_SMTP_ENABLED = False
SEND_IG_SMTP_MAX_ATTACHMENTS = 10
SEND_IG_SMTP_HOST = '127.0.0.1'
SEND_IG_SMTP_PORT = 587
SEND_IG_SMTP_USER = 'foobar'
SEND_IG_SMTP_PASS = 'secret2'
SEND_IG_SMTP_FROM = 'reviewe@ig_review.foo'
SEND_IG_SMTP_TO = ['somebody@example.com']
SEND_IG_SMTP_SUBJECT = 'reviewed images'
SEND_IG_SMTP_SECURE = ()  # Same syntax as logging.handlers.SMTPHandler

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