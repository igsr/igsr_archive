import logging

# create logger
object_logger = logging.getLogger(__name__)


class Object(object):
    """
    Class to represent a Fire object. An Object is
    the encapsulation of a file which was successfully archived.

    Class variables
    ---------------
    objectId : int
               The numerical unique identifier of an object.
               Intended for making paging queries easier.
    fireOid : int
              The unique identifier in the string form of an object.
    md5 : str
          md5sum
    size : int
           Size of objects in bytes

    """
    def __init__(self, **kwargs):

        object_logger.info('Creating a Fire Object')
