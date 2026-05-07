# main.py
import cv2
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from funcionhistograma import aplicar_expansion, aplicar_ecualizacion
from graficador import mostrar_resultados


class AplicacionProcesamiento:
    def __init__(self, root):
        self.root = root
        self.root.title("Procesamiento de Imágenes MA475")
        self.root.geometry("450x250")
        self.root.resizable(False, False)

        self.ruta_imagen = None
        self.crear_interfaz()

    def crear_interfaz(self):
        marco = ttk.Frame(self.root, padding="20")
        marco.pack(fill=tk.BOTH, expand=True)

        # Sección 1: Búsqueda de archivo
        ttk.Label(marco, text="1. Selecciona una imagen:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        marco_archivo = ttk.Frame(marco)
        marco_archivo.pack(fill=tk.X, pady=(0, 15))

        self.btn_buscar = ttk.Button(marco_archivo, text="Buscar Archivo...", command=self.seleccionar_archivo)
        self.btn_buscar.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_ruta = ttk.Label(marco_archivo, text="Ningún archivo seleccionado", foreground="gray")
        self.lbl_ruta.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(marco, text="2. Selecciona el método:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))

        self.opcion_metodo = tk.StringVar(value="Expansion")

        ttk.Radiobutton(marco, text="Expansión de Histograma (Estiramiento)", variable=self.opcion_metodo,
                        value="Expansion").pack(anchor=tk.W)
        ttk.Radiobutton(marco, text="Ecualización de Histograma", variable=self.opcion_metodo,
                        value="Ecualizacion").pack(anchor=tk.W, pady=(0, 15))

        self.btn_procesar = ttk.Button(marco, text="Procesar y Mostrar", command=self.ejecutar_proceso,
                                       state=tk.DISABLED)
        self.btn_procesar.pack(fill=tk.X, pady=10)

    def seleccionar_archivo(self):
        tipos = [("Imágenes", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"), ("Todos los archivos", "*.*")]
        ruta = filedialog.askopenfilename(title="Seleccionar Imagen", filetypes=tipos)

        if ruta:
            self.ruta_imagen = ruta
            self.lbl_ruta.config(text=os.path.basename(ruta), foreground="black")
            self.btn_procesar.config(state=tk.NORMAL)

    def ejecutar_proceso(self):
        if not self.ruta_imagen or not os.path.exists(self.ruta_imagen):
            messagebox.showerror("Error", "Ruta inválida.")
            return

        img_raw = cv2.imread(self.ruta_imagen, cv2.IMREAD_UNCHANGED)

        if img_raw is None:
            messagebox.showerror("Error", "El archivo no se pudo leer correctamente.")
            return

        dimensiones = len(img_raw.shape)

        if dimensiones == 2:
            img_original = img_raw

        elif dimensiones == 3:
            num_canales = img_raw.shape[2]

            if num_canales == 3:
                img_original = cv2.cvtColor(img_raw, cv2.COLOR_BGR2GRAY)
            elif num_canales == 4:
                img_original = cv2.cvtColor(img_raw, cv2.COLOR_BGRA2GRAY)
            else:
                img_original = img_raw  # Caso de seguridad (raro)
        else:
            messagebox.showerror("Error", "Formato de imagen no soportado.")
            return

        metodo = self.opcion_metodo.get()
        if metodo == "Expansion":
            img_procesada = aplicar_expansion(img_original)
            titulo = "Expansión"
        else:
            img_procesada = aplicar_ecualizacion(img_original)
            titulo = "Ecualización"

        mostrar_resultados(img_original, img_procesada, titulo)


if __name__ == "__main__":
    ventana = tk.Tk()
    app = AplicacionProcesamiento(ventana)
    ventana.mainloop()