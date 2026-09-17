import pygame
import random


class Bottle:

    def __init__(self, bottle_id, x, y):

        self.bottle_id = bottle_id

        self.x = x
        self.y = y

        self.target_y = y
        self.target_x = x

        self.speed = 2.5
        self.vertical_speed = 3

        self.width = 30
        self.height = 45

        # ====================================================
        # FACTORY POSITIONS
        # ====================================================

        self.vertical_belt_x = 700
        self.rework_station_x = 100

        # ====================================================
        # PILL INFORMATION
        # ====================================================

        self.expected_pills = 100
        self.pill_count = 0

        # ====================================================
        # LABEL INFORMATION
        # ====================================================

        self.expected_label = "MEDICINE-A"
        self.actual_label = "MEDICINE-A"

        # ====================================================
        # MAIN STATE
        # ====================================================

        self.state = "MOVING"

        # ====================================================
        # INSPECTION
        # ====================================================

        self.inspection_result = "NOT INSPECTED"

        # ====================================================
        # FILLING
        # ====================================================

        self.fill_time = 0
        self.fill_duration = 45

        # ====================================================
        # UNDERFILL REWORK
        # ====================================================

        self.missing_pills = 0
        self.rework_time = 0
        self.rework_duration = 50

        # ====================================================
        # LABEL REWORK
        # ====================================================

        self.label_rework_time = 0
        self.label_rework_duration = 50

        # ====================================================
        # OVERFILL REWORK
        # ====================================================

        self.overfill_rework_time = 0
        self.overfill_rework_duration = 50

        # ====================================================
        # REINSPECTION
        # ====================================================

        self.reinspection_count = 0

    # ========================================================
    # UPDATE
    # ========================================================

    def update(self, filling_x):

        # ----------------------------------------------------
        # MOVE TOWARD FILLING MACHINE
        # ----------------------------------------------------

        if self.state == "MOVING":

            if self.x < filling_x:

                self.x += self.speed

            else:

                self.state = "FILLING"
                self.fill_time = 0

        # ----------------------------------------------------
        # FILLING
        # ----------------------------------------------------

        elif self.state == "FILLING":

            self.fill_time += 1

            if self.fill_time >= self.fill_duration:

                # --------------------------------------------
                # SIMULATE PILL FILLING
                # --------------------------------------------

                roll = random.randint(1, 100)

                if roll <= 80:

                    # Normal fill
                    self.pill_count = 100

                elif roll <= 95:

                    # Underfill
                    self.pill_count = random.randint(95, 99)

                else:

                    # Overfill
                    self.pill_count = random.randint(101, 105)

                # --------------------------------------------
                # SIMULATE LABEL
                # --------------------------------------------

                label_roll = random.randint(1, 100)

                if label_roll <= 90:

                    self.actual_label = self.expected_label

                else:

                    self.actual_label = "WRONG-LABEL"

                self.state = "FILLED"

        # ----------------------------------------------------
        # MOVE AFTER FILLING / INSPECTION
        # ----------------------------------------------------

        elif self.state == "MOVING_AFTER_FILL":

            self.x += self.speed

        # ----------------------------------------------------
        # OUTPUT BELT
        # ----------------------------------------------------

        elif self.state == "OUTPUT":

            self.x += self.speed

        # ----------------------------------------------------
        # MOVE TO VERTICAL TRANSFER BELT
        # ----------------------------------------------------

        elif self.state == "TO_VERTICAL":

            if self.x < self.vertical_belt_x:

                self.x += self.speed

            else:

                self.x = self.vertical_belt_x

                # PASS goes directly downward to output
                if self.inspection_result == "PASS":

                    self.target_y = 490
                    self.state = "VERTICAL_TO_OUTPUT"

                # Any defect goes downward to rework
                else:

                    self.target_y = 370
                    self.state = "VERTICAL_TO_REWORK"

        # ----------------------------------------------------
        # VERTICAL BELT → OUTPUT
        # ----------------------------------------------------

        elif self.state == "VERTICAL_TO_OUTPUT":

            if self.y < self.target_y:

                self.y += self.vertical_speed

            else:

                self.y = self.target_y
                self.state = "OUTPUT"

        # ----------------------------------------------------
        # VERTICAL BELT → REWORK
        # ----------------------------------------------------

        elif self.state == "VERTICAL_TO_REWORK":

            if self.y < self.target_y:

                self.y += self.vertical_speed

            else:

                self.y = self.target_y

                self.target_x = self.rework_station_x

                self.state = "TO_REWORK"

        # ----------------------------------------------------
        # MOVE LEFT TO REWORK STATION
        # ----------------------------------------------------

        elif self.state == "TO_REWORK":

            if self.x > self.target_x:

                self.x -= self.speed

            else:

                self.x = self.target_x
                self.state = "REWORK"

        # ----------------------------------------------------
        # RETURN FROM REWORK → VERTICAL BELT
        # ----------------------------------------------------

        elif self.state == "RETURN_FROM_REWORK":

            if self.x < self.vertical_belt_x:

                self.x += self.speed

            else:

                self.x = self.vertical_belt_x

                self.target_y = 490
                self.state = "VERTICAL_TO_OUTPUT"

    # ========================================================
    # CONTINUE MOVING
    # ========================================================

    def continue_moving(self):

        if self.state == "FILLED":

            self.state = "MOVING_AFTER_FILL"

    # ========================================================
    # OLD ROUTING SUPPORT
    # ========================================================

    def route_to_belt(self, target_y):

        self.target_y = target_y
        self.state = "ROUTING"

    # ========================================================
    # OLD ROUTING SUPPORT
    # ========================================================

    def move_to_route(self):

        if self.state == "ROUTING":

            step = 3

            if abs(self.y - self.target_y) <= step:

                self.y = self.target_y

                if self.target_y == 370:

                    self.state = "REWORK"

                elif self.target_y == 490:

                    self.state = "OUTPUT"

            elif self.y < self.target_y:

                self.y += step

            else:

                self.y -= step

    # ========================================================
    # NEW VERTICAL ROUTING
    # ========================================================

    def route_via_vertical(self):

        self.target_x = self.vertical_belt_x
        self.state = "TO_VERTICAL"

    # ========================================================
    # START REWORK
    # ========================================================

    def start_rework(self):

        # ----------------------------------------------------
        # UNDERFILL / MISSING PILLS
        # ----------------------------------------------------

        if self.inspection_result == "DEFECT":

            self.missing_pills = (
                self.expected_pills - self.pill_count
            )

            self.rework_time = 0
            self.state = "REWORKING"

        # ----------------------------------------------------
        # WRONG LABEL
        # ----------------------------------------------------

        elif self.inspection_result == "WRONG LABEL":

            self.label_rework_time = 0
            self.state = "LABEL_REWORK"

        # ----------------------------------------------------
        # OVERFILL
        # ----------------------------------------------------

        elif self.inspection_result == "OVERFILL":

            self.overfill_rework_time = 0
            self.state = "OVERFILL_REWORK"

    # ========================================================
    # UNDERFILL REWORK
    # ========================================================

    def perform_rework(self):

        if self.state != "REWORKING":

            return

        self.rework_time += 1

        if self.rework_time >= self.rework_duration:

            # Add only the missing pills
            self.pill_count += self.missing_pills

            self.missing_pills = 0

            self.reinspection_count += 1

            self.state = "REINSPECTION"

    # ========================================================
    # LABEL REWORK
    # ========================================================

    def perform_label_rework(self):

        if self.state != "LABEL_REWORK":

            return

        self.label_rework_time += 1

        if self.label_rework_time >= self.label_rework_duration:

            # Fix the physical label
            self.actual_label = self.expected_label

            self.reinspection_count += 1

            # Send to label reinspection
            self.state = "LABEL_REINSPECTION"

    # ========================================================
    # OVERFILL REWORK
    # ========================================================

    def perform_overfill_rework(self):

        if self.state != "OVERFILL_REWORK":

            return

        self.overfill_rework_time += 1

        if self.overfill_rework_time >= self.overfill_rework_duration:

            # Remove excess pills
            self.pill_count = self.expected_pills

            self.reinspection_count += 1

            # Send to normal reinspection
            self.state = "REINSPECTION"

    # ========================================================
    # RETURN TO OUTPUT
    # ========================================================

    def return_from_rework(self):

        self.target_x = self.vertical_belt_x

        self.state = "RETURN_FROM_REWORK"

    # ========================================================
    # DRAW BOTTLE
    # ========================================================

    def draw(self, screen, font):

        # ----------------------------------------------------
        # BOTTLE BODY
        # ----------------------------------------------------

        body = pygame.Rect(
            int(self.x),
            int(self.y),
            self.width,
            self.height
        )

        pygame.draw.rect(
            screen,
            (220, 225, 230),
            body,
            border_radius=5
        )

        # ----------------------------------------------------
        # CAP
        # ----------------------------------------------------

        cap = pygame.Rect(
            int(self.x + 5),
            int(self.y - 6),
            20,
            7
        )

        pygame.draw.rect(
            screen,
            (160, 165, 170),
            cap,
            border_radius=2
        )

        # ----------------------------------------------------
        # LABEL
        # ----------------------------------------------------

        label = pygame.Rect(
            int(self.x + 3),
            int(self.y + 17),
            24,
            14
        )

        pygame.draw.rect(
            screen,
            (245, 245, 245),
            label
        )

        pygame.draw.rect(
            screen,
            (80, 80, 90),
            label,
            1
        )

        label_text = font.render(
            "A",
            True,
            (30, 30, 30)
        )

        screen.blit(
            label_text,
            (
                int(self.x + 11),
                int(self.y + 18)
            )
        )

        # ----------------------------------------------------
        # INSPECTION RESULT
        # ----------------------------------------------------

        if self.inspection_result == "PASS":

            result_color = (70, 220, 100)

        elif self.inspection_result in [
            "DEFECT",
            "WRONG LABEL"
        ]:

            result_color = (240, 70, 70)

        elif self.inspection_result == "OVERFILL":

            result_color = (255, 170, 50)

        else:

            result_color = (190, 190, 200)

        result_text = font.render(
            self.inspection_result,
            True,
            result_color
        )

        screen.blit(
            result_text,
            (
                int(self.x - 15),
                int(self.y - 27)
            )
        )

        # ----------------------------------------------------
        # PILL COUNT
        # ----------------------------------------------------

        if self.pill_count > 0:

            pill_text = font.render(
                str(self.pill_count),
                True,
                (255, 255, 255)
            )

            screen.blit(
                pill_text,
                (
                    int(self.x + 35),
                    int(self.y + 15)
                )
            )