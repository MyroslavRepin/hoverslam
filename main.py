from blessed import Terminal

term = Terminal()

g = 9.81
dt = 1 / 30 # Time of each frame

mass = 1000 # kg
max_thrust = 3 # g
throttle = 0
throttle_change = 0.1


with term.fullscreen(), term.cbreak(), term.hidden_cursor():
    x = term.width // 2
    y = 1.0
    v = 0.0


    while True:
        # Drawing frame
        frame = term.home + term.clear
        frame += term.move_xy(0, 0) + term.bold_cyan(f"HOVERSLAM  v={v:5.2f}  q - exit r - restart. Throttle: {throttle:.2f}")
        bottom = term.height -1
        frame += term.move_xy(10, bottom) + term.bold_cyan("******")
        frame += term.move_xy(x, round(y)) + term.yellow("#")
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
            if throttle > 1:
                throttle = 1
        if key == "s":
            throttle -= throttle_change
            if throttle <= 0:
                throttle = 0

        # Physics
        a_t = throttle * max_thrust * g
        a_net = g-a_t
        v += a_net * dt
        y += v*dt

        f_g = mass*g


        if y >= term.height - 1:
            x = term.width // 2
            y = 1.0
            v = 0.0
            throttle = 0.0
