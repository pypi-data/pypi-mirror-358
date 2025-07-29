from .alchemy_exception import AlchemyException


class RecordNotFoundError(AlchemyException):
    """Record was not found"""

    def __init__(self, table_class, **kwargs):
        self.table_class = table_class
        self.query = str(kwargs)
        super().__init__(
            f"No record found in {self.table_class.display_name__} ({self.table_class.__tablename__}) for {self.query}."
        )
        self.log()
