from datetime import datetime
import json
import os


class EventLogger:

    def __init__(
        self,
        filename="data/production.json"
    ):

        self.filename = filename

        os.makedirs(
            os.path.dirname(filename),
            exist_ok=True
        )

    def log(
        self,
        event_type,
        bottle_id,
        message,
        decision=""
    ):

        record = {

            "time":
                datetime.now().strftime(
                    "%Y-%m-%d %H:%M:%S"
                ),

            "event":
                event_type,

            "bottle_id":
                bottle_id,

            "message":
                message,

            "decision":
                decision
        }

        records = []

        if os.path.exists(self.filename):

            try:

                with open(
                    self.filename,
                    "r",
                    encoding="utf-8"
                ) as file:

                    records = json.load(file)

                    if not isinstance(
                        records,
                        list
                    ):

                        records = []

            except:

                records = []

        records.append(record)

        records = records[-500:]

        with open(
            self.filename,
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                records,
                file,
                indent=2
            )