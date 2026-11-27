from blessed import Terminal
import time
import pyfiglet

term = Terminal()
banner = pyfiglet.figlet_format("SYSTEM READY", font="small")
lines = banner.splitlines()

g = 9.81
dt = 1 / 30 # Time of each frame

mass = 1000 # kg
max_thrust = 3 # g
throttle = 0
throttle_change = 0.1
throttle_message = "░" * 10
fuel_message = "█" * 10
max_landing_v = 10
state = "playing"

message = ""
message_timer = 0

fuel_cons = 14
fuel = 100
fuel_steps = []
for i in range(10):
    fuel_steps.append(i)


def draw_box(text, color, side_padding=11, vertical_padding=1):
    text_lines = text.split("\n")

    longest = 0
    for line in text_lines:
        if len(line) > longest:
            longest = len(line)

    box_width = longest + 2 + 2 * side_padding
    box_height = 2 + len(text_lines) + 2 * vertical_padding
    box_left = (term.width - box_width) // 2
    box_top = (term.height - box_height) // 2

    top_border = "┌" + "─" * (box_width - 2) + "┐"
    empty_line = "│" + " " * (box_width - 2) + "│"
    bottom_border = "└" + "─" * (box_width - 2) + "┘"

    text_box_lines = []
    for line in text_lines:
        text_box_lines.append("│" + " " * side_padding + line.center(longest) + " " * side_padding + "│")

    box_lines = ([top_border] + [empty_line] * vertical_padding + text_box_lines
                 + [empty_line] * vertical_padding + [bottom_border])

    out = ""
    for i, line in enumerate(box_lines):
        out += term.move_xy(box_left, box_top + i) + color(line)
    return out

with term.fullscreen(), term.cbreak(), term.hidden_cursor():
    x = term.width // 2
    alt = term.height - 4
    v = 0.0

    # Welcome screen
    welcome_screen = True
    while welcome_screen:
        frame = term.home + term.clear
        title_asci = pyfiglet.figlet_format("Hoverslam", font="ansi_shadow")
        lines = title_asci.splitlines()

        width = 0
        for line in lines:
            if len(line) > width:
                width = len(line)

        x0 = (term.width - width) // 2
        y0 = 10

        for i, line in enumerate(lines):
            frame += term.move_xy(x0, y0 + i) + term.bold_cyan(line)
        frame += term.move_xy(0, y0 + len(lines) + 1) + term.bright_black(term.center("land a rocket using *real physics"))
        frame += term.move_xy(0, y0 + len(lines) + 3) + term.bold_cyan(term.center("< Press any key to start playing >"))

        print(frame, end="", flush=True)
        key = term.inkey(timeout=dt)
        if key == 'q':
            exit()
        if key:
            break

    def restart():
        global message_timer, throttle_message, x, alt, v, throttle, fuel, state
        throttle_message = "░" * 10
        message_timer = 2
        x = term.width // 2
        alt = term.height - 4
        v = 0.0
        throttle = 0.0
        fuel = 100
        state = "playing"


    while True:
        frame_start = time.monotonic()
        bottom = term.height -1
        ground_row = bottom - 2

        # Drawing frame
        frame = term.home + term.clear

        fuel_message = ""
        if fuel > 50:
            fuel_color = term.bold_cyan
        elif fuel > 20:
            fuel_color = term.bold_yellow
        else:
            fuel_color = term.bold_red

        if abs(v) > max_landing_v:
            velocity_color = term.bold_red
        else:
            velocity_color = term.bold_green

        for i in fuel_steps:
            if fuel > i * 10:
                fuel_message += "█"
            else:
                fuel_message += "░"
        # HUD
        hud = [
            term.bold_cyan("HOVERSLAM"),
            velocity_color(f"v={v:5.2f}"),
            term.bold_cyan(f"altitude: {alt:.2f}"),
            term.bold_cyan("q - exit r - restart."),
            term.bold_cyan(f"Throttle: {throttle_message}"),
            fuel_color(f"Fuel: {fuel_message}"),
        ]
        frame += term.move_xy(0, bottom) + " ".join(hud)



        frame += term.move_xy(0, bottom)
        frame += term.move_xy(0, bottom-1) + term.bold_cyan('_'*term.width)

        if state == "landed":
            frame += draw_box(f"Landing\nImpact velocity: {v:.2f}\nFuel left: {fuel:.1f}", term.bold_cyan)
        if state == "out_of_bound":
            frame += term.move_xy(0, term.height // 2) + term.green(term.center("Out of bound"))
            key = term.inkey(timeout=2)
            restart()
        if state == "crashed":
            #frame += term.move_xy(0, term.height // 2) + term.bold_red(term.center("You crashed"))
            #frame += term.move_xy(0, term.height // 2 + 2) + term.red(term.center(f"Velocity: {v:.2f}"))

            frame += draw_box(f"Crashed\nImpact velocity: {v:.2f}", term.bold_red)
            print(frame, flush=True, end=" ")
            key = term.inkey(timeout=2)
            restart()

        # Landing pad
        frame += term.move_xy(10, bottom-1) + term.bold_cyan("/▀▀▀▀▀\\")

        # Rocket
        frame += term.move_xy(x, ground_row - round(alt)) + term.yellow("#")
        frame += term.move_xy(0, 1) + term.bold_cyan(message)
        print(frame, end="", flush=True)

        # Keys
        key = term.inkey(timeout=dt)

        if key == "q":
            break
        if key == "r":
            x = term.width // 2
            restart()
        if state == "playing":
            if key == "a": x -= 1
            if key == "d": x += 1
            if key == "w":
                throttle += throttle_change
                if "░" in throttle_message:
                    throttle_message = "█" + throttle_message[:-1]
                if throttle > 1:
                    throttle = 1

            if key == "s":
                throttle -= throttle_change
                if "█" in throttle_message:
                    throttle_message = throttle_message[1:] + "░"
                if throttle <= 0:
                    throttle = 0

            if fuel <= 0:
                throttle = 0
                throttle_message = ""

            # Physics
            fuel -= fuel_cons * throttle * dt

            a_t = throttle * max_thrust * g
            a_net = a_t - g
            v += a_net * dt
            alt += v*dt

            f_g = mass*g

            if message_timer > 0:
                message_timer -= dt
                if message_timer <= 0:
                    message = ""
            if fuel <= 0:
                throttle = 0
                throttle_message = ""

            # Landing on pad
            if round(alt) <= 0: # TODO: adjust landing trigger
                if 10 <= x <= 15:
                    if abs(v) <= max_landing_v:
                        state = "landed"
                    else:
                        state = "crashed"

            # Out of bound exceptions
            if alt <= -1:
                state = "crashed"
            if x < 0 or x > term.width - 2:
                state = "out_of_bound"
            if alt > ground_row:
                state = "crashed"
            elapsed = time.monotonic() - frame_start
            if elapsed < dt:
                time.sleep(dt - elapsed)
