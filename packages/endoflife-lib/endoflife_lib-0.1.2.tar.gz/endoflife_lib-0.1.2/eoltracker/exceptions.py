# exception for EOL Tracker related error
class EOLTrackerAPIError(Exception):
    def __init__(self, message, status_code=None, payload=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code
        self.payload = payload

    def __str__(self):
        base = f"EOLTrackerAPIError: {self.message}"
        if self.status_code:
            base += f" (status code: {self.status_code})"
        if self.payload:
            base += f" | Payload: {self.payload}"
        return base