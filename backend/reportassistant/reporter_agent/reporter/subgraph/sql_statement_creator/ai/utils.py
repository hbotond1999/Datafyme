class RefineLimitExceededError(Exception):
    """
    Custom exception to handle refine limit exceeded errors.

    Attributes:
        message (str): A description of the refine limit error.
    """
    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return self.message
