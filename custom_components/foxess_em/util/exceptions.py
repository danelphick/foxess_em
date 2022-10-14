""""No data exception"""


class NoDataError(Exception):
    """No data"""

    def __init__(self, message):
        self.message = message
        super().__init__(self.message)

    def __str__(self):
        return f"{self.message}"
