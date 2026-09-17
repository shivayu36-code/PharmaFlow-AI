class PillCountSensor:

    def __init__(self):

        self.sensor_name = "Pill Count Sensor"
        self.last_detected_count = 0

    def inspect(self, bottle):

        self.last_detected_count = bottle.pill_count

        return self.last_detected_count


class LabelSensor:

    def __init__(self):

        self.sensor_name = "AI Label Sensor"
        self.last_detected_label = "NONE"

    def inspect(self, bottle):

        self.last_detected_label = bottle.actual_label

        return self.last_detected_label