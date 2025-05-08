import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import threading
import re
from datetime import datetime

class ConversorMTS:
    def __init__(self, ventana):
        self.ventana = ventana
        self.ventana.title("Conversor MTS a MP4")
        self.ventana.geometry("600x300")
        self.ventana.resizable(False, False)

        self.entrada_var = tk.StringVar()
        self.salida_var = tk.StringVar()
        self.crf_var = tk.StringVar(value="23")
        self.preset_var = tk.StringVar(value="medium")
        self.conversion_activa = False
        self.duracion_total = 0

        self.crear_interfaz()

    def crear_interfaz(self):
        main_frame = tk.Frame(self.ventana, padx=10, pady=10)
        main_frame.pack(fill=tk.BOTH, expand=True)

        tk.Label(main_frame, text="Archivo MTS de entrada:").grid(row=0, column=0, sticky="w")
        entrada_frame = tk.Frame(main_frame)
        entrada_frame.grid(row=1, column=0, columnspan=3, sticky="ew")
        tk.Entry(entrada_frame, textvariable=self.entrada_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(entrada_frame, text="Examinar", command=self.seleccionar_archivo).pack(side=tk.LEFT, padx=5)

        tk.Label(main_frame, text="Archivo MP4 de salida:").grid(row=2, column=0, sticky="w", pady=(10,0))
        salida_frame = tk.Frame(main_frame)
        salida_frame.grid(row=3, column=0, columnspan=3, sticky="ew")
        tk.Entry(salida_frame, textvariable=self.salida_var, width=50).pack(side=tk.LEFT, fill=tk.X, expand=True)
        tk.Button(salida_frame, text="Guardar como", command=self.seleccionar_destino).pack(side=tk.LEFT, padx=5)

        options_frame = tk.LabelFrame(main_frame, text="Opciones de Conversión", padx=5, pady=5)
        options_frame.grid(row=4, column=0, columnspan=3, sticky="ew", pady=(10,0))

        tk.Label(options_frame, text="Calidad (CRF):").grid(row=0, column=0, sticky="w")
        tk.Spinbox(options_frame, from_=18, to=28, textvariable=self.crf_var, width=5).grid(row=0, column=1, sticky="w", padx=(0,20))

        tk.Label(options_frame, text="Preset:").grid(row=0, column=2, sticky="w")
        tk.OptionMenu(options_frame, self.preset_var, "ultrafast", "superfast", "veryfast", "faster", "fast", "medium", "slow", "slower", "veryslow").grid(row=0, column=3, sticky="w")

        self.progress = ttk.Progressbar(main_frame, orient="horizontal", length=500, mode="determinate")
        self.progress.grid(row=5, column=0, columnspan=3, pady=(15,5))

        btn_frame = tk.Frame(main_frame)
        btn_frame.grid(row=6, column=0, columnspan=3, pady=(10,0))

        self.btn_convertir = tk.Button(btn_frame, text="Convertir", command=self.convertir, bg="green", fg="white", width=10)
        self.btn_convertir.pack(side=tk.LEFT, padx=5)

        self.btn_cancelar = tk.Button(btn_frame, text="Cancelar", command=self.cancelar_conversion, state=tk.DISABLED, width=10)
        self.btn_cancelar.pack(side=tk.LEFT, padx=5)

        tk.Button(btn_frame, text="Abrir Carpeta", command=self.abrir_carpeta, width=10).pack(side=tk.LEFT, padx=5)

    def seleccionar_archivo(self):
        archivo = filedialog.askopenfilename(title="Seleccionar archivo MTS", filetypes=[("Archivos MTS", "*.mts")])
        if archivo:
            self.entrada_var.set(archivo)
            nombre_base = os.path.splitext(os.path.basename(archivo))[0]
            carpeta = os.path.dirname(archivo)
            fecha = datetime.now().strftime("%Y%m%d_%H%M%S")
            self.salida_var.set(os.path.join(carpeta, f"{nombre_base}_converted_{fecha}.mp4"))

    def seleccionar_destino(self):
        archivo = filedialog.asksaveasfilename(defaultextension=".mp4", filetypes=[("Archivos MP4", "*.mp4")])
        if archivo:
            self.salida_var.set(archivo)

    def verificar_ffmpeg(self):
        try:
            subprocess.run(["ffmpeg", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            subprocess.run(["ffprobe", "-version"], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            return True
        except FileNotFoundError:
            return False

    def obtener_duracion(self, archivo):
        try:
            resultado = subprocess.run(
                ["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "default=noprint_wrappers=1:nokey=1", archivo],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )
            duracion = float(resultado.stdout.strip())
            return duracion
        except Exception:
            return 0

    def convertir(self):
        entrada = self.entrada_var.get()
        salida = self.salida_var.get()

        if not entrada or not os.path.exists(entrada):
            messagebox.showerror("Error", "Archivo de entrada no válido.")
            return
        if not salida:
            messagebox.showerror("Error", "No se especificó un archivo de salida.")
            return
        if not self.verificar_ffmpeg():
            messagebox.showerror("Error", "FFmpeg o ffprobe no están disponibles.")
            return

        self.duracion_total = self.obtener_duracion(entrada)
        if self.duracion_total <= 0:
            messagebox.showerror("Error", "No se pudo obtener la duración del archivo.")
            return

        self.conversion_activa = True
        self.progress["value"] = 0
        self.btn_convertir.config(state=tk.DISABLED)
        self.btn_cancelar.config(state=tk.NORMAL)

        threading.Thread(target=self.ejecutar_conversion, daemon=True).start()

    def ejecutar_conversion(self):
        entrada = self.entrada_var.get()
        salida = self.salida_var.get()
        crf = self.crf_var.get()
        preset = self.preset_var.get()

        comando = [
            "ffmpeg",
            "-i", entrada,
            "-c:v", "libx264",
            "-crf", crf,
            "-preset", preset,
            "-c:a", "aac",
            "-b:a", "192k",
            "-y",
            salida
        ]

        try:
            proceso = subprocess.Popen(comando, stderr=subprocess.PIPE, universal_newlines=True)

            for linea in proceso.stderr:
                if not self.conversion_activa:
                    proceso.terminate()
                    break

                match = re.search(r'time=(\d+):(\d+):(\d+.\d+)', linea)
                if match:
                    h, m, s = map(float, match.groups())
                    segundos = h * 3600 + m * 60 + s
                    porcentaje = (segundos / self.duracion_total) * 100
                    self.progress["value"] = min(100, porcentaje)

            proceso.wait()

            if self.conversion_activa and proceso.returncode == 0:
                self.ventana.after(0, lambda: messagebox.showinfo("Éxito", f"Conversión completada:\n{salida}"))
            elif self.conversion_activa:
                self.ventana.after(0, lambda: messagebox.showerror("Error", "La conversión falló."))

        except Exception as e:
            self.ventana.after(0, lambda: messagebox.showerror("Error", str(e)))
        finally:
            self.ventana.after(0, self.finalizar_conversion)

    def cancelar_conversion(self):
        self.conversion_activa = False
        self.btn_cancelar.config(state=tk.DISABLED)

    def finalizar_conversion(self):
        self.progress["value"] = 0
        self.btn_convertir.config(state=tk.NORMAL)
        self.btn_cancelar.config(state=tk.DISABLED)
        self.conversion_activa = False

    def abrir_carpeta(self):
        salida = self.salida_var.get()
        if salida:
            carpeta = os.path.dirname(salida)
            if os.path.exists(carpeta):
                try:
                    if os.name == 'nt':
                        os.startfile(carpeta)
                    else:
                        subprocess.Popen(["xdg-open", carpeta])
                except Exception as e:
                    messagebox.showerror("Error", f"No se pudo abrir la carpeta:\n{str(e)}")
            else:
                messagebox.showerror("Error", "La carpeta no existe.")

if __name__ == "__main__":
    ventana = tk.Tk()
    app = ConversorMTS(ventana)
    ventana.mainloop()
