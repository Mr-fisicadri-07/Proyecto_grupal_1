📋 Requisitos del Sistema

Python 3.8 o superior.

Librerías:

pygame (para el audio).

tkinter (incluido por defecto en la mayoría de instalaciones de Python).

🛠️ Instalación y Ejecución

Clonar o Descargar este repositorio.

Asegúrate de tener la estructura de carpetas correcta (ver sección Estructura del Proyecto).

Instala la dependencia de audio:

pip install pygame


Ejecuta el juego desde la raíz del proyecto:

python main.py


📂 Estructura del Proyecto

El proyecto sigue una estructura limpia para facilitar su mantenimiento:

simon_dice/
│
├── main.py                # 🚀 Punto de entrada principal
├── config.py              # ⚙️ Cargador de configuración y rutas
├── simon_record.txt       # 🏆 Archivo automático de puntuación máxima
│
├── data/                  # 💾 Datos editables
│   ├── settings.json      # Configuración de ventana y mapeo de sonidos
│   └── gamedata.json      # Base de datos de palabras y capitales
│
├── modules/               # 🧠 Código fuente modular
│   ├── logic.py           # Reglas del juego y normalización de texto
│   ├── sound.py           # Motor de audio
│   └── ui.py              # Interfaz gráfica (Tkinter)
│
└── assets/                # 🔊 Archivos de audio (.mp3)
    ├── tiempo_wii.mp3
    ├── fallo.mp3
    └── ...


🎮 Cómo Jugar

Atención a la Orden:

Si la instrucción empieza con "Simón dice...", ¡debes cumplirla! (Escribir la respuesta y pulsar "¡HACERLO!").

Si la instrucción NO empieza con "Simón dice...", NO hagas nada. Pulsa el botón "PASAR".

Tiempo Límite: Tienes un temporizador que disminuye conforme ganas puntos. Si llega a 0, pierdes.

Puntuación: Gana puntos acertando trampas y respuestas correctas.

⚙️ Personalización (JSON)

Puedes editar los archivos en la carpeta data/ para personalizar tu experiencia:

gamedata.json: Añade nuevas palabras para el modo escritura o nuevos países y capitales.

settings.json: Cambia el tamaño de la ventana, el color de fondo o reasigna los archivos de sonido.

👤 Autor

Desarrollado como proyecto educativo para demostrar buenas prácticas de programación en Python, uso de Tkinter y manejo de archivos JSON.

¡Disfruta del juego y supera tu récord! 🤡








""" Este programa es una versión avanzada del juego "Simón Dice" con múltiples tipos de preguntas.
Incluye matemáticas, palabras y capitales de países, con una interfaz gráfica mejorada y sonidos.
Al iniciar, muestra un menú con las reglas del juego. Una vez dentro del juego, el jugador debe decidir
si obedecer o no las órdenes de "Simón" basándose en si la instrucción comienza con "Simón dice".
Si el jugador responde correctamente, gana puntos; si falla o se acaba el tiempo, pierde.
Cuando el juego termina, se muestra el puntaje final si se ha establecido un nuevo récord y una opcion
para reiniciar el "Simón dice".
El usuario podrá volver al menú principal en cualquier momento durante el juego.

El juego utiliza un archivo JSON para cargar las preguntas y respuestas, y guarda el récord del jugador
en un archivo de texto. Tambien hemos utilizado las bibliotecas tkinter, random, os, threading y sys.
Hemos utilizado tkinker para la interfaz gráfica, random para la generación de números aleatorios,
os para la gestión de archivos, threading para manejar sonidos sin bloquear la interfaz, y sys para la detección del sistema operativo.

Por otro lado, hemos implementado un gestor de sonido que utiliza la biblioteca winsound en Windows para reproducir sonidos simples.

El código está estructurado en clases para separar la lógica del juego, la gestión de sonidos y la interfaz gráfica.

Ejemplo de juego:
1. El jugador inicia el juego y ve las reglas en el menú principal.
2. El juego genera una instrucción, por ejemplo: "Simón dice: calcula 5 + 3".
3. El jugador debe ingresar "8" y presionar "¡Hacerlo!" para ganar un punto en menos de 15 segundos.
4.
Si acierta:
    - Gana un punto y recibe una nueva instrucción.
Si falla o se acaba el tiempo:
    - El juego termina y se muestra el puntaje final. Se da la opción de reiniciar o volver al menú principal.
"""
