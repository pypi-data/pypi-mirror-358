

class ErrorObjects(Exception):
    '''
    Custom error class to capture abnormal response and trigger
    readable error object which helps user to adapt easily with
    the main application
    '''
    def __init__(self, data, status: int=400):
        self.status = status
        self.details = data
        self.message = "Error while fetching token"
        super().__init__(f"Status {status}: {self._handle_content()}")

    def _handle_content(self):
        if isinstance(self.details,dict):
            return self.details.get('msg') or self.details.get('message') or str(self.details)
        elif isinstance(self.details,bytes):
            try:
                return self.details.decode("utf-8")
            except:
                return 'received binary content, unable to parse it'
        return str(self.details)

    def __str__(self):
        return f"status code: {self.status}; content: {self._handle_content()}"