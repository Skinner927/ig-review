from pathlib import Path
import base64

IMAGE_EXTENSIONS = ['.png', '.jpg', '.jpeg', '.gif', '.tiff']


class RootImageStorage:
    def __init__(self, root):
        self.root = Path(root)

    @staticmethod
    def valid_user_dir(user_dir):
        user_dir = Path(user_dir)
        try:
            return user_dir.is_dir() and user_dir.exists() and user_dir.name[0] != '.'
        except OSError:
            return False

    @staticmethod
    def valid_image_file(img_file):
        img_file = Path(img_file)
        try:
            # I know checking the extension does not suffice, but it works well enough
            return img_file.is_file() and img_file.exists() and \
                   img_file.suffix.lower() in IMAGE_EXTENSIONS
        except OSError:
            return False

    def get_users(self):
        """
        Get all users that have images
        :return:
        :rtype: iter(string)
        """
        for user_dir in self.root.iterdir():
            if user_dir.is_dir() and any(self.get_images_for_user(user_dir.name)):
                yield user_dir.name

    def get_user_image_iterator(self, username):
        """
        Gets an iterator that will endlessly iterate over a user's images until there are none.

        Be careful with this as you cannot wrap it in a list as it will never end. Use
        `get_images_for_user()` instead.

        :param username:
        :type username: string
        :return: File names of images
        :rtype: iter(string)
        """
        user_dir = self.root / username.split('/')[-1]
        if self.valid_user_dir(user_dir):
            return self.ImageIterator(user_dir)
        return iter([])

    def get_images_for_user(self, username):
        """
        Gets all image file names for a user
        :param username:
        :type username: string
        :return:
        :rtype: iter(string)
        """
        try:
            user_dir = self.root / username.split('/')[-1]
            if self.valid_user_dir(user_dir):
                return (f for f in user_dir.iterdir() if self.valid_image_file(f))
        except OSError:
            pass
        # fail
        return iter([])

    class ImageIterator:
        """
        Iterator which will endlessly iterate over images in a given directory.
        The iterator will not throw StopIteration until there are no files in the directory.
        """
        def __init__(self, root):
            self.root = Path(root)
            self._hasRescanned = False
            self._rescan_images()

        @staticmethod
        def _valid_image_file(img_file):
            return RootImageStorage.valid_image_file(img_file)

        def _rescan_images(self):
            self._images = (i for i in self.root.iterdir() if self._valid_image_file(i))

        def __iter__(self):
            return self

        def __next__(self):
            while True:
                try:
                    img = next(self._images)
                    # Ensure it still exists as our iterator is always stale
                    if not self._valid_image_file(img):
                        continue
                    # Reset flag as we've got a valid image
                    self._hasRescanned = False

                    with img.open(mode='rb') as f:
                        b64_img = 'data:image/{};base64,{}'.format(
                            # This is def not the best way to do this
                            img.suffix[1:].lower(),
                            base64.standard_b64encode(f.read()).decode('ascii'))
                    return {
                        'filename': img.name,
                        'src': b64_img,
                    }

                except StopIteration:
                    if self._hasRescanned:
                        raise StopIteration()
                    else:
                        self._hasRescanned = True
                        self._rescan_images()
