import cv2
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from funcionhistograma import aplicar_expansion, aplicar_ecualizacion
from graficador import generar_figura_resultados


class AplicacionProcesamiento:
    def __init__(self, root):
        self.root = root
        self.root.title("Transformaciones de Histograma")
        self.root.geometry("450x260")
        self.root.resizable(False, False)

        self.ruta_imagen = None
        self.crear_interfaz()

    def crear_interfaz(self):
        marco = ttk.Frame(self.root, padding="20")
        marco.pack(fill=tk.BOTH, expand=True)

        ttk.Label(marco, text="1. Selecciona una imagen:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        marco_archivo = ttk.Frame(marco)
        marco_archivo.pack(fill=tk.X, pady=(0, 10))

        self.btn_buscar = ttk.Button(marco_archivo, text="Buscar Archivo...", command=self.seleccionar_archivo)
        self.btn_buscar.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_ruta = ttk.Label(marco_archivo, text="Ningún archivo seleccionado", foreground="gray")
        self.lbl_ruta.pack(side=tk.LEFT, fill=tk.X, expand=True)

        ttk.Label(marco, text="2. Selecciona el método:", font=("Arial", 10, "bold")).pack(anchor=tk.W, pady=(0, 5))
        self.opcion_metodo = tk.StringVar(value="Expansion")

        ttk.Radiobutton(marco, text="Expansión de Histograma", variable=self.opcion_metodo, value="Expansion").pack(
            anchor=tk.W)

        marco_rango = ttk.Frame(marco)
        marco_rango.pack(fill=tk.X, pady=(0, 5), padx=(20, 0))

        ttk.Label(marco_rango, text="Rango de salida s1:").pack(side=tk.LEFT)
        self.entry_s1 = ttk.Entry(marco_rango, width=5)
        self.entry_s1.insert(0, "0")
        self.entry_s1.pack(side=tk.LEFT, padx=(5, 15))

        ttk.Label(marco_rango, text="s2:").pack(side=tk.LEFT)
        self.entry_s2 = ttk.Entry(marco_rango, width=5)
        self.entry_s2.insert(0, "255")
        self.entry_s2.pack(side=tk.LEFT, padx=(5, 0))

        ttk.Radiobutton(marco, text="Ecualización de Histograma", variable=self.opcion_metodo,
                        value="Ecualizacion").pack(anchor=tk.W, pady=(5, 15))

        self.btn_procesar = ttk.Button(marco, text="Procesar y Mostrar Resultados", command=self.ejecutar_proceso,
                                       state=tk.DISABLED)
        self.btn_procesar.pack(fill=tk.X)

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
                img_original = img_raw
        else:
            return

        metodo = self.opcion_metodo.get()
        if metodo == "Expansion":
            try:
                s1_val = int(self.entry_s1.get())
                s2_val = int(self.entry_s2.get())

                if s1_val < 0 or s2_val > 255 or s1_val >= s2_val:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error de Rango",
                                     "s1 y s2 deben ser enteros entre 0 y 255. Además s1 debe ser menor que s2.")
                return

            img_procesada, datos_matematicos = aplicar_expansion(img_original, s1=s1_val, s2=s2_val)
            titulo = f"Expansión"
        else:
            img_procesada, datos_matematicos = aplicar_ecualizacion(img_original)
            titulo = "Ecualización"

        figura = generar_figura_resultados(img_original, img_procesada, titulo)
        self.mostrar_ventana_resultados(figura, datos_matematicos)

    def mostrar_ventana_resultados(self, figura, datos_matematicos):
        ventana_graficos = tk.Toplevel(self.root)
        ventana_graficos.title(f"Resultados Visuales - {datos_matematicos['tipo'].capitalize()}")

        canvas = FigureCanvasTkAgg(figura, master=ventana_graficos)
        canvas.draw()
        canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        marco_boton = ttk.Frame(ventana_graficos, padding="10")
        marco_boton.pack(side=tk.BOTTOM, fill=tk.X)

        btn_tabla = ttk.Button(
            marco_boton,
            text="Visualizar Calculo de los Pixeles",
            command=lambda: self.mostrar_tabla_ventana(datos_matematicos, ventana_graficos)
        )
        btn_tabla.pack(fill=tk.X, expand=True)

    def mostrar_tabla_ventana(self, datos_matematicos, ventana_padre):
        if not datos_matematicos:
            return

        ventana_tabla = tk.Toplevel(ventana_padre)
        ventana_tabla.title(f"Calculo: {datos_matematicos['tipo'].capitalize()}")
        ventana_tabla.geometry("750x400")

        scroll_y = ttk.Scrollbar(ventana_tabla, orient=tk.VERTICAL)

        if datos_matematicos["tipo"] == "ecualizacion":
            columnas = ("r_k", "p_r", "calculo", "s_k", "p_s")
            tree = ttk.Treeview(ventana_tabla, columns=columnas, show="headings", yscrollcommand=scroll_y.set)

            tree.heading("r_k", text="Nivel Orig. (r_k)")
            tree.heading("p_r", text="p_r(r_k)")
            tree.heading("calculo", text="Fórmula S_k")
            tree.heading("s_k", text="Nuevo Nivel (s_k)")
            tree.heading("p_s", text="p_s(s_k)")

            tree.column("r_k", width=100, anchor=tk.CENTER)
            tree.column("p_r", width=140, anchor=tk.CENTER)
            tree.column("calculo", width=200, anchor=tk.CENTER)
            tree.column("s_k", width=120, anchor=tk.CENTER)
            tree.column("p_s", width=140, anchor=tk.CENTER)
        else:
            columnas = ("r", "calculo", "s")
            tree = ttk.Treeview(ventana_tabla, columns=columnas, show="headings", yscrollcommand=scroll_y.set)

            tree.heading("r", text="Nivel Orig. (r)")
            tree.heading("calculo", text="Fórmula T(r)")
            tree.heading("s", text="Nuevo Nivel (s)")

            tree.column("r", width=120, anchor=tk.CENTER)
            tree.column("calculo", width=400, anchor=tk.CENTER)
            tree.column("s", width=120, anchor=tk.CENTER)

        scroll_y.config(command=tree.yview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        for fila in datos_matematicos["tabla"]:
            tree.insert("", tk.END, values=fila)


if __name__ == "__main__":
    ventana = tk.Tk()
    app = AplicacionProcesamiento(ventana)
    ventana.mainloop()