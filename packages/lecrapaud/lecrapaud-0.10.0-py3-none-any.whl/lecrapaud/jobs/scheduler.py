from redbeat.schedulers import RedBeatSchedulerEntry
from celery.schedules import crontab
from lecrapaud.jobs.tasks import app


def schedule_tasks():
    schedule_tasks_list = [
        {
            "name": "task_send_daily_emails",
            "task": "src.jobs.tasks.task_send_daily_emails",
            "schedule": crontab(minute=00, hour=12),
        },
        {
            "name": "task_training_experiment",
            "task": "src.jobs.tasks.task_training_experiment",
            "schedule": crontab(minute=45, hour=00),
        },
    ]

    for task in schedule_tasks_list:
        entry = RedBeatSchedulerEntry(**task, app=app)
        entry.save()


def unschedule_tasks():
    unschedule_task_keys = [
        "redbeat:task_send_daily_emails",
        "redbeat:task_train_models",
    ]

    for key in unschedule_task_keys:
        try:
            entry = RedBeatSchedulerEntry.from_key(key, app=app)
            entry.delete()
        except KeyError:
            pass
