# Mouse Jiggler 🖱

Mouse Jiggler es una sencilla pero potente utilidad para evitar que tu PC se bloquee y entre en suspensión por inactividad.

## Características

La aplicación mantiene tu equipo despierto empleando **tres métodos simultáneos**, asegurando máxima fiabilidad:
1. **Windows API (`SetThreadExecutionState`)**: Le indica directamente al sistema operativo que no apague la pantalla ni suspenda el sistema.
2. **Movimiento sutil del Mouse**: Mueve imperceptiblemente el cursor (por defecto 5 píxeles) y lo regresa a su posición original.
3. **Tecla fantasma (Shift)**: Simula una pulsación de la tecla `Shift`, lo que activa los eventos del teclado en el SO sin escribir ningún carácter ni afectar tu trabajo.

## Requisitos

Si se va a ejecutar desde el código fuente nativo:
- Python 3.10 o superior
- Módulos adicionales en el entorno virtual (ver [Instalación desde código fuente](#instalación-desde-código-fuente)).

## Instalación desde versión liberada (Release)

Si ya descargaste o generaste la versión compilada:
1. Navega hasta la carpeta `dist/MouseJiggler`.
2. Haz doble clic en el archivo `MouseJiggler.exe`.
3. Eso es todo, no se requiere instalación adicional.

## Instalación desde código fuente

Si prefieres ejecutar o modificar el código fuente:

1. Clona o descarga el repositorio en tu máquina.
2. Abre una terminal y navega hasta el directorio del proyecto.
3. Crea y activa un entorno virtual:
   ```bash
   python -m venv venv
   # En Windows:
   .\venv\Scripts\activate
   ```
4. Instala las dependencias necesarias:
   ```bash
   pip install pyautogui
   ```
   *(Opcional) Si quieres compilar tu propio ejecutable con su propio icono, necesitas dependencias extra:*
   ```bash
   pip install pyinstaller Pillow
   ```
5. Inicia el programa:
   ```bash
   python main.py
   ```

## Uso

1. Al abrir la aplicación, verás una pequeña interfaz gráfica.
2. Puedes ajustar el **Intervalo (en segundos)** entre cada acción (por defecto 60 segundos).
3. Puedes ajustar la **Distancia** del movimiento del mouse en píxeles (por defecto 5 px).
4. Presiona el botón **▶ INICIAR**. El indicador de estado cambiará a verde.
5. Para detener el programa, presiona **⏹ DETENER**, o como medida de seguridad, simplemente **mueve manualmente el ratón rápidamente a la esquina superior izquierda de tu pantalla** (Fail Safe).

---
*Icono del ratoncito generado algorítmicamente para hacer tus esquivas de inactividad más divertidas.* 🐭✨
