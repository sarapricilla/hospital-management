class AppointmentNotFoundException(Exception):
    def __init__(self, message="Appointment not found."):
        super().__init__(message)
