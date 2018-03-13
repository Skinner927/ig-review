from celery import Celery, Task
from celery.utils.log import get_task_logger
from flask import Flask
import logging
from logging.handlers import SMTPHandler
import os
import os.path
from .core import register_blueprints

_mail_logger_instance = None


def _get_mail_logger_instance(app):
    """
    We only ever need one email logger
    :param app:
    :return:
    """
    global _mail_logger_instance

    if not _mail_logger_instance:
        _mail_logger_instance = SMTPHandler(
            mailhost=(app.config['ERROR_SMTP_HOST'], app.config['ERROR_SMTP_PORT']),
            fromaddr=app.config['ERROR_SMTP_FROM'],
            toaddrs=app.config['ERROR_SMTP_TO'],
            subject=app.config['ERROR_SMTP_SUBJECT'],
            credentials=(app.config['ERROR_SMTP_USER'], app.config['ERROR_SMTP_PASS']),
            secure=app.config['ERROR_SMTP_SECURE']
        )
    return _mail_logger_instance


def create_app(package_name, package_path, settings_override=None):
    """
    Called by each module to get their `app` object that will be properly configured per
    application wide settings.

    :param package_name: application package name
    :param package_path: application package path
    :param settings_override: a dictionary of settings to override
    """
    app = Flask(package_name, instance_relative_config=True)

    # Build configuration
    app.config.from_object('ig_review.default_settings')
    app.config.from_pyfile('settings.cfg', silent=True)
    app.config.from_envvar('IG_REVIEW_SETTINGS', silent=True)
    app.config.from_object(settings_override)

    # Fix expected relative paths and make dirs
    map_relative_path_from_storage_root = [
        'IMAGES_REVIEW_DIR',
        'IMAGES_SEND_DIR',
        'USER_STORAGE_FILE',
        'LOCKFILE_DIR',
    ]
    app.config['STORAGE_ROOT'] = app.config['STORAGE_ROOT'] or app.instance_path
    for key in map_relative_path_from_storage_root:
        val = app.config[key]
        if not os.path.isabs(val):
            app.config[key] = os.path.join(app.config['STORAGE_ROOT'], val)

        path = app.config[key]
        if key.endswith('_FILE'):
            path = os.path.dirname(path)
        os.makedirs(path, exist_ok=True)

    # Load any blueprints contained within this package
    register_blueprints(app, package_name, package_path)

    if app.config['ERROR_SMTP_ENABLED'] and not app.debug:
        mail_handler = _get_mail_logger_instance(app)
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)

    return app


def create_celery_app(mod_name, app=None):
    app = app or create_app(mod_name, os.path.dirname(__file__))
    celery = Celery(mod_name,
                    backend=app.config['CELERY_BACKEND_URL'],
                    broker=app.config['CELERY_BROKER_URL'])
    celery.conf.update(app.config)

    # Create a unique name for our beat schedule file
    celery.conf.beat_schedule_filename = os.path.join(
        app.config['STORAGE_ROOT'],
        'beat-schedule-' + mod_name)

    logger = get_task_logger(mod_name)

    if app.config['ERROR_SMTP_ENABLED']:
        mail_handler = _get_mail_logger_instance(app)
        mail_handler.setLevel(logging.ERROR)
        logger.addHandler(mail_handler)

    class AppContextClass(Task):

        def __call__(self, *args, **kwargs):
            with app.app_context():
                return super(AppContextClass, self).__call__(*args, **kwargs)

        @property
        def log(self):
            return logger

        def on_failure(self, exc, task_id, args, kwargs, einfo):
            """
            Arguments:
                exc (Exception): The exception raised by the task.
                task_id (str): Unique id of the failed task.
                args (Tuple): Original arguments for the task that failed.
                kwargs (Dict): Original keyword arguments for the task that failed.
                einfo (~billiard.einfo.ExceptionInfo): Exception information.
            """
            logger.exception(exc, info=einfo, args=args, kwargs=kwargs)

    celery.Task = AppContextClass
    return celery
