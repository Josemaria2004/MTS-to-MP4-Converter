# Conversor MTS a MP4 (con Interfaz Gráfica)

Este es un programa de escritorio en Python que permite convertir archivos de video `.MTS` a `.MP4` usando **FFmpeg**, con una interfaz gráfica amigable desarrollada en **Tkinter**.

---

## 🎥 Características

- Conversión de archivos `.MTS` a `.MP4` con calidad ajustable
- Interfaz gráfica intuitiva (Tkinter)
- Barra de progreso de conversión
- Botón para abrir la carpeta del archivo convertido
- Parámetros configurables:
  - CRF (calidad del video)
  - Preset (velocidad de compresión)

---

## 🚀 Requisitos

- Python 3.8 o superior
- FFmpeg instalado y agregado al PATH del sistema

---

## ⚙️ Instalación

1. Clona el repositorio:

```bash
git clone https://github.com/Josemaria2004/conversor-mts-gui.git
cd conversor-mts-gui
```

2. Instala PyInstaller si quieres generar un `.exe`:

```bash
pip install pyinstaller
```

3. Ejecuta la aplicación (modo desarrollo):

```bash
python conversor_mts_gui.py
```

---

## 🛠️ Generar ejecutable `.exe`

```bash
pyinstaller --onefile --noconsole --icon=icono.ico conversor_mts_gui.py
```

El archivo `.exe` se generará en la carpeta `/dist`.

---

## 📄 Licencia

Este proyecto está licenciado bajo la [MIT License](LICENSE).

---

## 🙋‍♂️ Autor

Desarrollado por [Jose Maria](https://github.com/Josemaria2004)
