from .alchemy_exception import AlchemyException


class MultipleRecordsFoundError(AlchemyException):
    """Raised when only up to one record was expected, but more were found."""

    def __init__(self, table_class, count: int):
        self.table_class = table_class
        super().__init__(
            f"{count} records found when only one was expected for {self.table_class.display_name__} ({self.table_class.__tablename__})."
        )
        self.log()
