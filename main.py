import network
import socket
import time
import json
from machine import ADC, Pin, Timer
import machine
import math
import time



LDR_PIN = 35
ANEMOMETRE_PIN = 39
HUMIDITY_PIN = 33
TEMPERATURE_PIN = 34
CO2_PIN = 36
class Anemometre():
    def __init__(self, pin):
        self.analog_pin = Pin(pin)  # Pin GPIO 34 (cambiar según tu necesidad)
        self.adc = ADC(self.analog_pin)  # Crear objeto ADC
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)
    def read(self):
        return self.adc.read()
    def value(self):
        self.read = self.adc.read()
        self.vel = self.read*4.0*14.0/4095.0
        self.vel = self.vel*3.6
        return self.vel
    

class Humidity:
    def __init__(self, pin):
        self.input_pin = Pin(pin, Pin.IN)
        self.input_pin.irq(trigger=Pin.IRQ_RISING, handler=self.count_pulses)
        self.timer = Timer(1)
        self.timer.init(period=1000, mode=Timer.PERIODIC, callback=self.calculate_frequency)
        self.humidity = 0
        self.frequency = 0
        self.pulse_count = 0

    def count_pulses(self, pin):  # Añade el parámetro 'pin' porque es necesario para el handler de interrupción
        """Incrementa el contador de pulsos cada vez que se detecta un flanco ascendente."""
        self.pulse_count += 1

    def calculate_frequency(self, timer):
        """Calcula la frecuencia de los pulsos (Hz) y reinicia el contador."""
        self.frequency = self.pulse_count  # Frecuencia en Hz (pulsos por segundo)
        self.pulse_count = 0  # Reinicia el contador de pulsos para la siguiente medición

    def get_frequency(self):
        """Devuelve la frecuencia calculada."""
        return self.frequency

    def value(self):
        """Calcula y devuelve la humedad en función de la frecuencia."""
        if self.frequency == 0:
            self.humidity = 0  # Evita división por cero
            return self.humidity
        else:
            self.capacity = 1 / (self.frequency * 2 * 10**6) # Ajusta el cálculo según sea necesario
            self.capacity /= (180*10**-12)
            self.humidity = -3.4656*10**3*self.capacity**3 + 1.0732*10**4*self.capacity**2 - 1.0457*10**4*self.capacity + 3.2459*10**3
            if self.humidity >= 100:
                self.humidity = 100
            elif self.humidity < 0:
                self.humidity = 0
        return self.humidity
    
class LDR:
    def __init__(self, pin):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)
        self.R1 = 3086
        self.Vcc = 3.3
        self.R_lux = 10000
        self.gamma = 0.5

    def value(self):
        # Leer el valor analógico del ADC (0 a 4095)
        adc_value = self.adc.read()

        # Convertir a voltaje de salida del divisor de tensión
        Vin = (adc_value / 4095) * self.Vcc
        #print("Voltage: ", Vin)
        # Calcular R_LDR usando la ecuación del divisor de tensión
        if Vin == 0:  # Evitar división por cero
            return float('inf')  # Resistencia infinita (oscuridad)

        R_LDR = self.R1 * Vin / (self.Vcc - Vin)
        #print("Resistencia :", R_LDR)
        # Calcular la intensidad de luz (lux) usando la ecuación de la LDR
        if R_LDR <= 0:  # Evitar valores negativos de resistencia
            return 0

        self.lux = (R_LDR / self.R_lux) ** (-1 / self.gamma)
        return self.lux

class Temperature():
    def __init__(self, pin):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)
        self.Vcc = 3.3
        self.offset = 1.25
        self.gain = 100/3.0
    def value(self):
        # Leer el valor analógico del ADC (0 a 4095)
        try:
            adc_value = self.adc.read()
            #print(adc_value/4095*3.3)
            # Convertir a voltaje de salida del divisor de tensión
            temp = self.gain*((adc_value / 4095) * self.Vcc - self.offset)
        except ZeroDivisionError:
            temp = 0
        #print("Voltage: ", Vin)
        return temp


class MQ135(object):
    """ Class for dealing with MQ13 Gas Sensors """
    # The load resistance on the board
    RLOAD = 100.0
    # Calibration resistance at atmospheric CO2 level
    RZERO = 76.63
    # Parameters for calculating ppm of CO2 from sensor resistance
    PARA = 116.6020682
    PARB = 2.769034857

    # Parameters to model temperature and humidity dependence
    CORA = 0.00035
    CORB = 0.02718
    CORC = 1.39538
    CORD = 0.0018
    CORE = -0.003333333
    CORF = -0.001923077
    CORG = 1.130128205

    # Atmospheric CO2 level for calibration purposes
    ATMOCO2 = 397.13


    def __init__(self, pin):
        self.adc = ADC(Pin(pin))
        self.adc.atten(ADC.ATTN_11DB)
        self.adc.width(ADC.WIDTH_12BIT)

    def get_correction_factor(self, temperature, humidity):
        """Calculates the correction factor for ambient air temperature and relative humidity

        Based on the linearization of the temperature dependency curve
        under and above 20 degrees Celsius, asuming a linear dependency on humidity,
        provided by Balk77 https://github.com/GeorgK/MQ135/pull/6/files
        """

        if temperature < 20:
            return self.CORA * temperature * temperature - self.CORB * temperature + self.CORC - (humidity - 33.) * self.CORD

        return self.CORE * temperature + self.CORF * humidity + self.CORG

    def get_resistance(self):
        """Returns the resistance of the sensor in kOhms // -1 if not value got in pin"""
        value = self.adc.read()
        if value == 0:
            return -1

        return (1023./value - 1.) * self.RLOAD

    def get_corrected_resistance(self, temperature, humidity):
        """Gets the resistance of the sensor corrected for temperature/humidity"""
        return self.get_resistance()/ self.get_correction_factor(temperature, humidity)

    def get_ppm(self):
        """Returns the ppm of CO2 sensed (assuming only CO2 in the air)"""
        return self.PARA * math.pow((self.get_resistance()/ self.RZERO), -self.PARB)

    def get_corrected_ppm(self, temperature, humidity):
        """Returns the ppm of CO2 sensed (assuming only CO2 in the air)
        corrected for temperature/humidity"""
        return self.PARA * math.pow((self.get_corrected_resistance(temperature, humidity)/ self.RZERO), -self.PARB)

    def get_rzero(self):
        """Returns the resistance RZero of the sensor (in kOhms) for calibratioin purposes"""
        return self.get_resistance() * math.pow((self.ATMOCO2/self.PARA), (1./self.PARB))

    def get_corrected_rzero(self, temperature, humidity):
        """Returns the resistance RZero of the sensor (in kOhms) for calibration purposes
        corrected for temperature/humidity"""
        return self.get_corrected_resistance(temperature, humidity) * math.pow((self.ATMOCO2/self.PARA), (1./self.PARB))

class BME280:
    def __init__(self, sda_pin=12, scl_pin=14, address=0x76):
        # Inicialización del bus I2C
        self.i2c = machine.SoftI2C(scl=machine.Pin(scl_pin), sda=machine.Pin(sda_pin))
        self.address = address
        
        # Comandos de configuración del sensor BME280
        self.BME280_REG_CTRL_MEAS = 0xF4  # Registro de control de medición
        self.BME280_REG_PRESSURE_MSB = 0xF7  # Registro de presión

        # Inicialización del sensor BME280 (configurar la medición de temperatura y presión)
        # 0x27 corresponde a oversampling de 16x para temperatura y presión (configuración para obtener buena precisión)
        self.i2c.writeto(self.address, bytes([self.BME280_REG_CTRL_MEAS, 0x27]))  
    # Leer los parámetros de calibración del BME280
    def read_calibration_data(self):
        # Los registros de calibración del BME280
        calibration_data = {}
        calibration_data['dig_T1'] = self.i2c.readfrom_mem(self.address, 0x88, 2)  # T1
        calibration_data['dig_T2'] = self.i2c.readfrom_mem(self.address, 0x8A, 2)  # T2
        calibration_data['dig_T3'] = self.i2c.readfrom_mem(self.address, 0x8C, 2)  # T3
        calibration_data['dig_P1'] = self.i2c.readfrom_mem(self.address, 0x8E, 2)  # P1
        calibration_data['dig_P2'] = self.i2c.readfrom_mem(self.address, 0x90, 2)  # P2
        calibration_data['dig_P3'] = self.i2c.readfrom_mem(self.address, 0x92, 2)  # P3
        calibration_data['dig_P4'] = self.i2c.readfrom_mem(self.address, 0x94, 2)  # P4
        calibration_data['dig_P5'] = self.i2c.readfrom_mem(self.address, 0x96, 2)  # P5
        calibration_data['dig_P6'] = self.i2c.readfrom_mem(self.address, 0x98, 2)  # P6
        calibration_data['dig_P7'] = self.i2c.readfrom_mem(self.address, 0x9A, 2)  # P7
        calibration_data['dig_P8'] = self.i2c.readfrom_mem(self.address, 0x9C, 2)  # P8
        calibration_data['dig_P9'] = self.i2c.readfrom_mem(self.address, 0x9E, 2)  # P9

        # Convertir los datos de calibración de 2 bytes a valores enteros
        for key in calibration_data:
            calibration_data[key] = int.from_bytes(calibration_data[key], 'little')

        return calibration_data
    def calculate_pressure(self, press_raw, calibration_data, temperature):
        # Cálculos para la presión a partir de press_raw y los parámetros de calibración
        # Primer paso: realizar ajustes de temperatura (si es necesario)

        # Realizar el ajuste de temperatura
        var1 = (temperature / 2.0) - 64000.0
        var2 = var1 * var1 * calibration_data['dig_P6'] / 32768.0
        var2 = var2 + var1 * calibration_data['dig_P5'] * 2.0
        var2 = (var2 / 4.0) + (calibration_data['dig_P4'] * 65536.0)
        var1 = (calibration_data['dig_P3'] * var1 * var1 / 524288.0 + calibration_data['dig_P2'] * var1) / 524288.0
        var1 = (1.0 + var1 / 32768.0) * calibration_data['dig_P1']

        if var1 == 0:
            return 0  # Evitar división por cero

        # Calcular la presión
        press = 1048576.0 - press_raw
        press = (press - (var2 / 4096.0)) * 6250.0 / var1
        var2 = calibration_data['dig_P9'] * press * press / 2147483648.0
        var1 = var2 + press * calibration_data['dig_P8'] / 32768.0
        press = press + (var1 + calibration_data['dig_P7']) / 16.0

        return press  # Resultado en Pa

    def read_pressure(self):
        # Leer los 3 bytes de datos de presión (MSB, LSB, XLSB)
        data = self.i2c.readfrom_mem(self.address, self.BME280_REG_PRESSURE_MSB, 3)
        # Convertir los 3 bytes a un valor de 32 bits (presión en Pa)
        raw_pressure = (data[0] << 12) | (data[1] << 4) | (data[2] >> 4)
        return raw_pressure

    # def calculate_pressure(self, raw_pressure):
    #     # El sensor BME280 devuelve la presión en Pa, así que lo convertimos a hPa
    #     print("Raw pressure: ", raw_pressure)
    #     pressure = raw_pressure / 256.0  # Dividir por 256 para obtener el valor real en Pa
    #     return pressure

    def value(self, temperature):
        # Leer y calcular la presión
        calibration_data = self.read_calibration_data()

        # Leer el valor crudo de presión
        press_raw = self.read_pressure()

        # Calcular la presión real usando los datos de calibración y el valor crudo
        pressure = self.calculate_pressure(press_raw, calibration_data, temperature=temperature)  # Asume temperatura de 25°C, ajústala según sea necesario
        return pressure*0.75

ldr = LDR(LDR_PIN)
anemometre = Anemometre(ANEMOMETRE_PIN)
humidity = Humidity(HUMIDITY_PIN)
termo = Temperature(TEMPERATURE_PIN)
mq135 = MQ135(CO2_PIN)
bme = BME280()

# Conectar al WiFi
def connect_wifi():
    ssid = "iPhone de Pol"
    password = "polpavis"
    wlan = network.WLAN(network.STA_IF)
    wlan.active(True)
    if not wlan.isconnected():
        print('Conectando a la red WiFi...')
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Conexión WiFi establecida', wlan.ifconfig())

# Configuración del servidor
def start_server():
    addr = socket.getaddrinfo('172.20.10.2', 80)[0][-1]
    s = socket.socket()
    s.bind(addr)
    s.listen(5)
    print('Escuchando en', addr)

    while True:
        cl, addr = s.accept()
        print("Cliente connectado")
        # print('Cliente conectado desde', addr)
        request = cl.recv(1024)
        # print('Request:', request)
        temperature = termo.value() if termo.value() != float('inf') else None
        humidity_value = humidity.value() if humidity.value() != float('inf') else None
        wind_speed = anemometre.value() if anemometre.value() != float('inf') else None
        light_value = ldr.value() if ldr.value() != float('inf') else None
        co2_value = mq135.get_corrected_ppm(temperature, humidity_value) if mq135.get_corrected_ppm(temperature, humidity_value) != float('inf') else None
        pressure = bme.value(temperature) if bme.value(temperature) != float('inf') else None
        print("Temperature: ", temperature)
        print("Humidity: ", humidity_value)
        print("Wind Speed: ", wind_speed)
        print("Light: ", light_value)
        print("CO2: ", co2_value)
        print("Pressure: ", pressure)
        # Si se accede a la ruta "/data", enviamos los datos en formato JSON
        if b"/data" in request:
            response = {
                "temperature": temperature,
                "humidity": humidity_value,
                "windSpeed": wind_speed,
                "light": light_value,
                "co2": co2_value,
                "pressure": pressure
            }
            # Convertir los datos a JSON
            response_json = json.dumps(response)
            cl.send('HTTP/1.1 200 OK\r\n')
            cl.send('Content-Type: application/json\r\n')
            cl.send('Access-Control-Allow-Origin: *\r\n')  # Permitir solicitudes CORS
            cl.send('Access-Control-Allow-Methods: GET, POST, PUT, DELETE, OPTIONS\r\n')
            cl.send('Access-Control-Allow-Headers: Content-Type\r\n')
            cl.send('Connection: close\r\n\r\n')
            cl.send(response_json)
        else:
            # Responder con un mensaje básico para otras rutas
            cl.send('HTTP/1.1 404 Not Found\r\n')
            cl.send('Connection: close\r\n\r\n')
            cl.send('<h1>404 Not Found</h1>')

        cl.close()


if __name__ == "__main__":
    # Ejecutar el programa
    while True:
        try:
            connect_wifi()
            start_server()
        except Exception as e:
            print("Error:", e)
            machine.reset()
            time.sleep(5)
            continue
        finally:
            continue

