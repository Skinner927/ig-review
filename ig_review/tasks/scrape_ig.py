"""
Run as:
    celery -A ig_review.tasks.scrape_ig worker -B
And debugging:
    celery -A ig_review.tasks.scrape_ig worker --loglevel=info -E -B
"""
from celery.signals import beat_init
from flask import current_app
from ig_review import factory

app = factory.create_celery_app(__name__)


@app.on_after_configure.connect
def schedule_tasks(sender, **kwargs):
    interval = float(60.0 * current_app.config['SCRAPE_IG_INTERVAL'])
    sender.add_periodic_task(interval, test.s(), name='scrape IG every interval')


@beat_init.connect
def kick_first_task(sender, **kwargs):
    test.delay()


@app.task
def test():
    print('RUNNING SCRAPER LOL')