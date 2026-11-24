from blessed import Terminal
import time

term = Terminal()

g = 9.81
dt = 1 / 30 # Time of each frame

mass = 1000 # kg
max_thrust = 3 # g
throttle = 0
throttle_change = 0.1
throttle_message = ""
max_landing_v = 10

message = ""
message_timer = 0

fuel_cons = 14
fuel = 100

with term.fullscreen(), term.cbreak(), term.hidden_cursor():
    x = term.width // 2
    y = 1.0
    v = 0.0


    while True:
        frame_start = time.monotonic()


        # Drawing frame
        frame = term.home + term.clear

        # HUD
        frame += term.move_xy(0, 0) + term.bold_cyan(f"HOVERSLAM  v={v:5.2f}  q - exit r - restart. Throttle: {throttle_message}") + f' x: {x} y: {y:.2f} v: {v:.2f} fuel: {fuel:.2f}'
        bottom = term.height -1

        # Landing pad
        frame += term.move_xy(10, bottom) + term.bold_cyan("******")

        # Rocket
        frame += term.move_xy(x, round(y)) + term.yellow("#")
        frame += term.move_xy(0, 1) + term.bold_cyan(message)
        print(frame, end="", flush=True)

        # Keys
        key = term.inkey(timeout=dt)

        if key == "q":
            break
        if key == "r":
            x = term.width // 2
            y = 1.0
            v = 0.0
            throttle = 0.0
        if key == "a": x -= 1
        if key == "d": x += 1
        if key == "w":
            throttle += throttle_change
            if len(throttle_message) != 5:
                throttle_message += "█"
            if throttle > 1:
                throttle = 1


        if key == "s":
            throttle -= throttle_change
            throttle_message = throttle_message[:-1]
            if throttle <= 0:
                throttle = 0

        # Physics
        fuel -= fuel_cons * throttle * dt

        a_t = throttle * max_thrust * g
        a_net = g - a_t
        v += a_net * dt
        y += v*dt

        f_g = mass*g

        if message_timer > 0:
                    message_timer -= dt
                    if message_timer <= 0:
                        message = ""

        # Landing on pad
        if round(y) >= bottom - 1:
            if 10 <= x <= 15:
                if v <= max_landing_v:
                    message = "Landing successful"
                    message_timer = 2
                    x = term.width // 2
                    y = 1.0
                    v = 0.0
                    throttle = 0.0
                    fuel = 100

        # Out of bound exceptions
        if y >= term.height - 1:
            message = "You crashed"
            message_timer = 2
            x = term.width // 2
            y = 1.0
            v = 0.0
            throttle = 0.0
            fuel = 100
        if x < 0 or x > term.width - 1:
            message = "Out of bound"
            message_timer = 2
            x = term.width // 2
            y = 1.0
            v = 0.0
            throttle = 0.0
            fuel = 100
        if y < 0:
            message = "Out of bound (top)"
            message_timer = 2
            x = term.width // 2
            y = 1.0
            v = 0.0
            throttle = 0.0
            fuel = 100

        elapsed = time.monotonic() - frame_start
        if elapsed < dt:
            time.sleep(dt - elapsed)
