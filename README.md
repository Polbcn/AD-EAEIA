# Estaciones Meteorologicas Guays S.A.

Welcome to the **Estaciones Meteorologicas Guays S.A.**! This project leverages the ESP32 microcontroller to monitor air quality and other environmental indicators, providing real-time data through a web interface. Perfect for IoT enthusiasts and environmental monitoring projects.

---

## 🌟 Features

- **Real-time Monitoring**: Measures CO2 levels, temperature, pressure, and humidity.
- **Web Interface**: Access data from any device via a lightweight web server.
- **Customizable**: Easily adaptable to other sensors or functionalities.
- **CORS Support**: Enables seamless cross-origin requests for integration.

---

## 🚀 Quick Start

### Prerequisites

- **Hardware**:
  - ESP32 microcontroller
  - MQ135 gas sensor
  - BME280 environmental sensor
  - Termopar Type K
  - Anemometre 0-4V
  - LDR 5516
  - Humidity Sensor
  
- **Software**:
  - Python (for additional scripts)
  - MicroPython firmware installed on ESP32
  - Vscode / Thonny

### Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/Polbcn/AD-EAEIA
   ```
2. **Upload the firmware and scripts** to your ESP32 using tools like `Vscode` or `Thonny`.
3. **Connect the sensors** following the provided pinout diagram that you can find in our report.
4. **Run the ESP32 server script**, and access the web interface via the IP address displayed on the console.
5. **Run the Web Interface**, using a local hosting like `Apache`
---

## 📊 Sensor Data Output

### Example JSON Response
```json
{
  "co2": 412,
  "temperature": 25.3,
  "humidity": 40.2,
  "pressure": 1013.25
  ...
}
```

### Web Interface Screenshot
![Web Interface](https://drive.google.com/file/d/1-LrZYuq4FvdSe3PlL7FU4ftI4qVPQpC9/view?usp=sharing)

---

## 🛠️ Configuration

### Customization
- **Web Interface**: Modify the `HTML` template in the server code to customize the UI.


## ⚙️ Project Structure

```
📂 gas-sensor-monitoring-system
├── 📄 main.py           # Main server script
├── /Web
├──── 📄 index.html
├──── 📄 style.css
├──── 📄 script.js
└── 📄 README.md         # Project documentation
```

---

## 🤝 Contributing

1. Fork the repository
2. Create a new branch (`git checkout -b feature-branch`)
3. Commit your changes (`git commit -m 'Add a new feature'`)
4. Push to the branch (`git push origin feature-branch`)
5. Open a Pull Request

Note: This is an example as it is an educational project for one of our subjects at UPC, so we will not give support or accept pull requests :)
---

## 📄 License

This project is licensed not licensed. Please do not copy it, but as it is public we hope that you can learn something with it. If you have questions, please refer to pol.pavo@estudiantat.upc.edu or german.bueno@estudiantat.upc.edu

---

## 🌐 Links

- [ESP32 Documentation](https://docs.espressif.com/projects/esp-idf/en/latest/)
- [MicroPython Documentation](https://docs.micropython.org/en/latest/)
- [MQ135 Sensor Datasheet](https://www.sparkfun.com/datasheets/Sensors/Biometric/MQ-135.pdf)

---

**Developed with ❤️ by Pol Pavo & German Bueno (https://github.com/Polbcn)**
