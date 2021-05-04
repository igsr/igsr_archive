import logging

# create logger
object_logger = logging.getLogger(__name__)


class fObject(object):
    """
    Class to represent a FIRE object. An Object is
    the encapsulation of a file which was successfully archived.

    Attributes
    ----------
    objectId : int
               The numerical unique identifier of an object.
               Intended for making paging queries easier.
    fireOid : str
              The unique identifier in the string form of an object.
    md5 : str
          md5sum.
    size : int
           Size of objects in bytes.
    createTime : str
                 Representing datetime: i.e. '2020-02-17 16:44:55'.
    path : str
           Fire path of the object.
    published : bool
                True if associated object is exposed by the FUSE layer.
    """
    def __init__(self, **kwargs):
        """
        Constructor

        Parameters
        ----------
        **kwargs : dict, optional
                   Extra arguments to `fObject`: refer to each fObject documentation for a
                   list of all possible arguments.
        """

        object_logger.debug('Creating a FIRE Object')

        allowed_keys = ['objectId', 'fireOid', 'md5', 'size',
                        'createTime', 'path', 'published', 'objectMd5',
                        'objectSize']

        self.__dict__.update((k, v) for k, v in kwargs.items() if k in allowed_keys)

    # object introspection
    def __str__(self):
        sb = []
        for key in self.__dict__:
            sb.append("{key}='{value}'".format(key=key, value=self.__dict__[key]))

        return ', '.join(sb)

    def __repr__(self):
        return self.__str__()