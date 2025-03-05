class ApplicationException(Exception):
    pass


class ResourceNotFoundException(ApplicationException):
    def __init__(self, resource: str = "Resource"):
        super().__init__(f"{resource} not found")
