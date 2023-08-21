from abc import ABC
import datetime
import pytz

sgt_timezone = pytz.timezone("Asia/Singapore")


class Machine(ABC):
    COMPLETION_TEXT = "Fuyohhhhhh!! Your clothes are ready for collection! Please collect them now so that others may use it"

    # constant value which stores total time required for start (IN SECONDS)
    is_available = True
    time_to_complete = None
    # datetime storing start time of machine
    end_time = None
    curr_user = ""

    def __init__(self, new_time_to_complete, new_name):
        self.time_to_complete = new_time_to_complete
        self.name = new_name

    def get_name(self):
        return self.name

    def get_time_to_complete(self):
        return self.time_to_complete

    def status(self):
        if self.is_available:
            reply = f"AVAILABLE \U00002705"
            if self.curr_user:
                reply += f', last used by @{self.curr_user} ({self.end_time.astimezone(sgt_timezone).strftime("%d/%m/%Y %I:%M%p")})'
            return reply
        time_delta = self.end_time - datetime.datetime.now()
        time_in_min = time_delta.seconds // 60
        time_in_sec = time_delta.seconds % 60
        return f"UNAVAILABLE \U0000274C for {time_in_min}mins and {time_in_sec}s by @{self.curr_user}"

    def time_left_mins(self):
        return self.time_to_complete // 60

    def time_left_secs(self):
        return self.time_to_complete % 60

    def start_machine(self, new_user):
        if not self.is_available:
            return False

        self.is_available = False
        self.end_time = datetime.datetime.now() + datetime.timedelta(
            seconds=self.time_to_complete
        )
        self.curr_user = new_user
        return True

    def alarm(self):
        self.is_available = True
        return self.COMPLETION_TEXT
