import os
import json
import datetime
import firebase_admin
from firebase_admin import db
from utils import is_prod

prod_ref = "/prod"
beta_ref = "/beta"


def authenticate():
    json_cert = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
    app = firebase_admin.initialize_app(
        firebase_admin.credentials.Certificate(json_cert),
        {
            "databaseURL": "https://dragon-laundry-bot-default-rtdb.asia-southeast1.firebasedatabase.app/"
        },
    )


def set_laundry_timer(name: str, curr_user: str, end_time: datetime.datetime):
    env_data = db.reference(prod_ref if is_prod else beta_ref)
    env_data.child(name).set(
        {
            "currUser": curr_user,
            "endTime": end_time.timestamp(),
        }
    )


def get_laundry_timer(name: str) -> tuple[str, datetime.datetime | None]:
    env_data = db.reference(prod_ref if is_prod else beta_ref)
    timer_data = env_data.child(name).get()
    if timer_data and timer_data["currUser"] and timer_data["endTime"]:
        return (
            timer_data["currUser"],
            datetime.datetime.fromtimestamp(timer_data["endTime"]),
        )
    return ("", None)
