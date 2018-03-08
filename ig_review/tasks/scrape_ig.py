"""
Run as:
    celery worker -A ig_review.tasks.scrape_ig -B
And debugging:
    celery worker -A ig_review.tasks.scrape_ig -B --loglevel=info -E
"""
from celery.signals import beat_init
from ig_review import factory

app = factory.create_celery_app(__name__)


@app.on_after_configure.connect
def schedule_tasks(sender, **kwargs):
    interval = 60.0 * float(sender.conf['SCRAPE_IG_INTERVAL'])
    sender.add_periodic_task(interval, do_scrape.s(), name='Scrape IG at interval')


@beat_init.connect
def kick_first_task(sender, **kwargs):
    do_scrape.delay()


@app.task(bind=True)
def do_scrape(self):
    print('Scrape ' + self.app.conf['SCRAPE_IG_USER'])
    #ig_scraper.scrape()
