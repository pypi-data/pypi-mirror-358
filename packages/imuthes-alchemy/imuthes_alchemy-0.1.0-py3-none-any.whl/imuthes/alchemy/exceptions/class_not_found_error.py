from .alchemy_exception import AlchemyException


class ClassNotFoundError(AlchemyException):
    """Raised when no SQLAlchemy class was found for database table."""

    def __init__(self, table_name: str):
        self.table_name = table_name
        super().__init__(
            f"No mapped class found for database table »{self.table_name}«."
        )
        self.log()
