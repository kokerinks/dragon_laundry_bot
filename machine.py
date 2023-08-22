from abc import ABC
import datetime
import pytz
from laundry_firebase import LaundryFirebase
import utils

sgt_timezone = pytz.timezone("Asia/Singapore")


class Machine(ABC):
    COMPLETION_TEXT = "Fuyohhhhhh!! Your clothes are ready for collection! Please collect them now so that others may use it"

    # constant value which stores total time required for start (IN SECONDS)
    name = None
    time_to_complete = None

    def __init__(self, new_time_to_complete, new_name):
        self.time_to_complete = new_time_to_complete
        self.name = new_name

    def get_name(self):
        return self.name

    def get_time_to_complete(self):
        return self.time_to_complete

    def status(self):
        curr_user, end_time = LaundryFirebase.get_laundry_timer(self.name)
        if utils.is_available(end_time):
            reply = f"AVAILABLE \U00002705"
            if curr_user:
                reply += f', last used by @{curr_user} ({end_time.astimezone(sgt_timezone).strftime("%d/%m/%Y %I:%M%p")})'
            return reply
        else:
            time_delta = end_time - datetime.datetime.now()
            time_in_min = time_delta.seconds // 60
            time_in_sec = time_delta.seconds % 60
            return f"UNAVAILABLE \U0000274C for {time_in_min}mins and {time_in_sec}s by @{curr_user}"

    def time_left_mins(self):
        return self.time_to_complete // 60

    def time_left_secs(self):
        return self.time_to_complete % 60

    def total_time(self):
        return f"{self.time_left_mins()}mins"

    def start_machine(self, new_user):
        _, end_time = LaundryFirebase.get_laundry_timer(self.name)
        if not utils.is_available(end_time):
            return False
        else:
            new_end_time = datetime.datetime.now() + datetime.timedelta(
                seconds=self.timeToComplete
            )
            new_curr_user = new_user
            LaundryFirebase.set_laundry_timer(self.name, new_curr_user, new_end_time)
            return True

    def alarm(self):
        return self.COMPLETION_TEXT
