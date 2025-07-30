class TNSAAPIError(Exception):
    """Custom exception for TNSA API errors."""
    def __init__(self, message, status_code=None):
        super().__init__(message)
        self.message = message
        self.status_code = status_code

    def __str__(self):
        if self.status_code:
            return f"[Status Code: {self.status_code}] {self.message}"
        return self.message