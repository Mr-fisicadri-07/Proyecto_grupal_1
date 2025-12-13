Voy a dejar el readme iniciado

Integrantes del grupo:

Jorge Martínez

Santiago de Dios Smith

Adrián López Flores

Distribución de las tareas:

Jorge: creador de la idea del simón dice y principal encargado del audio del programa, el cual desarrolló el mecanismo de descargar e importar audio, definiendo la función (no me acuerdo) y creando un miniprograma con el que descargar el audio de los vídeos de YouTube.

Santi: principal ideador de mejoras, betatester (es decir, que estaba viendo que la mitad del código iba de pena y que había que echarle la bronca al Gemini por ser tan malo picando código) y bueno, en resumen, el que vio la forma de que la estructura del programa no se cayera a pedazos.

Adrián: principal prompt engineer de IA (me he leído el código, no te creas que he hecho copy-paste durante horas, que también, pero que luego lo estaba viendo), preocupado siempre por la modularidad, la eficiencia, la limpieza y la claridad del código.

Inicialmente Jorge propuso la idea del simón dice pero, para asegurarnos de que la idea era la mejor posible , exploramos otras posibilidades (mentira, Adrián se puso cabezón e insistió en que probáramos a hacer una lluvia de ideas), como fueron un simulador de las físicas de un cañón tipo Angry Birds (con objetivo móvil y ajuste de parámetros y de UI) y también un ajedrez. Ambos los dejamos de lado (o quizá alguno de nosotros los rescata para el proyecto individual) y procedimos a continuar con el simón dice. En un primer lugar era un simple boceto hecho por IA, funcional pero todavía muy verde.








El audio nos supuso un problema bastante extenso de desarrollar, puesto que éste comenzó como un simple winsound de una única frecuencia (vamos, peor que un videojuego de la NES y esas máquinas apenas y tenían unos kilobytes de memoria para cargar un juego entero, cómo se notaba cuando los programadores eran maestros de la eficiencia). Luego nos dimos cuenta de que era una tremenda basura y que debíamos de descartarlo. Tras batallar para meter el audio en el programa (tuvimos que hacer un código para poder descargar los archivos), nos dimos cuenta que de pronto el programa se había convertido en un dolor de cabeza de usar. Básicamente era como meterse en la mente de una persona con TDAH a vivir, sonidos estridentes por todas partes e impulsos continuos de falta de tiempo, de tensión... Un caos. Bueno, pues tocó abortar misión por segunda vez, y ahora nos toca hacerlo una tercera (esta vez sin tanto estímulo, que sino va a parecer más un TikTok que un juego per se).








ESTO ES IA, PERO POR SI OS SIRVE PARA REDACTAR ALGO INTERESANTE

🤡 Simón Dice: Final Edition

¡Bienvenido a Simón Dice: Final Edition! Una reimaginación moderna y desafiante del clásico juego infantil, desarrollada en Python utilizando Tkinter y una arquitectura modular robusta.

Este proyecto no se trata de luces y colores, sino de velocidad mental, cálculo rápido y cultura general, todo bajo la presión de un temporizador implacable y la constante duda de: ¿Lo dijo Simón?

🚀 Características Principales

Arquitectura Modular (MVC): Código limpio y organizado, separando la lógica del juego, la interfaz gráfica y la gestión de datos.

Configuración Externa (JSON): Todos los datos del juego (preguntas, capitales, configuración de ventana) se cargan desde archivos .json, permitiendo modificar el juego sin tocar el código fuente.

Sistema de Audio Dinámico:

Música de fondo que cambia según el contexto (países específicos).

Efectos de sonido para tensión ("hurry up"), victoria y derrota.

Gestor de sonido robusto basado en pygame.

Procesamiento de Texto Inteligente: El juego es capaz de entender respuestas con o sin tilde y en mayúsculas o minúsculas (ej: "Perú" = "peru").

Desafíos Variados:

🧮 Matemáticas: Sumas rápidas.

⌨️ Escritura: Velocidad de mecanografía.

🌍 Geografía: Capitales del mundo (con eventos de audio especiales para España, Perú y Japón).

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