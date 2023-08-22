import os
import json
import datetime
import firebase_admin
from firebase_admin import db
from utils import is_prod

prod_ref = "/prod"
beta_ref = "/beta"


class LaundryFirebase:
    db_reference = None
    laundry_data = None

    @staticmethod
    def query_firebase(event: db.Event = None):
        LaundryFirebase.laundry_data = LaundryFirebase.db_reference.get()

    @staticmethod
    def authenticate():
        json_cert = json.loads(os.getenv("FIREBASE_CREDENTIALS"))
        app = firebase_admin.initialize_app(
            firebase_admin.credentials.Certificate(json_cert),
            {
                "databaseURL": "https://dragon-laundry-bot-default-rtdb.asia-southeast1.firebasedatabase.app/"
            },
        )
        LaundryFirebase.db_reference = db.reference(prod_ref if is_prod else beta_ref)
        LaundryFirebase.query_firebase()
        LaundryFirebase.db_reference.listen(LaundryFirebase.query_firebase)

    @staticmethod
    def set_laundry_timer(name: str, curr_user: str, end_time: datetime.datetime):
        LaundryFirebase.db_reference.child(name).set(
            {
                "currUser": curr_user,
                "endTime": end_time.timestamp(),
            }
        )

    @staticmethod
    def get_laundry_timer(name: str) -> tuple[str, datetime.datetime]:
        timer_data = LaundryFirebase.laundry_data.get(name, None)
        if timer_data and timer_data.get("currUser") and timer_data.get("endTime"):
            return (
                timer_data["currUser"],
                datetime.datetime.fromtimestamp(timer_data["endTime"]),
            )
        return ("", None)
