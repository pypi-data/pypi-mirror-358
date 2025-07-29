# import inspect
#
# from hakisto import Logger
#
# logger = Logger("imuthes.ansible.exceptions")
#
# Logger.register_excluded_source_file(inspect.currentframe().f_code.co_filename)


class AlchemyException(Exception):
    """Base class for imuthes.ansible exceptions in this module."""

    def __init__(self, msg: str, *args, **kwargs):
        super().__init__(msg, *args)
        self.msg = msg
        self.kwargs = kwargs

    def log(self):
        print(self.msg)

    def __str__(self):
        return self.msg
