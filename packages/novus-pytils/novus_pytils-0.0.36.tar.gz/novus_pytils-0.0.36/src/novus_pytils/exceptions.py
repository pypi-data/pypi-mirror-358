class PathNotFoundException(Exception):
    def __init__(self, message, invalid_value):
        super().__init__(message)
        self.invalid_value = invalid_value

    def __str__(self):
        return f"Error: {self.args[0]} - Path not found: {self.invalid_value}"