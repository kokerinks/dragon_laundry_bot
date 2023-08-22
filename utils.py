import os
import datetime

is_prod = os.getenv("FLY_APP_NAME") != None

# Returns True if end_time is None because timer not set --> not being used
def is_available(end_time):
    if not end_time:
        return True
    return end_time < datetime.datetime.now()
