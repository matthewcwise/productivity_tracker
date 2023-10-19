mouse_count = 0
key_count = 0

from pynput import keyboard
from pynput import mouse

def on_press(key):
    global key_count
    key_count +=1
    try:
        print(f"alphanumeric key {key} pressed, tally: {key_count}")
    except AttributeError:
        print(f"special key {key} pressed, tally: {key_count}")


def on_click(x, y, button, pressed):
    global mouse_count
    mouse_count +=1
    try:
        print(f"Mouse: {pressed}. Mouse tally: {mouse_count}")
    except AttributeError:
        print(AttributeError)

def on_scroll(x, y, dx, dy):
    global mouse_count
    mouse_count +=1
    try:
        print(f"Mouse: scrolled. Mouse tally: {mouse_count}")
    except AttributeError:
        print(AttributeError)

# Collect events in a non-blocking fashion:

# ...or, in a non-blocking fashion:
keyboard_listener = keyboard.Listener(on_press=on_press)
keyboard_listener.start()


mouse_listener = mouse.Listener(
    on_click=on_click,
    on_scroll=on_scroll)
mouse_listener.start()

try:
    while True:
        continue

except KeyboardInterrupt:  # Graceful exit on Ctrl+C
    # Clean up and exit
    # mouse_listener.stop()
    keyboard_listener.stop()
    mouse_listener.stop()
    print("Logging stopped by user.")
except Exception as e:
    print(f"An unexpected error occurred: {str(e)}")
