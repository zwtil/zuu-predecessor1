from time import sleep
import pyautogui
import click
import pygetwindow as gw
import re

def read_text_from_file(path, slice_):
    with open(path, 'r') as file:
        text = file.read()
    return eval(f"text{slice_}", {'text': text})

def apply_slice(text, slice_):
    return eval(f"text{slice_}", {'text': text})

@click.command()
@click.option('-f', '--file', type=click.Path(exists=True), help="Read input text from a file.")
@click.option('-s', '--segment', default='[:]', help="Apply slicing to text input (e.g., [1:-1], [::-1]).")
@click.option('-d', '--delay', type=int, default=1, help="Delay before typing starts.")
@click.option('--interval', type=int, default=0.1, help="Interval between key presses.")
@click.option('-owc', '--on-window-change', is_flag=True, help="Trigger only on window change.")
@click.option('-own', '--own-name', type=str, help="Specify window name to focus.")
@click.option('-owt', '--own-title', type=str, help="Specify window title (supports regex).")
@click.argument('text', default='', required=False)
def main(file, segment, delay, interval, on_window_change, own_name, own_title, text):
    if file:
        text = read_text_from_file(file, segment)
    elif text:
        text = apply_slice(text, segment)
    
    target_window = None
    if own_name:
        windows = gw.getWindowsWithTitle(own_name)
        if windows:
            target_window = windows[0]
    elif own_title:
        regex = re.compile(own_title)
        for window in gw.getAllWindows():
            if regex.search(window.title):
                target_window = window
                break

    last_active_title = None
    while True:
        if on_window_change:
            active_window = gw.getActiveWindow()
            if not active_window or active_window.title == last_active_title:
                sleep(1)
                continue
            last_active_title = active_window.title
        
        if target_window:
            while not target_window.isActive:
                sleep(1)
        
        if delay:
            sleep(delay)

        pyautogui.typewrite(text, interval=interval)
        break  # Remove or modify this line based on whether you want to keep re-triggering.

def run():
    """
    a typewriter
    """
    main()

if __name__ == "__main__":
    run()