from flask import Flask
import os
import os.path
from .core import register_blueprints


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
    ]
    storage_root = app.config['STORAGE_ROOT'] or app.instance_path
    for key in map_relative_path_from_storage_root:
        val = app.config[key]
        if not os.path.isabs(val):
            app.config[key] = os.path.join(storage_root, val)

        path = app.config[key]
        if key.endswith('_FILE'):
            path = os.path.dirname(path)
        os.makedirs(path, exist_ok=True)

    # Load any blueprints contained within this package
    register_blueprints(app, package_name, package_path)

    return app
