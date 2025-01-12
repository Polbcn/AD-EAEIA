document.addEventListener('DOMContentLoaded', function() {
    // Datos históricos iniciales
    let humidityHistory = [];
    let temperatureHistory = [];
    let windSpeedHistory = [];
    let lightHistory = [];
    let co2History = [];
    let PressureHistory = [];
    let labels = [];
    const status_img = document.getElementById("connectionStatus");
    // Función para actualizar los datos
    function updateData() {
        let newHumidity = 'N/A';
        let newTemperature = 'N/A';
        let newWindSpeed = 'N/A';
        let newLight = 'N/A';
        let newCO2 = 'N/A';
        let newPressure = 'N/A';

        // Crear un AbortController
        const controller = new AbortController();
        const timeoutId = setTimeout(() => {
            controller.abort();  // Aborta la solicitud después del tiempo de espera
        }, 5000);  // Timeout de 5 segundos

        fetch('http://172.20.10.2/data', { signal: controller.signal })
            .then(response => {
                if (!response.ok) {
                    throw new Error(`HTTP error! Status: ${response.status}`);
                }
                return response.json();
            })
            .then(data => {
                // Limpiar el timeout cuando la solicitud se complete correctamente
                clearTimeout(timeoutId);

                // Asignar los nuevos valores a las variables, con validación para null o undefined
                newHumidity = data.humidity !== null && data.humidity !== undefined ? data.humidity.toFixed(2) : 'N/A';
                newTemperature = data.temperature !== null && data.temperature !== undefined ? data.temperature.toFixed(2) : 'N/A';
                newWindSpeed = data.windSpeed !== null && data.windSpeed !== undefined ? data.windSpeed.toFixed(2) : 'N/A';
                newLight = data.light !== null && data.light !== undefined ? data.light.toFixed(2) : 'N/A';
                newCO2 = data.co2 !== null && data.co2 !== undefined ? data.co2.toFixed(2) : 'N/A';
                newPressure = data.pressure !== null && data.pressure !== undefined ? data.pressure.toFixed(2) : 'N/A';

                // Añadir los nuevos datos al historial (solo si no son 'N/A')
                if (newHumidity !== 'N/A') humidityHistory.push(newHumidity);
                if (newTemperature !== 'N/A') temperatureHistory.push(newTemperature);
                if (newWindSpeed !== 'N/A') windSpeedHistory.push(newWindSpeed);
                if (newLight !== 'N/A') lightHistory.push(newLight);
                if (newCO2 !== 'N/A') co2History.push(newCO2);
                if (newPressure !== 'N/A') PressureHistory.push(newPressure);

                // Limitar a los últimos 10 datos
                if (humidityHistory.length > 10) humidityHistory.shift();
                if (temperatureHistory.length > 10) temperatureHistory.shift();
                if (windSpeedHistory.length > 10) windSpeedHistory.shift();
                if (lightHistory.length > 10) lightHistory.shift();
                if (co2History.length > 10) co2History.shift();
                if (PressureHistory.length > 10) PressureHistory.shift();

                // Actualizar los indicadores de la página
                document.getElementById('temperature').innerText = `${newTemperature} °C`;
                document.getElementById('humidity').innerText = `${newHumidity} %`;
                document.getElementById('windSpeed').innerText = `${newWindSpeed} km/h`;
                document.getElementById('light').innerText = `${newLight} Lux`;
                document.getElementById('co2').innerText = `${newCO2} ppm`;
                document.getElementById('pressure').innerText = `${newPressure} hPa`;
                status_img.src = "connected.png";
            })
            .catch(error => {
                // Capturar error si la solicitud falla o se aborta
                if (error.name === 'AbortError') {
                    console.error('La solicitud se agotó por el tiempo de espera.');
                } else {
                    console.error('Error al obtener los datos:', error);
                }

                // Aquí puedes manejar valores predeterminados cuando hay un error
                newHumidity = 'Error';
                newTemperature = 'Error';
                newWindSpeed = 'Error';
                newLight = 'Error';
                newCO2 = 'Error';
                newPressure = 'Error';

                // Actualizar los indicadores con los valores predeterminados
                document.getElementById('temperature').innerText = `${newTemperature}`;
                document.getElementById('humidity').innerText = `${newHumidity}`;
                document.getElementById('windSpeed').innerText = `${newWindSpeed}`;
                document.getElementById('light').innerText = `${newLight}`;
                document.getElementById('co2').innerText = `${newCO2}`;
                document.getElementById('pressure').innerText = `${newPressure}`;
                status_img.src = "disconnected.png";

            });
    }

    // Actualizar datos cada 5 segundos
    setInterval(updateData, 1000);
});
