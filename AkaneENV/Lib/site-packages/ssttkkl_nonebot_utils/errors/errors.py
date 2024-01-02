class BadRequestError(Exception):
    def __init__(self, message: str = ""):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message


class QueryError(Exception):
    def __init__(self, message: str = ""):
        super().__init__()
        self.message = message

    def __str__(self):
        return self.message
