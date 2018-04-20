from flask_api.parsers import BaseParser
# TODO: They should do something actually
class JpegImageParser(BaseParser):
    """
    Image parser.
    """
    media_type = 'image/jpeg'

    def parse(self, stream, media_type, **options):
        """
        Simply return a string representing the body of the request.
        """
        return stream
    
class PngImageParser(BaseParser):
    """
    Image parser.
    """
    media_type = 'image/png'

    def parse(self, stream, media_type, **options):
        """
        Simply return a string representing the body of the request.
        """
        return stream