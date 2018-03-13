"""
Run as:
    celery worker -A ig_review.tasks -B
And debugging:
    celery worker -A ig_review.tasks --loglevel=info -E -B
"""
# Ensure to use absolute module reference or celery worker may not work
from celery.signals import beat_init
from email.message import EmailMessage
from ig_review import factory
from ig_review.api.image_storage import RootImageStorage
from instagram_scraper import InstagramScraper
from pathlib import Path
import functools
import imghdr
import os
import os.path
import smtplib

app = factory.create_celery_app(__name__)


def single_instance_task(func):
    """
    Decorator to prevent tasks from running at the same time.
    Works independent of OS and process/thread.

    :param func:
    :return:
    """

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        self = args[0]
        func_name = 'celerylock-' + func.__name__
        lock_file = os.path.join(self.app.conf['LOCKFILE_DIR'], func_name)
        try:
            f = open(lock_file, 'x')
            f.write(str(os.getpid()))
        except OSError:
            # Someone holds the lock, get out!
            self.log.info('wanted to run but locked ' + func_name)
            return
        try:
            return func(*args, **kwargs)
        finally:
            f.close()
            os.remove(lock_file)

    return wrapper


@app.on_after_configure.connect
def schedule_tasks(sender, **kwargs):
    interval = 60.0 * float(sender.conf['SCRAPE_IG_INTERVAL'])
    sender.add_periodic_task(interval, do_scrape.s(), name='Scrape IG at interval')

    interval = 60.0 * float(sender.conf['SEND_IG_APPROVED'])
    sender.add_periodic_task(interval, do_mail_images.s(), name='Send reviewed images')


@beat_init.connect
def kick_first_task(sender, **kwargs):
    do_scrape.delay()
    do_mail_images.delay()


@app.task(bind=True)
@single_instance_task
def do_scrape(self):
    self.log.info('Scraping IG as ' + self.app.conf['SCRAPE_IG_USER'])
    scraper = InstagramScraper(
        login_user=self.app.conf['SCRAPE_IG_USER'],
        login_pass=self.app.conf['SCRAPE_IG_PASS'],
        usernames=self.app.conf['SCRAPE_IG_FRIENDS'],
        destination=self.app.conf['IMAGES_REVIEW_DIR'],
        retain_username=True,
        media_types=['image', 'story-image'],
        maximum=self.app.conf['SCRAPE_IG_MAX_PER_FRIEND'],
        latest_stamps=os.path.join(self.app.conf['STORAGE_ROOT'], 'ig_user_stamps.ini'),
    )
    scraper.scrape()
    self.log.info('Done scraping IG without errors as ' + self.app.conf['SCRAPE_IG_USER'])


@app.task(bind=True)
@single_instance_task
def do_mail_images(self):
    if not self.app.conf['SEND_IG_SMTP_ENABLED']:
        self.log.info('Sending images is disabled')
        return

    self.log.info('Starting to send images')

    # Create a message
    msg = EmailMessage()
    msg['Subject'] = self.app.conf['SEND_IG_SMTP_SUBJECT']
    msg['From'] = self.app.conf['SEND_IG_SMTP_FROM']
    msg['To'] = ', '.join(self.app.conf['SEND_IG_SMTP_TO'])

    # Get all images
    img_dir = Path(self.app.conf['IMAGES_SEND_DIR'])
    max_files = self.app.conf['SEND_IG_SMTP_MAX_ATTACHMENTS']
    files_sent = 0
    for file in img_dir.iterdir():
        if files_sent >= max_files:
            break
        # Ensure they're legit
        if not RootImageStorage.valid_image_file(file):
            self.log.warning('Invalid image file in send directory ' + str(file))
            os.remove(file)
            continue

        with open(file, 'rb') as f:
            img_data = f.read()
        msg.add_attachment(img_data,
                           maintype='image',
                           subtype=imghdr.what(None, img_data),
                           filename=os.path.basename(file))
        files_sent += 1

    if files_sent < 1:
        self.log.info('No images to send')
        return

    # Create SMTP sender
    with smtplib.SMTP(host=self.app.conf['SEND_IG_SMTP_HOST'],
                      port=self.app.conf['SEND_IG_SMTP_PORT']) as s:
        secure = self.app.conf['SEND_IG_SMTP_SECURE']
        if isinstance(secure, tuple) or secure:
            kwargs = {}
            if len(secure) > 0:
                kwargs['keyfile'] = secure[0]
                if len(secure) == 2:
                    kwargs['certfile'] = secure[1]
            s.starttls(**kwargs)
        if self.app.conf['SEND_IG_SMTP_USER']:
            s.login(self.app.conf['SEND_IG_SMTP_USER'], self.app.conf['SEND_IG_SMTP_PASS'])
        s.send_message(msg)

    self.log.info('Done sending {} images without errors'.format(files_sent))
