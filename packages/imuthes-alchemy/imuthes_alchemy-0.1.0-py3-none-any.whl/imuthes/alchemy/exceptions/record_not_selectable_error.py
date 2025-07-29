from .alchemy_exception import AlchemyException


class RecordNotSelectableError(AlchemyException):
    """Record is not active"""

    def __init__(self, table_class, record):
        self.table_class = table_class
        self.record = record
        super().__init__(
            f"Record {self.record!s} of {self.table_class.display_name__} ({self.table_class.__tablename__}) can not be selected."
        )
        self.log()
