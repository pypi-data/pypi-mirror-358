from .alchemy_exception import AlchemyException


class NameLengthExceededError(AlchemyException):
    """The length of the value provided is too long"""

    def __init__(self, table_class, value: str):
        self.table_class = table_class
        self.value = value
        super().__init__(
            f"Length ({len(self.value)}) of Value '{self.value}' exceeds permitted length of 'name' in {self.table_class.display_name__} ({self.table_class.__tablename__})."
        )
        self.log()
