class AIEngine:

    def __init__(self):

        self.engine_name = (
            "PharmaFlow AI Decision Engine"
        )

        self.last_decision = "NONE"

    def inspect_pill_count(
        self,
        detected_pills,
        expected_pills
    ):

        if detected_pills == expected_pills:

            return "PASS"

        elif detected_pills < expected_pills:

            return "DEFECT"

        else:

            return "OVERFILL"

    def inspect_label(
        self,
        detected_label,
        expected_label
    ):

        if detected_label == expected_label:

            return "CORRECT"

        return "WRONG"

    def final_decision(
        self,
        detected_pills,
        expected_pills,
        detected_label,
        expected_label
    ):

        pill_result = self.inspect_pill_count(
            detected_pills,
            expected_pills
        )

        label_result = self.inspect_label(
            detected_label,
            expected_label
        )

        if pill_result == "OVERFILL":

            decision = "OVERFILL"

        elif pill_result == "DEFECT":

            decision = "DEFECT"

        elif label_result == "WRONG":

            decision = "WRONG LABEL"

        else:

            decision = "PASS"

        self.last_decision = decision

        return decision