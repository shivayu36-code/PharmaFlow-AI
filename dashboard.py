import pygame


def draw_dashboard(
    screen,
    stats,
    status,
    last_event,
    font
):

    panel = pygame.Rect(
        10,
        10,
        780,
        105
    )

    pygame.draw.rect(
        screen,
        (42, 44, 54),
        panel,
        border_radius=8
    )

    pygame.draw.rect(
        screen,
        (90, 92, 105),
        panel,
        2,
        border_radius=8
    )

    title = font.render(
        "PHARMAFLOW AI - AUTONOMOUS PRODUCTION MONITOR",
        True,
        (255, 255, 255)
    )

    screen.blit(
        title,
        (22, 18)
    )

    if status == "RUNNING":

        status_color = (70, 220, 100)

    elif status == "CRITICAL":

        status_color = (240, 70, 70)

    elif status == "PAUSED":

        status_color = (190, 190, 200)

    else:

        status_color = (255, 190, 60)

    status_text = font.render(
        "STATUS: " + status,
        True,
        status_color
    )

    screen.blit(
        status_text,
        (650, 18)
    )

    stats_list = [

        "Produced: " +
        str(stats["produced"]),

        "PASS: " +
        str(stats["pass"]),

        "Defect: " +
        str(stats["defect"]),

        "Wrong Label: " +
        str(stats["wrong_label"]),

        "Overfill: " +
        str(stats["overfill"]),

        "Recovered: " +
        str(stats["recovered"])
    ]

    x = 22

    for stat in stats_list:

        text = font.render(
            stat,
            True,
            (235, 235, 240)
        )

        screen.blit(
            text,
            (x, 48)
        )

        x += 125

    event_text = font.render(
        "EVENT: " + last_event[:90],
        True,
        (190, 210, 230)
    )

    screen.blit(
        event_text,
        (22, 82)
    )


def draw_controls(screen, font):

    controls = font.render(
        "SPACE = Pause/Resume    R = Reset    M = Machine Alarm",
        True,
        (190, 190, 200)
    )

    screen.blit(
        controls,
        (22, 570)
    )