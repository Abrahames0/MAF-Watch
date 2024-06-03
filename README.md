## MAF-Watch
Proyecto de Dispositivo Inteligente

## Integrantes.
- Abraham Salvador Espinoza Gómez.
- Mario Alberto Rangel Márquez.
- Fernando Arvizu Sotelo.

## Objetivo general.


### Objetivos específicos.
Implementar un sistema de análisis del ambiente que monitorice condiciones como luz, ruido, temperatura y ritmo cardiaco, en base a los resultados el sistema puede mejorar la calidad del ambiente y activar automáticamente mecanismos como un ventilador o música cuando las condiciones puedan llegar a perjudicar la calidad del sueño.


## Tabla de Software utilizado.
| Id | Software | Version | Tipo |
|----|----------|---------|------|
| 1 |  sqlite  | 3.46.0 | SQL |
| 2 | Arduino IDE  | 4.1.4 |  IDE |
| 3 | Node-Red | 3.2.9 | MQTT |

## Tabla con el hardware utilizado (El costo de cada componente es al dia de 2-3 de junio del 2024).
| Id | Componente | Descripción | Imagen | Cantidad | Costo total |
|----|------------|-------------|--------|----------|-------------|
|1|TZT|TZT Módulo de Motor de vibración vibratoria de 5V, de alto y bajo nivel|![image](Imagenes/TZT.jpg)|1|$6,22 MXN|
|2|fotoconductora|Resistencia fotoconductora de luz LDR. |![image](/Imagenes/fotorresistencia.jpg)|1|$7,83 MXN|
|3|Sensor de detección UV|Módulo de Sensor de detección UV, módulo de rayos ultravioleta.|![image](./Imagenes/Modulo-de-Sensor-UV.jpg)|2|$43,32 MXN|
|4|Pantalla táctil|Pantalla táctil inteligente para Arduino LVGL, módulo TFT LCD RGB de 4,3 pulgadas.|![image](./Imagenes/Pantalla-tactil.jpg)|1|$560,69 MXN|
|5|Mini humidificador USB|Mini humidificador USB, Kits de bricolaje, fabricante de niebla y controlador|![image](./Imagenes/Mini-humidificador.jpg)|2|$27,77 MXN|
|6|ESP32|ESP32 es la denominación de una familia de chips SoC de bajo coste y consumo de energía, con tecnología Wi-Fi y Bluetooth de modo dual integrada.|![image](./Imagenes/Esp32.jpg)|2|$250.00 MXN|
|7|Sensor de oximetría|Módulo de Sensor de oximetría de frecuencia cardíaca, Sensor de ritmo cardíaco, consumo de energía ultrabajo. |![image](./Imagenes/Modulo-de-Sensor.jpg)|1|$24,67|

## Epicas del proyecto (Minimo debe de haber una épica por integrante de equipo).
-Monitorear las condiciones ambientales: esta épica se enfoca en el monitoreo de las condicioens ambientales con el sensor de rayos UV para asi aconsegar al usuario de los altos niveles y recomendarle no salir o usar bloqueador solar.

-Control de calidad del usuario: esta épica se enfoca en el control automático de la calidad del usuario para mantenerlo presentable o referscado, dependiendo de la situacion ya con algunos sensores puede rocearse agua o alguna locion.

-Almacenamiento y analsis de datos: esta épica se enfoca en el almacenamiento y analis de la información recopilada en tiempo real por medio de los sensores. El objetivo es enviar los datos medidos por los sensores a una base de datos y permitir su consumo para el análisis de los datos para entregarlos a forma de resumen al usuario.

## Tabla de historias de usuario.
| Id | Historia de usuario | Prioridad | Estimación | Como probarlo | Responsable |
|----|---------------------|-----------|------------|---------------|-------------|
|  1  | Como usuario quiero que se monitorice en tiempo real la temperatura que tengo para tener información más fiel a la realidad.| 1 | 3 Dias | Se obtiene información fiel en tiempo real através del sensor.| Mario Alberto Rangel Márquez |            |
|  2  | Como usuario quiero que se monitorice en tiempo real mi ritmo cardiaco que tengo para tener información más fiel a la realidad.| 1 | 3 Dias | Se obtiene información fiel en tiempo real através del sensor.| Abraham Salvador Espinoza Gómez |
|  3  | Como usuario quiero que se monitorice en tiempo real la luz UV para saber si debo usar bloqueador solar| 1 | 3 Dias | Se obtiene información fiel en tiempo real através del sensor.| Mario Alberto Rangel Márquez |
|  4  | Como usuario quiero poder rosearme aromas en ciertos momentos.| 5 | 3 Dias | Se obtiene información fiel en tiempo real através del sensor.| Mario Alberto Rangel Márquez | 
|  5  | Como usuario quiero poder configurar un recordatorio para dormir.| 5 | 3 Dias | Se obtiene información fiel en tiempo real através del sensor.| Mario Alberto Rangel Márquez |  
|  6  | Como usuario quiero saber la duración de mi sueño para saber si dormi las horas necesarias.| 2 | 3 Dias | Se obtiene información fiel en tiempo real através del sensor.| Fernando Arvizu Sotelo. | 
|  7  | Como usuario quiero que el dispositivo sea comodo de usar para que no me moleste al dormir.| 3 | 3 Dias | Se obtiene información fiel en tiempo real através del sensor.| Fernando Arvizu Sotelo. | 

## Tablero de ClickUp.
![image](./Imagenes/Clickup.png)

## Dashbord de Node-Red
![image](./Imagenes/Node-Red.jpg)

## Librerias Utilizadas.
- Wire.h
- MAX30105.h
- heartRate.h
- WiFi.h
- PubSubClient.h