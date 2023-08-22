from abc import ABC
import datetime
from math import floor
import pytz
import laundry_firebase
import utils

sgt_timezone = pytz.timezone("Asia/Singapore")


class Machine(ABC):
    completionText = "Fuyohhhhhh!! Your clothes are ready for collection! Please collect them now so that others may use it"

    ##constant value which stores total time required for start (IN SECONDS)
    timeToComplete = None

    def __init__(self, newTimeToComplete, newName):
        self.timeToComplete = newTimeToComplete
        self.name = newName

    def getName(self):
        return self.name

    def getTimeToComplete(self):
        return self.timeToComplete

    def status(self):
        curr_user, end_time = laundry_firebase.get_laundry_timer(self.name)
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
        return self.timeToComplete // 60

    def time_left_secs(self):
        return self.timeToComplete % 60

    def total_time(self):
        return f"{self.time_left_mins()}mins"

    def start_machine(self, new_user):
        _, end_time = laundry_firebase.get_laundry_timer(self.name)
        if not utils.is_available(end_time):
            return False
        else:
            new_end_time = datetime.datetime.now() + datetime.timedelta(
                seconds=self.timeToComplete
            )
            new_curr_user = new_user
            laundry_firebase.set_laundry_timer(self.name, new_curr_user, new_end_time)
            return True

    def alarm(self):
        return self.completionText
