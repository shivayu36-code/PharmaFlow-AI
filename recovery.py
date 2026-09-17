class RecoverySystem:

    def __init__(self):

        self.last_recovery = "NONE"
        self.recoveries = 0

    def recover_bottle(self, bottle):

        if bottle.inspection_result == "DEFECT":

            self.last_recovery = (
                "Missing pills corrected"
            )

            self.recoveries += 1

            return self.last_recovery

        elif bottle.inspection_result == "WRONG LABEL":

            self.last_recovery = (
                "Wrong label corrected"
            )

            self.recoveries += 1

            return self.last_recovery

        elif bottle.inspection_result == "OVERFILL":

            self.last_recovery = (
                "Overfill corrected"
            )

            self.recoveries += 1

            return self.last_recovery

        self.last_recovery = (
            "No recovery required"
        )

        return self.last_recovery