import io
import os
import uuid
from mimetypes import guess_extension, guess_type
import json
import logging
import base64
from werkzeug.datastructures import FileStorage

from mlapi.shellColors import ShellColors

class ImageStorage(object):
    '''Contains methods for on-server images processing.

    Attributes
    ----------
    _storage_path: str
        Path to a folder where the iages will be saved.
    _uuidgen: uuid.uuid4, any function returning str
        Function returning unique strings. \`uuid.uuid4\` by default
    fopen: io.open, function opening files
        Function that opens files. \`io.open\` by default

    Methods
    -------
    save
    '''
    _CHUNK_SIZE_BYTES = 4096
    DBGT = ShellColors.YELLOW + "[ImageStorage] " + ShellColors.ENDC
    # Note the use of dependency injection for standard library
    # methods. We'll use these later to avoid monkey-patching.
    def __init__(self, storage_path, uuidgen=uuid.uuid4, fopen=io.open):
        self._storage_path = storage_path
        self._uuidgen = uuidgen
        self._fopen = fopen

    def save(self, image_stream, image_content_type):
        '''Saves given image stream. Sets the extension basing on Content-Type.

        Parameters
        ----------
        image_stream: str
            Stream of bytes, Base64 coded image, FileStorage
        image_content_type: str
            Type of image sent e.g "image/jpeg", "application/json" etc.
        '''
        if image_stream:
            
            logging.info(self.DBGT + "Loading {} type image".format(image_content_type))
            try:
                ext = guess_extension(image_content_type)
            except:
                logging.error("There was a problem while guessing image's extension.")
                
            if image_content_type == "application/json" or image_content_type == "application/x-www-form-urlencoded":
                base64_split = image_stream['image'].split(',')
                logging.debug("Got header: {}".format(base64_split[0]))
                # Splitting for getting string in "image/jpeg" format.
                ext = guess_extension(base64_split[0].split(';')[0].split(":")[1])
            if ext==".jpe":
                ext=".jpg"

            name = '{uuid}{ext}'.format(uuid=self._uuidgen(), ext=ext)
            image_path = os.path.join(self._storage_path, name)
            logging.info(self.DBGT + "Image's extension: {}".format(ext))
            with self._fopen(image_path, 'wb') as image_file:
                if image_content_type == "application/json" or image_content_type == "application/x-www-form-urlencoded":
                    try:
                        ### Decoding part without the "Data:image/jpeg;base64," header in the beginning.
                        b = base64.b64decode(base64_split[1])
                        # logging.debug(self.DBGT + "Decoded image: {}".format(b))
                    except:
                        logging.error(self.DBGT + "Error while reading Base64 image from client.")
                    image_file.write(b)
                else:
                    if type(image_stream) == FileStorage:
                        image_stream = image_stream.stream
                    while True:
                        chunk = image_stream.read(self._CHUNK_SIZE_BYTES)
                        if not chunk:
                            break
                        image_file.write(chunk)
            logging.debug("Saved file to {}".format(image_path))
            return image_path
        else:
            logging.error("The posted file is empty")
    