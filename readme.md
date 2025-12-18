
---

# 🤡 Simón Dice 

Un juego interactivo de "Simón Dice" desarrollado en Python con interfaz gráfica (Tkinter) y efectos de sonido (Pygame). El jugador debe seguir las instrucciones (cálculos matemáticos, capitales o escribir palabras) **solo si** "Simón lo dice".

## 📋 Requisitos del Sistema

* **Python 3.8** o superior.
* **Librerías necesarias:**
El proyecto requiere instalar `pygame` para la reproducción de efectos de sonido y música de fondo.
```bash
pip install pygame

```

## 🚀 Instalación y Ejecución

Sigue estos pasos para iniciar el juego:

1. **Descargar el proyecto:**
Clona el repositorio o descarga los archivos asegurándote de mantener la estructura de carpetas correcta.
2. **Verificar Assets:**
Asegúrate de que la carpeta `assets` contenga los archivos de audio `.mp3` necesarios para el juego.
3. **Ejecutar el juego:**
Inicia la aplicación desde la raíz del proyecto ejecutando el archivo principal:
```bash
python main.py

```

## 📂 Estructura del Proyecto

El proyecto se organiza en carpetas modulares para facilitar su mantenimiento:

```text
simon_dice/
│
├── 📂 assets/              # 🔊 Archivos de audio (.mp3)
├── 📂 data/                # 💾 Datos configurables (JSON)
│   ├── gamedata.json       # Base de datos de palabras y capitales
│   └── settings.json       # Configuración de ventana y sonidos
│
├── 📂 modules/             # 🧠 Código fuente modular
│   ├── logic.py            # Lógica del juego (puntuación y turnos)
│   ├── sound.py            # Motor de audio (mixer)
│   └── ui.py               # Interfaz gráfica (Tkinter)
│
├── config.py               # ⚙️ Rutas y carga de configuración
├── main.py                 # 🚀 Punto de entrada principal
└── simon_record.txt        # 🏆 Guarda el puntaje máximo localmente

```

## ⚙️ Personalización

Puedes editar los archivos JSON en la carpeta `data/` para modificar el juego a tu gusto:

* **`data/gamedata.json`**:
* `palabras`: Añade palabras nuevas para el modo escritura.
* `capitales`: Agrega nuevos países y sus respuestas.


* **`data/settings.json`**:
* `window`: Personaliza el título, el tamaño de la ventana o el color de fondo.
* `sounds`: Reasigna qué audio suena para cada evento (victoria, derrota, fondo).

## ✍️ Autores

Proyecto desarrollado en Python por:
**Jorge, Santi y Adrián**