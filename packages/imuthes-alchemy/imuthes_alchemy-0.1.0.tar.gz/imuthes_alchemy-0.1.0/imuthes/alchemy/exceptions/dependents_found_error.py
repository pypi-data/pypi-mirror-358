from .alchemy_exception import AlchemyException


class DependentsFoundError(AlchemyException):
    """Dependent Records were found."""

    def __init__(self, table_class, dependents):
        self.table_class = table_class
        self.dependents = dependents
        super().__init__(
            f"{len(self.dependents)} dependent(s) found for {self.table_class.display_name__} ({self.table_class.__tablename__})."
        )
        self.log()
