import keyboard
import win32gui
from ctypes import windll
import colorkey
import yaml
import zmq


#run local server
context = zmq.Context()
socket = context.socket(zmq.REP)
socket.bind("tcp://*:5555")

#create config from file
hdc = windll.user32.GetDC(0)
config = {}
CONFIG = 'config.yaml'
window_title = 'World of Warcraft'
key_1 = None
key_2 = None
x = None
y = None



def config_open(): #open config and configure
    global x, y, config, key_1, key_2
    with open(CONFIG) as f:
        config = yaml.load(f)
        key_1 = config['single_key']
        key_2 = config['aoe_key']
        x = config['x']
        y = config['y']

def single_press(): #determine the state of the game in single scenario
    if window_title in win32gui.GetWindowText(win32gui.GetForegroundWindow()):
        spec_color = windll.gdi32.GetPixel(hdc, config['x'], config['y']+5)
        target_is_enemy = windll.gdi32.GetPixel(hdc, config['x'], config['y']-5)
        key_color = windll.gdi32.GetPixel(hdc, config['x'], config['y'])
        color_mixer(spec_color, target_is_enemy, key_color)

def aoe_press(): #determine the state of the game in aoe scenario
    if  window_title in win32gui.GetWindowText(win32gui.GetForegroundWindow()):
            if windll.gdi32.GetPixel(hdc, config['x'], config['y']+10) == 65280:
                keyboard.send('5')
            else:
                spec_color = windll.gdi32.GetPixel(hdc, config['x'], config['y']+5)
                target_is_enemy = windll.gdi32.GetPixel(hdc, config['x'], config['y']-5)
                key_color = windll.gdi32.GetPixel(hdc, config['x'], config['y'])
                color_mixer(spec_color, target_is_enemy, key_color)

def color_mixer(spec_color, target_is_enemy, key_color): 
    if spec_color in colorkey.GLOBAL_DIST and target_is_enemy == 65280:
        spec = colorkey.GLOBAL_DIST[spec_color]
        if key_color in spec:
            key = spec[key_color]
            keyboard.send(key)

def start_key(key1, key2): #hotkey config
    keyboard.add_hotkey(key1, single_press, suppress=False, timeout=0.1, trigger_on_release=False)
    keyboard.add_hotkey(key2, aoe_press, suppress=False, timeout=0.1, trigger_on_release=False)



config_open()
while True:
    a = 0
    if a == 0: #start recive from socket
        start_key(config['single_key'], config['aoe_key'])
        a = 1
    message = socket.recv()
    if message == 'reset': #reset config, and start new recive cycle
        a = 0
        keyboard.unhook_all_hotkeys()
        config_open()
    else:
        pass
