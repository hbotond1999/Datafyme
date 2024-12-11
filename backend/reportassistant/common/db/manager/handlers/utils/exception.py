

class ExecuteQueryError(Exception):
    """
    Custom exception to handle errors during SQL query execution.

    Attributes:
        message (str): A description of the error.
        original_exception (Exception, optional): The original exception that caused this error.
    """
    def __init__(self, message, original_exception=None):
        self.message = message
        self.original_exception = original_exception
        super().__init__(self.message)

    def __str__(self):
        if self.original_exception:
            return f"{self.message} (Caused by: {self.original_exception})"
        return self.message
