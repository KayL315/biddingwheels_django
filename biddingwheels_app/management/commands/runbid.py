import logging

from django.conf import settings

from apscheduler.schedulers.blocking import BlockingScheduler
from apscheduler.triggers.cron import CronTrigger
from django.core.management.base import BaseCommand
from django_apscheduler.jobstores import DjangoJobStore
from django_apscheduler.models import DjangoJobExecution
from django_apscheduler import util
from django.db import connection

logger = logging.getLogger(__name__)


def update_transactions():
    cursor = connection.cursor()
    # start SQL transaction
    cursor.execute("START TRANSACTION")
    # find all carlist that are out of date
    cursor.execute(
        """
            WITH BidList as (SELECT listid, highestBid, highestBidHolder FROM CarListing WHERE biddingDeadline < NOW() AND isSold = 0)
            UPDATE Transactions SET done = 1 WHERE list_id in (SELECT listid FROM BidList)
        """
    )

    cursor.execute(
        """
            WITH BidList as (SELECT listid, highestBid, highestBidHolder FROM CarListing WHERE biddingDeadline < NOW() AND isSold = 0)
            DELETE FROM Transactions WHERE list_id IN (SELECT listid as list_id FROM BidList) AND buyer_id NOT IN (SELECT highestBidHolder FROM BidList)
        """
    )

    # add shipment data
    cursor.execute(
        """
        SELECT t.buyer_id, t.transaction_id, t.address_id 
    FROM Transactions t
    inner JOIN CarListing c ON t.list_id = c.listid
    WHERE c.biddingDeadline > NOW() 
    AND c.isSold = 0
    AND t.buyer_id = c.highestBidHolder
    """
    )

    transaction = cursor.fetchall()

    if transaction:
        for row in transaction:
            cursor.execute(
                "INSERT INTO Shipping (user_id, transaction_id, tracking_number, address_id, status, date) VALUES (%s, %s, FLOOR(RAND() * 10000000000), %s, 'Pending', NOW()) ",
                [row[0], row[1], row[2]],
            )

    # update the status of the carlist to sold if the bidding deadline is passed, suppose we have more than one carlist that are out of date
    cursor.execute(
        """
            WITH BidList as (SELECT listid, highestBid, highestBidHolder FROM CarListing WHERE biddingDeadline < NOW() AND isSold = 0)
            UPDATE CarListing SET isSold = 1 WHERE listid in (SELECT listid FROM BidList)
        """
    )

    # end SQL transaction
    cursor.execute("Commit")

    print("Updated transactions")


# The `close_old_connections` decorator ensures that database connections, that have become
# unusable or are obsolete, are closed before and after your job has run. You should use it
# to wrap any jobs that you schedule that access the Django database in any way.
@util.close_old_connections
def delete_old_job_executions(max_age=604_800):
    """
    This job deletes APScheduler job execution entries older than `max_age` from the database.
    It helps to prevent the database from filling up with old historical records that are no
    longer useful.

    :param max_age: The maximum length of time to retain historical job execution records.
                    Defaults to 7 days.
    """
    DjangoJobExecution.objects.delete_old_job_executions(max_age)


class Command(BaseCommand):
    help = "Runs APScheduler."

    def handle(self, *args, **options):
        scheduler = BlockingScheduler(timezone=settings.TIME_ZONE)
        scheduler.add_jobstore(DjangoJobStore(), "default")

        scheduler.add_job(
            update_transactions,
             # every day at midnight
            trigger=CronTrigger(
                day_of_week="mon-sun", hour="00", minute="01"
            ),
            id="update_transactions",  # The `id` assigned to each job MUST be unique
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added job 'update_transactions'.")

        scheduler.add_job(
            delete_old_job_executions,
            trigger=CronTrigger(
                day_of_week="mon", hour="00", minute="00"
            ),  # Midnight on Monday, before start of the next work week.
            id="delete_old_job_executions",
            max_instances=1,
            replace_existing=True,
        )
        logger.info("Added weekly job: 'delete_old_job_executions'.")

        try:
            logger.info("Starting scheduler...")
            scheduler.start()
        except KeyboardInterrupt:
            logger.info("Stopping scheduler...")
            scheduler.shutdown()
            logger.info("Scheduler shut down successfully!")
