class PathNotFoundException(Exception):
    def __init__(self, invalid_value):
        super().__init__("Path not found")
        self.invalid_value = invalid_value
