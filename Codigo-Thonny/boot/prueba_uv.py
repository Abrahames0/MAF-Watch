from machine import Pin, ADC, SoftI2C
from ssd1306 import SSD1306_I2C
from time import sleep
import math
from simple import MQTTClient

# Configuración del pin analógico donde está conectado el sensor UV
uv_pin = ADC(Pin(34))  # GPIO34 (D34) en ESP32
uv_pin.atten(ADC.ATTN_11DB)   # Atenuación para medir hasta 3.6V
uv_pin.width(ADC.WIDTH_12BIT)  # Resolución de 12 bits (0-4095)

# Configura el I2C y la pantalla OLED
i2c = SoftI2C(scl=Pin(22), sda=Pin(21))
oled = SSD1306_I2C(width=128, height=64, i2c=i2c)
oled.init_display()

# Configura el botón del rotary encoder
button_pin = Pin(13, Pin.IN, Pin.PULL_UP)  # Configura el pin del botón

mqtt_server = b'broker.hivemq.com'  # Dirección IP de tu broker MQTT
topic_pub = b'topico/uv'  # Tópico para publicar los datos

def read_uv_sensor():
    uv_reading = uv_pin.read()
    uv_voltage = uv_reading * (3.6 / 4095.0)  # Convertir lectura a voltaje (0-3.6V)
    uv_intensity = uv_voltage * 307  # Aproximación a intensidad UV en mW/cm²
    return uv_intensity

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
    
    # Convertir el valor de intensidad UV a un ángulo en grados (0-360)
    angle = min(int((value / 1023) * 360), 360)
    
    # Dibujar el contorno del gráfico circular (esto es un borde simple)
    for i in range(0, 360, 2):
        angle_rad = math.radians(i)
        x = int(cx + radius * math.cos(angle_rad))
        y = int(cy - radius * math.sin(angle_rad))
        if 0 <= x < 128 and 0 <= y < 64:
            oled.pixel(x, y, 1)
    
    # Dibujar el arco que representa el nivel de intensidad UV
    draw_thick_arc(cx, cy, radius, 0, angle, thickness=6)
    
    # Mostrar la intensidad UV en una posición más a la izquierda
    text_x = cx - 32  # Ajustar el valor para mover el texto a la izquierda
    text_y = cy - 4
    oled.text("{:.2f} mW/cm2".format(value), text_x, text_y, 1)
    
    # Mostrar el gráfico
    oled.show()
    
def publish_uv_data(uv_value):
    client = MQTTClient("", mqtt_server, 1883)
    client.connect()
    mensaje = str(uv_value)
    client.publish(topic_pub, mensaje)
    print("Publicado en MQTT:", mensaje)
    client.disconnect()

while True:
    # Verificar si el botón del encoder está presionado
    if button_pin.value() == 0:  # Asumiendo que el botón está activo en bajo
        break  # Salir del bucle si el botón está presionado
    
    uv_intensity = read_uv_sensor()
    
    # Dibujar el gráfico circular en la pantalla OLED
    draw_circular_graph(uv_intensity)
    publish_uv_data(int(uv_intensity))
    
    sleep(1)
