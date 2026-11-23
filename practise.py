from blessed import Terminal

term = Terminal()
dt = 1/30

text = "Hello"
colors = [term.yellow, term.bold_cyan, term.bright_red, term.green]
color_index = 0

with term.fullscreen(), term.cbreak(), term.hidden_cursor():
    x = 5.0
    y = 3.0
    vx = 20.0
    vy = 8.0

    while True:
        frame = term.home + term.clean
        hud = f"x={x:6.2f} space - colour. q - exit"
        frame += term.move_xy(0,0) + hud
        paint = colors[color_index]
        frame += term.move_xy(round(x), round(y)) + paint(text)
        print(frame, end="", flush=True)

        key = term.inkey(timeout=dt)
        if key == 'q':
            break
        elif key == ' ':
            color_index = (color_index + 1) % len(colors)

        x += vx * dt
        y += vy * dt

        right = term.width - len(text)
        bottom = term.height - 2
        if x <= 0 or x >= right:
            if color_index >= len(colors):
                color_index = 0
            color_index +=1
            vx = -vx
        if y <= 1 or y >= bottom:
            if color_index >= len(colors):
                color_index = 0
            color_index += 1
            vy = -vy
        x = max(0, min(x, right))
        y = max(1, min(y, bottom))
