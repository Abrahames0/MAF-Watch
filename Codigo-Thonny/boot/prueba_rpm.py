from machine import Pin, ADC, SoftI2C
from ssd1306 import SSD1306_I2C
from time import sleep, ticks_diff, ticks_ms
from max30102 import MAX30102, MAX30105_PULSE_AMP_MEDIUM
import math
from simple import MQTTClient

# Configura el I2C y la pantalla OLED
i2c = SoftI2C(sda=Pin(21), scl=Pin(22), freq=400000)
oled = SSD1306_I2C(width=128, height=64, i2c=i2c)
oled.init_display()

# Configura el botón del rotary encoder
button_pin = Pin(13, Pin.IN, Pin.PULL_UP)

mqtt_server = b'broker.hivemq.com'  # Dirección IP de tu broker MQTT
topic_pub = b'topico/rpm'  # Tópico para publicar los datos

# Clase para el monitoreo del ritmo cardíaco
class HeartRateMonitor:
    def __init__(self, sample_rate=100, window_size=10, smoothing_window=5):
        self.sample_rate = sample_rate
        self.window_size = window_size
        self.smoothing_window = smoothing_window
        self.samples = []
        self.timestamps = []
        self.filtered_samples = []

    def add_sample(self, sample):
        timestamp = ticks_ms()
        self.samples.append(sample)
        self.timestamps.append(timestamp)

        if len(self.samples) >= self.smoothing_window:
            smoothed_sample = sum(self.samples[-self.smoothing_window:]) / self.smoothing_window
            self.filtered_samples.append(smoothed_sample)
        else:
            self.filtered_samples.append(sample)

        if len(self.samples) > self.window_size:
            self.samples.pop(0)
            self.timestamps.pop(0)
            self.filtered_samples.pop(0)

    def find_peaks(self):
        peaks = []
        if len(self.filtered_samples) < 3:
            return peaks

        recent_samples = self.filtered_samples[-self.window_size:]
        min_val = min(recent_samples)
        max_val = max(recent_samples)
        threshold = min_val + (max_val - min_val) * 0.6  # Ajustar la sensibilidad aquí

        for i in range(1, len(self.filtered_samples) - 1):
            if (
                self.filtered_samples[i] > threshold
                and self.filtered_samples[i - 1] < self.filtered_samples[i]
                and self.filtered_samples[i] > self.filtered_samples[i + 1]
            ):
                peak_time = self.timestamps[i]
                peaks.append((peak_time, self.filtered_samples[i]))

        return peaks

    def calculate_heart_rate(self):
        peaks = self.find_peaks()

        if len(peaks) < 2:
            return None

        intervals = []
        for i in range(1, len(peaks)):
            interval = ticks_diff(peaks[i][0], peaks[i - 1][0])
            intervals.append(interval)

        average_interval = sum(intervals) / len(intervals)
        heart_rate = 60000 / average_interval
        return heart_rate

# Función para dibujar un arco grueso
def draw_thick_arc(cx, cy, radius, start_angle, end_angle, thickness=2):
    for t in range(thickness):
        for angle in range(start_angle, end_angle + 1):
            angle_rad = math.radians(angle)
            x = int(cx + (radius - t) * math.cos(angle_rad))
            y = int(cy - (radius - t) * math.sin(angle_rad))
            if 0 <= x < 128 and 0 <= y < 64:
                oled.pixel(x, y, 1)

# Función para dibujar la gráfica circular
def draw_circular_graph(value):
    oled.fill(0)
    cx, cy = 64, 32
    radius = 30
    angle = min(int((value / 4095) * 360), 360)
    
    for i in range(0, 360, 2):
        angle_rad = math.radians(i)
        x = int(cx + radius * math.cos(angle_rad))
        y = int(cy - radius * math.sin(angle_rad))
        if 0 <= x < 128 and 0 <= y < 64:
            oled.pixel(x, y, 1)
    
    draw_thick_arc(cx, cy, radius, 0, angle, thickness=6)
    
    text_x = cx - 32
    text_y = cy - 4
    oled.text("BPM: {}".format(value), text_x, text_y, 1)
    oled.show()
    
def publish_rpm_data(ldr_value):
    client = MQTTClient("", mqtt_server, 1883)
    client.connect()
    mensaje = str(ldr_value)
    client.publish(topic_pub, mensaje)
    print("Publicado en MQTT:", mensaje)
    client.disconnect()

def main():
    sensor = MAX30102(i2c=i2c)
    if sensor.i2c_address not in i2c.scan():
        oled.text("Sensor not found", 0, 0)
        oled.show()
        return
    elif not sensor.check_part_id():
        oled.text("Incompatible sensor", 0, 0)
        oled.show()
        return
    else:
        oled.text("Sensor ready", 0, 0)
        oled.show()

    sensor.setup_sensor()
    sensor_sample_rate = 400
    sensor.set_sample_rate(sensor_sample_rate)
    sensor_fifo_average = 8
    sensor.set_fifo_average(sensor_fifo_average)
    sensor.set_active_leds_amplitude(MAX30105_PULSE_AMP_MEDIUM)
    actual_acquisition_rate = int(sensor_sample_rate / sensor_fifo_average)

    sleep(1)

    hr_monitor = HeartRateMonitor(
        sample_rate=actual_acquisition_rate,
        window_size=int(actual_acquisition_rate * 3),
    )

    hr_compute_interval = 1  # Segundos
    ref_time = ticks_ms()

    while True:
        if button_pin.value() == 0:
            break

        sensor.check()

        if sensor.available():
            ir_reading = sensor.pop_ir_from_storage()
            if ir_reading > 0:  # Filtra los valores de 0
                #print(f"IR Reading: {ir_reading}")  # Depuración: Mostrar el valor IR
                hr_monitor.add_sample(ir_reading)

        if ticks_diff(ticks_ms(), ref_time) / 1000 > hr_compute_interval:
            heart_rate = hr_monitor.calculate_heart_rate()
            if heart_rate is not None:
                draw_circular_graph(int(heart_rate))
                publish_rpm_data(int(heart_rate))
            else:
                oled.fill(0)
                oled.text("Calculating...", 0, 0)
                oled.show()
            ref_time = ticks_ms()

if __name__ == "__main__":
    main()

