import time
from math import ceil, floor


class RateLimiter:
    def __init__(self, rps):
        self.rps = rps
        self.last_request_time = 0
        self.requests_this_second = 0

    def wait(self):
        """
        Keeps track of the number of requests sent this second. Waits if this
        exceeds rps


        check if we are rate limited.
        First update last_request time

        """
        current_time = time.time()
        # Check if a new second started
        if floor(current_time) > self.last_request_time:
            self.requests_this_second = 0
            self.last_request_time = floor(current_time)

        elif self.requests_this_second >= self.rps:
            time.sleep(ceil(current_time) - current_time)
            self.requests_this_second = 0
            self.last_request_time = ceil(current_time)

        self.requests_this_second += 1
