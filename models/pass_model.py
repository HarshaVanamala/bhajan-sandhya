class Pass:
    def __init__(self, code, registration):
        self.code = code
        self.name = registration.name
        self.email = registration.email
        self.phone = registration.phone
        self.status = "Pending"