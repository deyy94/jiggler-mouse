"""
Mouse Jiggler - Evita que la PC se bloquee por inactividad
Usa tres métodos simultáneos:
  1. SetThreadExecutionState (Windows API) — le dice al SO que no apague pantalla
  2. Movimiento sutil del mouse
  3. Press de tecla Shift (inofensiva) como fallback
Requiere: pip install pyautogui
"""

import pyautogui
import time
import random
import threading
import sys
import platform

# ── Windows: SetThreadExecutionState ─────────────────────────────────────────
IS_WINDOWS = platform.system() == "Windows"
IS_MAC     = platform.system() == "Darwin"

_ES_CONTINUOUS        = 0x80000000
_ES_SYSTEM_REQUIRED   = 0x00000001
_ES_DISPLAY_REQUIRED  = 0x00000002

def _prevent_sleep_windows(enable: bool):
    """Llama a SetThreadExecutionState para bloquear el apagado de pantalla."""
    try:
        import ctypes
        if enable:
            ctypes.windll.kernel32.SetThreadExecutionState(
                _ES_CONTINUOUS | _ES_SYSTEM_REQUIRED | _ES_DISPLAY_REQUIRED
            )
        else:
            ctypes.windll.kernel32.SetThreadExecutionState(_ES_CONTINUOUS)
    except Exception:
        pass

# ── Intenta importar tkinter para la GUI ──────────────────────────────────────
try:
    import tkinter as tk
    from tkinter import ttk
    HAS_GUI = True
except ImportError:
    HAS_GUI = False

# ── Configuración de pyautogui ────────────────────────────────────────────────
pyautogui.FAILSAFE = True   # Mover mouse a esquina superior-izquierda = parar
pyautogui.PAUSE = 0.05

# ══════════════════════════════════════════════════════════════════════════════
#  LÓGICA DEL JIGGLER
# ══════════════════════════════════════════════════════════════════════════════

class Jiggler:
    """
    Mantiene la PC despierta usando tres métodos simultáneos:
      1. SetThreadExecutionState (Windows) — nivel de SO
      2. Movimiento sutil del mouse
      3. Pulsación de Shift — señal de actividad de teclado
    """

    def __init__(self):
        self.running = False
        self._thread: threading.Thread | None = None
        self.interval = 60        # segundos entre acciones
        self.distance = 5         # píxeles de desplazamiento
        self.move_count = 0
        self.method_log = ""      # último método usado

    def _jiggle_loop(self):
        # Método 1: decirle al SO que no apague la pantalla (Windows)
        if IS_WINDOWS:
            _prevent_sleep_windows(True)

        while self.running:
            try:
                # Método 2: mover el mouse sutilmente y regresar
                dx = random.choice([-1, 1]) * self.distance
                dy = random.choice([-1, 1]) * self.distance
                pyautogui.moveRel(dx, dy, duration=0.3)
                time.sleep(0.15)
                pyautogui.moveRel(-dx, -dy, duration=0.3)

                # Método 3: presionar Shift (no escribe nada, solo activa input)
                pyautogui.press('shift')

                self.move_count += 1
                self.method_log = f"mouse±{self.distance}px + shift"

            except pyautogui.FailSafeException:
                self.running = False
                break
            except Exception:
                pass

            # Esperar el intervalo en fragmentos pequeños
            for _ in range(self.interval * 10):
                if not self.running:
                    break
                time.sleep(0.1)

        # Liberar el bloqueo de SO al detenerse
        if IS_WINDOWS:
            _prevent_sleep_windows(False)

    def start(self):
        if not self.running:
            self.running = True
            self._thread = threading.Thread(target=self._jiggle_loop, daemon=True)
            self._thread.start()

    def stop(self):
        self.running = False

    def is_running(self):
        return self.running


# ══════════════════════════════════════════════════════════════════════════════
#  INTERFAZ GRÁFICA
# ══════════════════════════════════════════════════════════════════════════════

class JigglerApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.jiggler = Jiggler()
        self._build_ui()
        self._update_loop()

    # ── Construcción de la UI ─────────────────────────────────────────────────
    def _build_ui(self):
        root = self.root
        root.title("🖱 Mouse Jiggler")
        root.geometry("360x450")
        root.resizable(False, False)
        root.configure(bg="#0f0f14")

        try:
            icon_image = tk.PhotoImage(file="icon.png")
            root.iconphoto(False, icon_image)
        except Exception:
            pass

        # ── Título ──
        tk.Label(
            root, text="MOUSE JIGGLER",
            font=("Courier", 16, "bold"),
            fg="#7DF9AA", bg="#0f0f14"
        ).pack(pady=(24, 2))



        # ── Indicador de estado ──
        self.status_frame = tk.Frame(root, bg="#0f0f14")
        self.status_frame.pack(pady=4)

        self.dot = tk.Label(
            self.status_frame, text="●",
            font=("Courier", 18),
            fg="#333", bg="#0f0f14"
        )
        self.dot.pack(side="left", padx=(0, 8))

        self.status_lbl = tk.Label(
            self.status_frame, text="INACTIVO",
            font=("Courier", 13, "bold"),
            fg="#555", bg="#0f0f14"
        )
        self.status_lbl.pack(side="left")

        # ── Contador ──
        self.count_lbl = tk.Label(
            root, text="Acciones: 0",
            font=("Courier", 10),
            fg="#444", bg="#0f0f14"
        )
        self.count_lbl.pack(pady=(4, 4))

        # Métodos activos
        methods = "🖥 SetThreadExecState  🖱 Mouse  ⌨ Shift key" if IS_WINDOWS else "🖱 Mouse  ⌨ Shift key"
        tk.Label(
            root, text=methods,
            font=("Courier", 8),
            fg="#2a6644", bg="#0f0f14"
        ).pack(pady=(0, 14))

        # ── Separador ──
        ttk.Separator(root, orient="horizontal").pack(fill="x", padx=30, pady=4)

        # ── Configuración: Intervalo ──
        cfg_frame = tk.Frame(root, bg="#0f0f14")
        cfg_frame.pack(pady=12, fill="x", padx=40)

        tk.Label(cfg_frame, text="Intervalo (seg):", font=("Courier", 10),
                 fg="#888", bg="#0f0f14").grid(row=0, column=0, sticky="w", pady=4)
        self.interval_var = tk.IntVar(value=60)
        interval_spin = tk.Spinbox(
            cfg_frame, from_=10, to=300, increment=10,
            textvariable=self.interval_var, width=6,
            font=("Courier", 10), bg="#1a1a22", fg="#7DF9AA",
            buttonbackground="#1a1a22", relief="flat",
            insertbackground="#7DF9AA"
        )
        interval_spin.grid(row=0, column=1, padx=(12, 0), sticky="w")

        # ── Configuración: Distancia ──
        tk.Label(cfg_frame, text="Distancia (px):", font=("Courier", 10),
                 fg="#888", bg="#0f0f14").grid(row=1, column=0, sticky="w", pady=4)
        self.distance_var = tk.IntVar(value=5)
        distance_spin = tk.Spinbox(
            cfg_frame, from_=1, to=50, increment=1,
            textvariable=self.distance_var, width=6,
            font=("Courier", 10), bg="#1a1a22", fg="#7DF9AA",
            buttonbackground="#1a1a22", relief="flat",
            insertbackground="#7DF9AA"
        )
        distance_spin.grid(row=1, column=1, padx=(12, 0), sticky="w")

        # ── Botón principal ──
        ttk.Separator(root, orient="horizontal").pack(fill="x", padx=30, pady=(12, 4))

        self.btn = tk.Button(
            root, text="▶  INICIAR",
            font=("Courier", 12, "bold"),
            bg="#7DF9AA", fg="#0f0f14",
            activebackground="#5dcf88", activeforeground="#0f0f14",
            relief="flat", padx=20, pady=10, cursor="hand2",
            command=self._toggle
        )
        self.btn.pack(pady=18, ipadx=20)

        # ── Nota de seguridad ──
        tk.Label(
            root,
            text="💡 Mueve el cursor a la esquina sup-izq para detener",
            font=("Courier", 8), fg="#333", bg="#0f0f14", wraplength=300
        ).pack(pady=(5, 10))

    # ── Lógica de toggle ─────────────────────────────────────────────────────
    def _toggle(self):
        if self.jiggler.is_running():
            self.jiggler.stop()
            self.btn.config(text="▶  INICIAR", bg="#7DF9AA", fg="#0f0f14")
            self.status_lbl.config(text="INACTIVO", fg="#555")
            self.dot.config(fg="#333")
        else:
            # Aplicar configuración antes de iniciar
            self.jiggler.interval = max(10, self.interval_var.get())
            self.jiggler.distance = max(1, self.distance_var.get())
            self.jiggler.start()
            self.btn.config(text="⏹  DETENER", bg="#FF6B6B", fg="#fff")
            self.status_lbl.config(text="ACTIVO", fg="#7DF9AA")
            self.dot.config(fg="#7DF9AA")

    # ── Loop de actualización del contador ───────────────────────────────────
    def _update_loop(self):
        self.count_lbl.config(text=f"Acciones realizadas: {self.jiggler.move_count}")
        # Si el jiggler se detuvo por failsafe, actualizar UI
        if not self.jiggler.is_running() and self.btn.cget("text") == "⏹  DETENER":
            self.btn.config(text="▶  INICIAR", bg="#7DF9AA", fg="#0f0f14")
            self.status_lbl.config(text="INACTIVO", fg="#555")
            self.dot.config(fg="#333")
        self.root.after(500, self._update_loop)


# ══════════════════════════════════════════════════════════════════════════════
#  MODO CONSOLA (si no hay tkinter)
# ══════════════════════════════════════════════════════════════════════════════

def run_console():
    jiggler = Jiggler()
    print("\n🖱  Mouse Jiggler — Modo consola")
    print("─" * 40)

    try:
        interval = int(input("Intervalo en segundos (default 60): ").strip() or "60")
        distance = int(input("Distancia en píxeles   (default 5):  ").strip() or "5")
    except ValueError:
        interval, distance = 60, 5

    jiggler.interval = interval
    jiggler.distance = distance
    jiggler.start()

    print(f"\n✅ Jiggler activo — cada {interval}s, {distance}px")
    print("   Presiona Ctrl+C para detener\n")

    try:
        while True:
            time.sleep(1)
            sys.stdout.write(f"\r   Movimientos: {jiggler.move_count}   ")
            sys.stdout.flush()
    except KeyboardInterrupt:
        jiggler.stop()
        print("\n\n🛑 Jiggler detenido.")


# ══════════════════════════════════════════════════════════════════════════════
#  ENTRY POINT
# ══════════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    if HAS_GUI:
        root = tk.Tk()
        app = JigglerApp(root)
        root.mainloop()
    else:
        run_console()
