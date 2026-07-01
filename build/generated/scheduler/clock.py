import time

class HighResolutionSystemClock:
    @staticmethod
    def get_monotonic_time():
        return time.monotonic()

    @staticmethod
    def get_wall_clock_drift(reference_time):
        return time.time() - reference_time