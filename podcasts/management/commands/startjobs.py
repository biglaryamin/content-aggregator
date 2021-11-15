from django.core.management.base import BaseCommand
from django.utils import timezone
import feedparser
from dateutil import parser
from podcasts.models import Episode

def save_new_episodes(feed,*args):
        podcast_title = feed.channel.title
        podcast_image = feed.channel.image["href"]

        for item in feed.entries:
            if not Episode.objects.filter(guid=item.guid).exists():
                episode = Episode(
                    title=args[0]+item.title,
                    description=item.description,
                    pub_date=parser.parse(item.published),
                    link=item.link,
                    image=podcast_image,
                    podcast_name=podcast_title,
                    guid=item.guid,
                )
                episode.save()
            




def fetch_realpython_episodes():
    _feed = feedparser.parse("https://realpython.com/podcasts/rpp/feed")
    save_new_episodes(_feed)


def fetch_talkpython_episodes():
    _feed=feedparser.parse("https://talkpython.fm/episodes/rss")
    save_new_episodes(_feed)

class Command(BaseCommand):
    def handle(self, *args, **options):
        fetch_realpython_episodes()
        fetch_talkpython_episodes()



# Standard Library
import logging

# Django
from django.conf import settings
from django.core.management.base import BaseCommand


# Third Party
import feedparser
from dateutil import parser
from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution


# Models
from podcasts.models import Episode
logger = logging.getLogger(__name__)




def delete_old_job_executions(max_age=604_800):
    """Deletes all apscheduler job execution logs older than `max_age`."""
    DjangoJobExecution.objects.delete_old_job_executions(max_age)

def handle(self, *args ,**option):
    scheduler=BlockingScheduler(timezone=settings.TIME_ZONE)
    scheduler.add_jobstore(DjangoJobStore(),"default")

    #
    #


    scheduler.add_job(
        fetch_realpython_episodes,
        trigger="interval",
        minutes=2,
        id="The Real Python Podcast",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added job: The Real Python Podcast.")

    scheduler.add_job(
        fetch_talkpython_episodes,
        trigger="interval",
        minutes=2,
        id="Talk Pyhton Feed",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Add job: Talk Python Feed.")

    scheduler.add_job(
        delete_old_job_executions,
        trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),
        id="Delete Old Job Executions",
        max_instances=1,
        replace_existing=True,
    )
    logger.info("Added weekly job: Delete Old Job Execution.")

    try:
        logger.info("Starting scheduler...")
        scheduler.start()
    except KeyboardInterrupt:
        logger.info("Stopping scheduler...")
        scheduler.shutdown()
        logger.info("Scheduler shut down successfully!")