from abc import ABC
import datetime
from math import floor
import pytz

sgt_timezone = pytz.timezone("Asia/Singapore")


class Machine(ABC):
    isAvailable = True

    completionText = "Fuyohhhhhh!! Your clothes are ready for collection! Please collect them now so that others may use it"

    ##constant value which stores total time required for start (IN SECONDS)
    timeToComplete = None

    ##datetime storing start time of machine
    endTime = None

    currUser = ""

    def __init__(self, newTimeToComplete, newName):
        self.timeToComplete = newTimeToComplete
        self.name = newName

    def getName(self):
        return self.name

    def getTimeToComplete(self):
        return self.timeToComplete

    def status(self):
        if self.isAvailable:
            reply = f"AVAILABLE \U00002705"
            if self.currUser:
                reply += f', last used by @{self.currUser} ({self.endTime.astimezone(sgt_timezone).strftime("%d/%m/%Y %I:%M%p")})'
            return reply
        else:
            timeDelta = self.endTime - datetime.datetime.now()
            timeInMin = timeDelta.seconds // 60
            timeInSec = timeDelta.seconds % 60
            return f"UNAVAILABLE \U0000274C for {timeInMin}mins and {timeInSec}s by @{self.currUser}"

    def time_left_mins(self):
        return self.timeToComplete // 60

    def time_left_secs(self):
        return self.timeToComplete % 60

    def total_time(self):
        return f"{self.time_left_mins()}mins"

    def start_machine(self, newUser):
        if not (self.isAvailable):
            return False
        else:
            self.isAvailable = False
            self.endTime = datetime.datetime.now() + datetime.timedelta(
                seconds=self.timeToComplete
            )
            self.currUser = newUser
            return True

    def alarm(self):
        self.isAvailable = True
        return self.completionText
