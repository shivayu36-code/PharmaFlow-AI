class FactoryRouter:

    def __init__(self):

        self.router_name = (
            "PharmaFlow AI Factory Router"
        )

    def route_bottle(
        self,
        bottle,
        output_y,
        defect_y
    ):

        if bottle.inspection_result == "PASS":

            bottle.route_to_belt(output_y)

            return "OUTPUT"

        else:

            bottle.route_to_belt(defect_y)

            return "REWORK"