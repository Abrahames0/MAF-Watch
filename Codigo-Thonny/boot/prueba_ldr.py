from machine import Pin, ADC, SoftI2C
from ssd1306 import SSD1306_I2C
from time import sleep
import math
from simple import MQTTClient
import random

# Configuración del pin ADC para leer el valor del fotoresistor (LDR)
ldr_pin = ADC(Pin(35))  # GPIO15 en ESP32
ldr_pin.atten(ADC.ATTN_11DB)  # Atenuación para medir hasta 3.6V
ldr_pin.width(ADC.WIDTH_12BIT)  # Resolución de 12 bits (0-4095)

# Configura el I2C y la pantalla OLED
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(width=128, height=64, i2c=i2c)
oled.init_display()

# Configura el botón del rotary encoder
button_pin = Pin(13, Pin.IN, Pin.PULL_UP)  # Configura el pin del botón


mqtt_server = b'broker.hivemq.com'  # Dirección IP de tu broker MQTT
topic_pub = b'topico/ldr_value'  # Tópico para publicar los datos

def read_ldr_sensor():
    ldr_reading = ldr_pin.read()
    return ldr_reading

def draw_thick_arc(cx, cy, radius, start_angle, end_angle, thickness=2):
    for t in range(thickness):
        for angle in range(start_angle, end_angle + 1):
            angle_rad = math.radians(angle)
            x = int(cx + (radius - t) * math.cos(angle_rad))
            y = int(cy - (radius - t) * math.sin(angle_rad))
            if 0 <= x < 128 and 0 <= y < 64:
                oled.pixel(x, y, 1)

def draw_circular_graph(value):
    oled.fill(0)  # Limpiar pantalla
    
    # Coordenadas del centro y radio del gráfico
    cx, cy = 64, 32
    radius = 30
    
    # Convertir el valor del LDR a un ángulo en grados (0-360)
    angle = min(int((value / 4095) * 360), 360)
    
    # Dibujar el contorno del gráfico circular (esto es un borde simple)
    for i in range(0, 360, 2):
        angle_rad = math.radians(i)
        x = int(cx + radius * math.cos(angle_rad))
        y = int(cy - radius * math.sin(angle_rad))
        if 0 <= x < 128 and 0 <= y < 64:
            oled.pixel(x, y, 1)
    
    # Dibujar el arco que representa el nivel de intensidad de luz
    draw_thick_arc(cx, cy, radius, 0, angle, thickness=6)
    
    # Mostrar el valor de luz en una posición más a la izquierda
    text_x = cx - 32  # Ajustar el valor para mover el texto a la izquierda
    text_y = cy - 4
    oled.text("LDR: {}".format(value), text_x, text_y, 1)
    
    # Mostrar el gráfico
    oled.show()
    
def publish_ldr_data(ldr_value):
    client = MQTTClient("", mqtt_server, 1883)
    client.connect()
    mensaje = str(ldr_value)
    client.publish(topic_pub, mensaje)
    print("Publicado en MQTT:", mensaje)
    client.disconnect()

while True:
    # Verificar si el botón del encoder está presionado
    if button_pin.value() == 0:  # Asumiendo que el botón está activo en 
        break  # Salir del bucle si el botón está presionado
    
    ldr_value = round(read_ldr_sensor() + random.uniform(25, 50), 2)
    
    # Dibujar el gráfico circular en la pantalla OLED
    draw_circular_graph(ldr_value)
    publish_ldr_data(int(ldr_value))
    
    sleep(1)