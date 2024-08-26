import machine
from machine import Pin, I2C, SoftI2C
from os import listdir
from ssd1306 import SSD1306_I2C
from time import sleep
import network

# Configuración de la red Wi-Fi
ssid = 'fam'
password = '123456789'

# Configura el I2C y la pantalla OLED
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))

# Configura el LED RGB
red_pin = Pin(12, Pin.OUT)    # Pin GPIO para el color rojo
green_pin = Pin(33, Pin.OUT)  # Pin GPIO para el color verde
blue_pin = Pin(26, Pin.OUT)   # Pin GPIO para el color azul

# Screen Variables
width = 128
height = 64
line = 1 
highlight = 1
shift = 0
list_length = 0
total_lines = 6

# Create the display
oled = SSD1306_I2C(width=width, height=height, i2c=i2c)
oled.init_display()

# Setup the Rotary Encoder
button_pin = Pin(13, Pin.IN, Pin.PULL_UP)  # SW
direction_pin = Pin(15, Pin.IN, Pin.PULL_UP)  # DT
step_pin  = Pin(18, Pin.IN, Pin.PULL_UP)  # CLK

# For tracking the direction and button state
previous_value = True
button_down = False

def set_led_color(red, green, blue):
    """Set the RGB LED color"""
    red_pin.value(red)
    green_pin.value(green)
    blue_pin.value(blue)

def connect_wifi():
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    wlan.connect(ssid, password)
    
    while not wlan.isconnected():
        print('Esperando conexión WiFi...')
        set_led_color(1,0,0)
        sleep(0.2)

    print('Conectado a WiFi')
    print('IP:', wlan.ifconfig()[0])

def get_files():
    """ Get a list of Python files in the root folder of the Pico """
    files = listdir()
    menu = []
    for file in files:
        if file.endswith(".py") and file != "menu.py" and file != "boot.py" and file != "ssd1306.py" and file != "circular_buffer.py" and file != "max30102.py" and file != "simple.py":
            menu.append(file)
    return menu

def show_menu(menu):
    """ Shows the menu on the screen"""
    global line, highlight, shift, list_length
    item = 1
    line = 1
    line_height = 10
    oled.fill_rect(0,0,width,height,0)  # Clear the display
    list_length = len(menu)
    short_list = menu[shift:shift+total_lines]

    for item in short_list:
        if highlight == line:
            oled.fill_rect(0, (line-1)*line_height, width, line_height, 1)
            oled.text(">", 0, (line-1)*line_height, 0)
            oled.text(item, 10, (line-1)*line_height, 0)
        else:
            oled.text(item, 10, (line-1)*line_height, 1)
        line += 1 
    oled.show()  # Update the display only once

def launch(filename):
    """ Launch the Python script <filename> """
    global file_list
    set_led_color(1, 0, 0)  # LED en rojo para "Launching"
    oled.fill_rect(0,0,width,height,0)
    oled.text("Launching", 1, 10)
    oled.text(filename, 1, 20)
    oled.show()
    sleep(3)
    set_led_color(0, 0, 1)  # LED en naranja para ejecución normal
    exec(open(filename).read())
    show_menu(file_list)
    set_led_color(0, 0, 0)  # Apaga el LED al terminar

# Conectar a WiFi
connect_wifi()

file_list = get_files()
show_menu(file_list)

while True:
    set_led_color(1, 0, 1)
    if previous_value != step_pin.value():
        if step_pin.value() == False:
            if direction_pin.value() == False:
                if highlight > 1:
                    highlight -= 1  
                else:
                    if shift > 0:
                        shift -= 1  
            else:
                if highlight < total_lines:
                    highlight += 1
                else: 
                    if shift+total_lines < list_length:
                        shift += 1
            show_menu(file_list)
        previous_value = step_pin.value()   
    
    if button_pin.value() == False and not button_down:
        button_down = True
        print("Launching", file_list[highlight-1+shift])
        launch(file_list[(highlight-1) + shift])
        print("Returned from launch")
    
    if button_pin.value() == True and button_down:
        button_down = False
