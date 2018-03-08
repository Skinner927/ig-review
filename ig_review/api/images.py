from flask import Blueprint, request, make_response, jsonify
import os.path
import random
import shutil
import string
from . import NoDataException
from .authentication import require_login
from .image_storage import RootImageStorage

bp = Blueprint('images', __name__)
user_iterators = {}

img_storage = None
_IMAGES_REVIEW_DIR = None
_IMAGES_SEND_DIR = None


@bp.record
def init_storage(setup_state):
    global img_storage, _IMAGES_REVIEW_DIR, _IMAGES_SEND_DIR
    img_storage = RootImageStorage(setup_state.app.config['IMAGES_REVIEW_DIR'])
    _IMAGES_REVIEW_DIR = setup_state.app.config['IMAGES_REVIEW_DIR']
    _IMAGES_SEND_DIR = setup_state.app.config['IMAGES_SEND_DIR']


@bp.route('/images/users')
@require_login
def get_users():
    return jsonify(list(img_storage.get_users()))


@bp.route('/images/<string:username>', methods=['GET'])
@require_login
def get_images(username):
    """
    Get all images for a user
    :param username:
    :return:
    """
    files = [f.name for f in img_storage.get_images_for_user(username)]
    if len(files) < 1:
        raise NoDataException('User has no images')
    return jsonify(files)


@bp.route('/images/<string:username>/next', methods=['GET'])
@require_login
def get_next_image(username):
    """
    Get next image for a user. An internal generator keeps track of the next available image.
    The next image is global so if multiple consumers are iterating through the same user's files,
    there's no guarantee two consumers will ever receive the same sequence of images.

    :param username:
    :return:
    """
    try:
        if username not in user_iterators:
            user_iterators[username] = img_storage.get_user_image_iterator(username)
        return jsonify(next(user_iterators[username]))
    except StopIteration:
        pass
    raise NoDataException('User has no images')


@bp.route('/images/<string:username>/<string:image_name>', methods=['POST', 'DELETE'])
@require_login
def mail_image(username, image_name):
    global _IMAGES_REVIEW_DIR, _IMAGES_SEND_DIR
    username = username.split('/')[-1]
    image_name = image_name.split('/')[-1]
    src_path = os.path.join(_IMAGES_REVIEW_DIR, username, image_name)

    if not RootImageStorage.valid_image_file(src_path):
        raise NoDataException()

    if request.method == 'POST':
        if not os.path.exists(_IMAGES_SEND_DIR):
            os.makedirs(_IMAGES_SEND_DIR)

        rand = ''.join(random.choice(string.ascii_uppercase + string.digits) for _ in range(8))
        dest_path = os.path.join(_IMAGES_SEND_DIR, username + '_' + rand + '_' + image_name)

        shutil.copyfile(src_path, dest_path)

    os.remove(src_path)
    return make_response(jsonify(True), 200)
