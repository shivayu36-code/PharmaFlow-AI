import pygame
import sys

from bottle import Bottle
from sensors import PillCountSensor, LabelSensor
from ai_engine import AIEngine
from factory import FactoryRouter
from recovery import RecoverySystem
from events import EventLogger
from dashboard import draw_dashboard, draw_controls


# ============================================================
# PHARMAFLOW AI
# SENSES -> DECIDES -> ACTS -> RECOVERS -> REPORTS
# ============================================================

pygame.init()


# ============================================================
# SCREEN
# ============================================================

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600

screen = pygame.display.set_mode(
    (SCREEN_WIDTH, SCREEN_HEIGHT)
)

pygame.display.set_caption(
    "PharmaFlow AI - Autonomous Pharmaceutical Packaging"
)

clock = pygame.time.Clock()


# ============================================================
# FONTS
# ============================================================

font = pygame.font.Font(None, 22)
small_font = pygame.font.Font(None, 18)
station_font = pygame.font.Font(None, 20)


# ============================================================
# COLORS
# ============================================================

BG_COLOR = (30, 30, 40)
BELT_COLOR = (100, 100, 110)
BELT_EDGE = (150, 150, 160)

WHITE = (245, 245, 245)
GREEN = (70, 220, 100)
YELLOW = (255, 190, 60)
RED = (240, 70, 70)


# ============================================================
# FACTORY LAYOUT
# ============================================================

belt_height = 40

main_belt_y = 250
defect_belt_y = 370
output_belt_y = 490

vertical_belt_x = 700
vertical_belt_width = 35

filling_machine_x = 350
bottle_y = main_belt_y + 10


# ============================================================
# SYSTEMS
# ============================================================

pill_sensor = PillCountSensor()
label_sensor = LabelSensor()

ai_engine = AIEngine()

factory_router = FactoryRouter()

recovery_system = RecoverySystem()

logger = EventLogger()


# ============================================================
# BOTTLES
# ============================================================

bottles = []

next_bottle_id = 1001

bottle_spawn_timer = 0
bottle_spawn_delay = 110


# ============================================================
# STATISTICS
# ============================================================

stats = {

    "produced": 0,
    "pass": 0,
    "defect": 0,
    "wrong_label": 0,
    "overfill": 0,
    "recovered": 0
}


# ============================================================
# SYSTEM STATUS
# ============================================================

last_event = (
    "System initialized. Waiting for production..."
)

machine_issue = False
machine_issue_timer = 0

paused = False


# ============================================================
# DRAW BELT
# ============================================================

def draw_belt(y):

    pygame.draw.rect(
        screen,
        BELT_COLOR,
        (0, y, SCREEN_WIDTH, belt_height)
    )

    pygame.draw.line(
        screen,
        BELT_EDGE,
        (0, y),
        (SCREEN_WIDTH, y),
        2
    )

    pygame.draw.line(
        screen,
        BELT_EDGE,
        (0, y + belt_height),
        (SCREEN_WIDTH, y + belt_height),
        2
    )

    for x in range(0, SCREEN_WIDTH, 45):

        pygame.draw.line(
            screen,
            (125, 125, 135),
            (x, y + 8),
            (x + 18, y + 20),
            2
        )

        pygame.draw.line(
            screen,
            (125, 125, 135),
            (x + 18, y + 20),
            (x, y + 32),
            2
        )


# ============================================================
# DRAW STATIONS
# ============================================================

def draw_station(
    x,
    y,
    width,
    height,
    title,
    subtitle,
    status_color=GREEN
):

    rect = pygame.Rect(
        x,
        y,
        width,
        height
    )

    pygame.draw.rect(
        screen,
        (48, 50, 60),
        rect,
        border_radius=7
    )

    pygame.draw.rect(
        screen,
        status_color,
        rect,
        2,
        border_radius=7
    )

    title_text = station_font.render(
        title,
        True,
        WHITE
    )

    screen.blit(
        title_text,
        (x + 8, y + 8)
    )

    subtitle_text = small_font.render(
        subtitle,
        True,
        (185, 185, 195)
    )

    screen.blit(
        subtitle_text,
        (x + 8, y + 31)
    )


# ============================================================
# DRAW FACTORY
# ============================================================

def draw_factory():

    # --------------------------------------------------------
    # HORIZONTAL BELTS
    # --------------------------------------------------------

    draw_belt(main_belt_y)

    draw_belt(defect_belt_y)

    draw_belt(output_belt_y)

    # --------------------------------------------------------
    # VERTICAL TRANSFER BELT
    # --------------------------------------------------------

    pygame.draw.rect(
        screen,
        BELT_COLOR,
        (
            vertical_belt_x,
            main_belt_y,
            vertical_belt_width,
            output_belt_y - main_belt_y + belt_height
        )
    )

    pygame.draw.rect(
        screen,
        BELT_EDGE,
        (
            vertical_belt_x,
            main_belt_y,
            vertical_belt_width,
            output_belt_y - main_belt_y + belt_height
        ),
        2
    )

    # --------------------------------------------------------
    # VERTICAL BELT MOVEMENT LINES
    # --------------------------------------------------------

    for y in range(
        main_belt_y + 5,
        output_belt_y + belt_height,
        25
    ):

        pygame.draw.line(
            screen,
            (125, 125, 135),
            (
                vertical_belt_x + 7,
                y
            ),
            (
                vertical_belt_x + 28,
                y + 12
            ),
            2
        )

    # --------------------------------------------------------
    # STATIONS
    # --------------------------------------------------------

    draw_station(
        45,
        165,
        130,
        65,
        "BOTTLE INPUT",
        "Supply"
    )

    draw_station(
        300,
        165,
        145,
        65,
        "FILLING",
        "100 pills target",
        RED if machine_issue else GREEN
    )

    draw_station(
        515,
        165,
        160,
        65,
        "AI INSPECTION",
        "Pills + Label"
    )

    draw_station(
        45,
        300,
        145,
        55,
        "REWORK",
        "Auto recovery",
        YELLOW
    )

    draw_station(
        520,
        300,
        150,
        55,
        "OUTPUT",
        "Approved",
        GREEN
    )

    # --------------------------------------------------------
    # FILLING MACHINE
    # --------------------------------------------------------

    machine = pygame.Rect(
        filling_machine_x - 20,
        main_belt_y - 35,
        75,
        35
    )

    pygame.draw.rect(
        screen,
        (70, 75, 85),
        machine,
        border_radius=6
    )

    pygame.draw.rect(
        screen,
        RED if machine_issue else GREEN,
        machine,
        3,
        border_radius=6
    )

    machine_text = small_font.render(
        "MACHINE ERROR"
        if machine_issue
        else "FILLER READY",
        True,
        RED if machine_issue else GREEN
    )

    screen.blit(
        machine_text,
        (
            filling_machine_x - 15,
            main_belt_y - 27
        )
    )

    # --------------------------------------------------------
    # BELT LABELS
    # --------------------------------------------------------

    labels = [

        (
            "MAIN PRODUCTION BELT",
            15,
            main_belt_y + 12
        ),

        (
            "DEFECT / REWORK BELT",
            15,
            defect_belt_y + 12
        ),

        (
            "APPROVED OUTPUT BELT",
            15,
            output_belt_y + 12
        )
    ]

    for text, x, y in labels:

        label = small_font.render(
            text,
            True,
            (170, 170, 180)
        )

        screen.blit(
            label,
            (x, y)
        )


# ============================================================
# INSPECTION
# ============================================================

def inspect_bottle(bottle):

    global last_event

    # --------------------------------------------------------
    # PILL SENSOR
    # --------------------------------------------------------

    detected_pills = pill_sensor.inspect(
        bottle
    )

    # --------------------------------------------------------
    # LABEL SENSOR
    # --------------------------------------------------------

    detected_label = label_sensor.inspect(
        bottle
    )

    # --------------------------------------------------------
    # AI DECISION
    # --------------------------------------------------------

    decision = ai_engine.final_decision(

        detected_pills,

        bottle.expected_pills,

        detected_label,

        bottle.expected_label
    )

    bottle.inspection_result = decision

    # --------------------------------------------------------
    # PASS
    # --------------------------------------------------------

    if decision == "PASS":

        stats["pass"] += 1

        bottle.route_via_vertical()

        last_event = (
            f"Bottle {bottle.bottle_id}: "
            f"PASS - 100 pills + correct label"
        )

        logger.log(
            "INSPECTION",
            bottle.bottle_id,
            last_event,
            decision
        )

    # --------------------------------------------------------
    # UNDERFILL
    # --------------------------------------------------------

    elif decision == "DEFECT":

        stats["defect"] += 1

        bottle.route_via_vertical()

        missing = (
            bottle.expected_pills
            - detected_pills
        )

        last_event = (
            f"Bottle {bottle.bottle_id}: "
            f"DEFECT - {detected_pills}/"
            f"{bottle.expected_pills} pills "
            f"({missing} missing)"
        )

        logger.log(
            "INSPECTION",
            bottle.bottle_id,
            last_event,
            decision
        )

    # --------------------------------------------------------
    # WRONG LABEL
    # --------------------------------------------------------

    elif decision == "WRONG LABEL":

        stats["wrong_label"] += 1

        bottle.route_via_vertical()

        last_event = (
            f"Bottle {bottle.bottle_id}: "
            f"WRONG LABEL detected"
        )

        logger.log(
            "INSPECTION",
            bottle.bottle_id,
            last_event,
            decision
        )

    # --------------------------------------------------------
    # OVERFILL
    # --------------------------------------------------------

    elif decision == "OVERFILL":

        stats["overfill"] += 1

        bottle.route_via_vertical()

        last_event = (
            f"Bottle {bottle.bottle_id}: "
            f"OVERFILL - {detected_pills} pills"
        )

        logger.log(
            "INSPECTION",
            bottle.bottle_id,
            last_event,
            decision
        )

    bottle.continue_moving()


# ============================================================
# RECOVERY
# ============================================================

def process_recovery(bottle):

    global last_event

    # --------------------------------------------------------
    # ARRIVED AT REWORK
    # --------------------------------------------------------

    if bottle.state == "REWORK":

        bottle.start_rework()

        return

    # --------------------------------------------------------
    # UNDERFILL REPAIR
    # --------------------------------------------------------

    if bottle.state == "REWORKING":

        bottle.perform_rework()

        return

    # --------------------------------------------------------
    # WRONG LABEL REPAIR
    # --------------------------------------------------------

    if bottle.state == "LABEL_REWORK":

        bottle.perform_label_rework()

        return

    # --------------------------------------------------------
    # OVERFILL REPAIR
    # --------------------------------------------------------

    if bottle.state == "OVERFILL_REWORK":

        bottle.perform_overfill_rework()

        return

    # --------------------------------------------------------
    # PILL / OVERFILL RE-INSPECTION
    # --------------------------------------------------------

    if bottle.state == "REINSPECTION":

        detected_pills = pill_sensor.inspect(
            bottle
        )

        detected_label = label_sensor.inspect(
            bottle
        )

        decision = ai_engine.final_decision(

            detected_pills,

            bottle.expected_pills,

            detected_label,

            bottle.expected_label
        )

        bottle.inspection_result = decision

        # ----------------------------------------------------
        # REPAIR SUCCESS
        # ----------------------------------------------------

        if decision == "PASS":

            bottle.inspection_result = "PASS"

            bottle.return_from_rework()

            stats["recovered"] += 1

            last_event = (
                f"Bottle {bottle.bottle_id}: "
                f"REWORK SUCCESS - PASS"
            )

            recovery_system.recover_bottle(
                bottle
            )

            logger.log(
                "RECOVERY",
                bottle.bottle_id,
                last_event,
                "PASS"
            )

        # ----------------------------------------------------
        # REPAIR FAILED
        # ----------------------------------------------------

        else:

            bottle.state = "REWORK"

            last_event = (
                f"Bottle {bottle.bottle_id}: "
                f"REWORK FAILED - "
                f"RETURNING TO REWORK"
            )

        return

    # --------------------------------------------------------
    # LABEL RE-INSPECTION
    # --------------------------------------------------------

    if bottle.state == "LABEL_REINSPECTION":

        detected_label = label_sensor.inspect(
            bottle
        )

        if detected_label == bottle.expected_label:

            bottle.actual_label = (
                bottle.expected_label
            )

            bottle.inspection_result = "PASS"

            bottle.return_from_rework()

            stats["recovered"] += 1

            last_event = (
                f"Bottle {bottle.bottle_id}: "
                f"LABEL FIXED - PASS"
            )

            recovery_system.recover_bottle(
                bottle
            )

            logger.log(
                "RECOVERY",
                bottle.bottle_id,
                last_event,
                "PASS"
            )

        else:

            bottle.state = "REWORK"

            last_event = (
                f"Bottle {bottle.bottle_id}: "
                f"LABEL REPAIR FAILED - "
                f"RETURNING TO REWORK"
            )

        return


# ============================================================
# MACHINE ALARM
# ============================================================

def simulate_machine_issue():

    global machine_issue
    global machine_issue_timer
    global last_event

    if not machine_issue:

        machine_issue = True

        machine_issue_timer = 180

        last_event = (
            "ALARM: Filling machine malfunction detected!"
        )

        logger.log(
            "ALARM",
            0,
            last_event,
            "CRITICAL"
        )


# ============================================================
# RESET
# ============================================================

def reset_stats():

    global last_event

    for key in stats:

        stats[key] = 0

    last_event = (
        "Dashboard counters reset."
    )


# ============================================================
# MAIN LOOP
# ============================================================

running = True

while running:

    # ========================================================
    # EVENTS
    # ========================================================

    for event in pygame.event.get():

        if event.type == pygame.QUIT:

            running = False

        elif event.type == pygame.KEYDOWN:

            # ------------------------------------------------
            # PAUSE
            # ------------------------------------------------

            if event.key == pygame.K_SPACE:

                paused = not paused

                if paused:

                    last_event = (
                        "Production PAUSED."
                    )

                else:

                    last_event = (
                        "Production RESUMED."
                    )

            # ------------------------------------------------
            # RESET
            # ------------------------------------------------

            elif event.key == pygame.K_r:

                reset_stats()

            # ------------------------------------------------
            # MACHINE MALFUNCTION
            # ------------------------------------------------

            elif event.key == pygame.K_m:

                simulate_machine_issue()

    # ========================================================
    # UPDATE FACTORY
    # ========================================================

    if not paused:

        # ----------------------------------------------------
        # MACHINE RECOVERY TIMER
        # ----------------------------------------------------

        if machine_issue:

            machine_issue_timer -= 1

            if machine_issue_timer <= 0:

                machine_issue = False

                last_event = (
                    "Filling machine tested "
                    "and recovered. Alarm GREEN."
                )

                logger.log(
                    "RECOVERY",
                    0,
                    last_event,
                    "PASS"
                )

        # ----------------------------------------------------
        # SPAWN BOTTLE
        # ----------------------------------------------------

        bottle_spawn_timer += 1

        if bottle_spawn_timer >= bottle_spawn_delay:

            new_bottle = Bottle(
                next_bottle_id,
                -40,
                bottle_y
            )

            bottles.append(
                new_bottle
            )

            next_bottle_id += 1

            bottle_spawn_timer = 0

            stats["produced"] += 1

            logger.log(
                "PRODUCTION",
                new_bottle.bottle_id,
                (
                    f"Bottle "
                    f"{new_bottle.bottle_id} "
                    f"entered production."
                ),
                "START"
            )

        # ----------------------------------------------------
        # UPDATE BOTTLES
        # ----------------------------------------------------

        for bottle in bottles[:]:

            # -----------------------------------------------
            # MACHINE MALFUNCTION PAUSES FILLING
            # -----------------------------------------------

            if (
                machine_issue
                and bottle.state == "FILLING"
            ):

                continue

            # -----------------------------------------------
            # NORMAL BOTTLE UPDATE
            # -----------------------------------------------

            bottle.update(
                filling_machine_x
            )

            # -----------------------------------------------
            # INSPECTION
            # -----------------------------------------------

            if bottle.state == "FILLED":

                inspect_bottle(
                    bottle
                )

            # -----------------------------------------------
            # OLD ROUTING SUPPORT
            # -----------------------------------------------

            if bottle.state == "ROUTING":

                bottle.move_to_route()

            # -----------------------------------------------
            # RECOVERY
            #
            # IMPORTANT:
            # Every recovery state is included here.
            # -----------------------------------------------

            if bottle.state in [

                "REWORK",

                "REWORKING",

                "LABEL_REWORK",

                "OVERFILL_REWORK",

                "LABEL_REINSPECTION",

                "REINSPECTION"

            ]:

                process_recovery(
                    bottle
                )

            # -----------------------------------------------
            # REMOVE FINISHED BOTTLES
            # -----------------------------------------------

            if bottle.x > SCREEN_WIDTH + 60:

                bottles.remove(
                    bottle
                )

    # ========================================================
    # DRAW
    # ========================================================

    screen.fill(
        BG_COLOR
    )

    draw_factory()

    # --------------------------------------------------------
    # DRAW BOTTLES
    # --------------------------------------------------------

    for bottle in bottles:

        bottle.draw(
            screen,
            font
        )

    # --------------------------------------------------------
    # STATUS
    # --------------------------------------------------------

    if paused:

        status = "PAUSED"

    elif machine_issue:

        status = "CRITICAL"

    else:

        status = "RUNNING"

    # --------------------------------------------------------
    # DASHBOARD
    # --------------------------------------------------------

    draw_dashboard(
        screen,
        stats,
        status,
        last_event,
        font
    )

    # --------------------------------------------------------
    # ALARM
    # --------------------------------------------------------

    if machine_issue:

        alarm = font.render(
            "FILLING MACHINE ALARM - RECOVERY IN PROGRESS",
            True,
            RED
        )

        screen.blit(
            alarm,
            (175, 125)
        )

    # --------------------------------------------------------
    # CONTROLS
    # --------------------------------------------------------

    draw_controls(
        screen,
        small_font
    )

    # --------------------------------------------------------
    # DISPLAY
    # --------------------------------------------------------

    pygame.display.flip()

    clock.tick(60)


# ============================================================
# EXIT
# ============================================================

pygame.quit()
sys.exit()
