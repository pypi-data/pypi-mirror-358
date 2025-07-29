class PathNotFoundException(Exception):
    def __init__(self, invalid_value):
        super().__init__("Path not found")
        self.invalid_value = invalid_value

    def __str__(self):
        return f"{self.message} : {self.invalid_value}"
    
class FileNotFoundException(Exception):
    def __init__(self, invalid_value):
        super().__init__("Path not found")
        self.invalid_value = invalid_value

    def __str__(self):
        return f"{self.message} : {self.invalid_value}"