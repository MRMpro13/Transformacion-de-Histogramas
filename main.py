import cv2
import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from typing import Optional

import numpy as np
import matplotlib
matplotlib.use("TkAgg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk

from funcionhistograma import aplicar_expansion, aplicar_ecualizacion
from graficador import generar_figura_resultados


class AplicacionProcesamiento:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Transformaciones de Histograma")
        self.root.geometry("950x700")
        self.root.minsize(800, 600)

        self._configurar_estilos()

        self.ruta_imagen: Optional[str] = None
        self.img_procesada: Optional[np.ndarray] = None
        self.datos_matematicos: Optional[dict] = None
        self.hist_orig: Optional[np.ndarray] = None
        self.hist_proc: Optional[np.ndarray] = None
        self.color_proceso: str = "#2ca02c"
        self.titulo: str = ""

        self._crear_interfaz()

    def _configurar_estilos(self) -> None:
        self.root.configure(background="#f0f0f0")
        COLOR_FONDO = "#f5f5f5"
        COLOR_FONDO_OSCURO = "#f0f0f0"
        COLOR_TEXTO = "#1f2937"
        COLOR_TEXTO_SEC = "#6b7280"
        COLOR_BORDE = "#d1d5db"

        estilo = ttk.Style()
        try:
            estilo.theme_use("vista")
        except tk.TclError:
            pass

        estilo.configure(".", font=("Segoe UI", 10), background=COLOR_FONDO)

        estilo.configure("TFrame", background=COLOR_FONDO)
        estilo.configure("TLabelframe", background=COLOR_FONDO, relief=tk.GROOVE, borderwidth=2)
        estilo.configure("TLabelframe.Label", font=("Segoe UI", 9, "bold"), background=COLOR_FONDO, foreground=COLOR_TEXTO)

        estilo.configure("Title.TLabel", font=("Segoe UI", 16, "bold"), foreground=COLOR_TEXTO, background=COLOR_FONDO_OSCURO)
        estilo.configure("Info.TLabel", font=("Segoe UI", 9), foreground=COLOR_TEXTO_SEC, background=COLOR_FONDO)

        estilo.configure("TEntry", font=("Segoe UI", 10), fieldbackground="#ffffff")
        estilo.configure("TCombobox", font=("Segoe UI", 10), fieldbackground="#ffffff")

        estilo.configure("TNotebook", background=COLOR_FONDO_OSCURO, borderwidth=0)
        estilo.configure("TNotebook.Tab", font=("Segoe UI", 10), padding=(14, 5))

        estilo.configure("Treeview", rowheight=28, font=("Consolas", 9), fieldbackground="#ffffff")
        estilo.configure("Treeview.Heading", font=("Segoe UI", 9, "bold"), background=COLOR_FONDO, foreground=COLOR_TEXTO)
        estilo.map("Treeview.Heading", background=[("active", "#e5e7eb")])
        estilo.map("Treeview", background=[("selected", "#bfdbfe")], foreground=[("selected", COLOR_TEXTO)])

        estilo.configure("TButton", font=("Segoe UI", 10), padding=(10, 5))

        estilo.configure("Procesar.TButton", font=("Segoe UI", 11, "bold"), padding=(16, 8))

        estilo.configure("Volver.TButton", font=("Segoe UI", 10), padding=(6, 3))
        estilo.configure("Guardar.TButton", font=("Segoe UI", 10, "bold"), padding=(10, 5))

    def _crear_interfaz(self) -> None:
        # === VISTA 1: INICIO ===
        self.marco_inicio = ttk.Frame(self.root, style="TFrame")
        self.marco_inicio.pack(fill=tk.BOTH, expand=True)

        # Centro vertical
        centro = ttk.Frame(self.marco_inicio, style="TFrame")
        centro.place(relx=0.5, rely=0.45, anchor=tk.CENTER)

        ttk.Label(
            centro, text="Transformaciones de Histograma",
            style="Title.TLabel"
        ).pack(pady=(0, 30))

        # -- Archivo --
        marco_archivo = ttk.LabelFrame(centro, text="Archivo", padding="12")
        marco_archivo.pack(fill=tk.X, pady=(0, 12))

        fila_archivo = ttk.Frame(marco_archivo, style="TFrame")
        fila_archivo.pack(fill=tk.X)

        self.btn_buscar = ttk.Button(fila_archivo, text="Buscar Archivo...", command=self.seleccionar_archivo)
        self.btn_buscar.pack(side=tk.LEFT, padx=(0, 10))

        self.lbl_ruta = ttk.Label(
            fila_archivo, text="Ningún archivo seleccionado",
            style="Info.TLabel", foreground="#9ca3af"
        )
        self.lbl_ruta.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.lbl_info_img = ttk.Label(fila_archivo, text="", style="Info.TLabel")
        self.lbl_info_img.pack(side=tk.RIGHT)

        # -- Método --
        marco_metodo = ttk.LabelFrame(centro, text="Método", padding="12")
        marco_metodo.pack(fill=tk.X, pady=(0, 12))

        fila_metodo = ttk.Frame(marco_metodo, style="TFrame")
        fila_metodo.pack(fill=tk.X)

        ttk.Label(fila_metodo, text="Tipo de transformación:", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 10))

        self.opcion_metodo = tk.StringVar()
        self.combo_metodo = ttk.Combobox(
            fila_metodo, textvariable=self.opcion_metodo,
            values=["Expansión de Histograma", "Ecualización de Histograma"],
            state="readonly", width=32, font=("Segoe UI", 10)
        )
        self.combo_metodo.current(0)
        self.combo_metodo.pack(side=tk.LEFT)

        # -- Rango (solo para expansión) --
        self.marco_rango = ttk.Frame(marco_metodo, style="TFrame")
        ttk.Label(self.marco_rango, text="Rango de salida", font=("Segoe UI", 10)).pack(side=tk.LEFT, padx=(0, 8))

        ttk.Label(self.marco_rango, text="Valor mínimo:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.entry_s1 = ttk.Entry(self.marco_rango, width=5, font=("Segoe UI", 10))
        self.entry_s1.insert(0, "0")
        self.entry_s1.pack(side=tk.LEFT, padx=(4, 12))

        ttk.Label(self.marco_rango, text="Valor máximo:", font=("Segoe UI", 10)).pack(side=tk.LEFT)
        self.entry_s2 = ttk.Entry(self.marco_rango, width=5, font=("Segoe UI", 10))
        self.entry_s2.insert(0, "255")
        self.entry_s2.pack(side=tk.LEFT, padx=(4, 0))

        self.opcion_metodo.trace_add("write", self._alternar_rango)
        self._alternar_rango()

        # -- Botón --
        self.btn_procesar = ttk.Button(
            centro, text="Aplicar Transformación",
            style="Procesar.TButton", command=self.ejecutar_proceso, state=tk.DISABLED
        )
        self.btn_procesar.pack(pady=(0, 6), ipadx=10, ipady=4)

        # === VISTA 2: RESULTADOS ===
        self.marco_resultados = ttk.Frame(self.root, style="TFrame")

        # Cabecera con botón volver
        cabecera = ttk.Frame(self.marco_resultados, style="TFrame", padding="10")
        cabecera.pack(fill=tk.X)

        self.btn_volver = ttk.Button(
            cabecera, text="← Nueva imagen", style="Volver.TButton",
            command=self._volver_inicio
        )
        self.btn_volver.pack(side=tk.LEFT)

        self.lbl_resultado_titulo = ttk.Label(
            cabecera, text="", font=("Segoe UI", 13, "bold"),
            foreground="#1f2937", background="#f5f5f5"
        )
        self.lbl_resultado_titulo.pack(side=tk.LEFT, padx=(15, 0))

        self.btn_guardar = ttk.Button(
            cabecera, text="Guardar Imagen", style="Guardar.TButton",
            command=self.guardar_imagen, state=tk.DISABLED
        )
        self.btn_guardar.pack(side=tk.RIGHT)

        # -- Notebook --
        self.notebook = ttk.Notebook(self.marco_resultados, padding=(4, 4, 4, 0))
        self.notebook.pack(fill=tk.BOTH, expand=True, padx=8, pady=(0, 5))

        # Pestaña Resultados
        self.tab_resultados = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.tab_resultados, text="Resultados")
        self.marco_figura = ttk.Frame(self.tab_resultados, style="TFrame")
        self.marco_figura.pack(fill=tk.BOTH, expand=True)
        self.canvas: Optional[FigureCanvasTkAgg] = None
        self.toolbar: Optional[NavigationToolbar2Tk] = None

        # Pestaña Comparación
        self.tab_comparacion = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.tab_comparacion, text="Comparación")
        self.marco_comparacion = ttk.Frame(self.tab_comparacion, style="TFrame")
        self.marco_comparacion.pack(fill=tk.BOTH, expand=True)
        self.lbl_comp_placeholder = ttk.Label(
            self.marco_comparacion, text="Procesa una imagen para ver la comparación",
            font=("Segoe UI", 13), foreground="#cccccc", anchor=tk.CENTER
        )
        self.lbl_comp_placeholder.pack(expand=True)
        self.canvas_comp: Optional[FigureCanvasTkAgg] = None
        self.toolbar_comp: Optional[NavigationToolbar2Tk] = None

        # Pestaña Cálculo
        self.tab_calculo = ttk.Frame(self.notebook, style="TFrame")
        self.notebook.add(self.tab_calculo, text="Cálculo")
        self.marco_calculo = ttk.Frame(self.tab_calculo, style="TFrame")
        self.marco_calculo.pack(fill=tk.BOTH, expand=True)
        self.lbl_calc_placeholder = ttk.Label(
            self.marco_calculo, text="Procesa una imagen para ver la tabla de cálculo",
            font=("Segoe UI", 13), foreground="#cccccc", anchor=tk.CENTER
        )
        self.lbl_calc_placeholder.pack(expand=True)

    def _alternar_rango(self, *_args: object) -> None:
        if self.opcion_metodo.get().startswith("Expansión"):
            self.marco_rango.pack(fill=tk.X, pady=(10, 0))
        else:
            self.marco_rango.pack_forget()

    def seleccionar_archivo(self) -> None:
        tipos = [
            ("Imágenes", "*.png *.jpg *.jpeg *.bmp *.tif *.tiff"),
            ("Todos los archivos", "*.*"),
        ]
        ruta = filedialog.askopenfilename(title="Seleccionar Imagen", filetypes=tipos)

        if ruta:
            self.ruta_imagen = ruta
            self.lbl_ruta.config(text=os.path.basename(ruta), foreground="#222222")
            img = cv2.imread(ruta, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                h, w = img.shape
                kb = os.path.getsize(ruta) / 1024
                self.lbl_info_img.config(text=f"{w} × {h} px  ·  {kb:.1f} KB")
            self.btn_procesar.config(state=tk.NORMAL)

    def _volver_inicio(self) -> None:
        self.marco_resultados.pack_forget()
        self.marco_inicio.pack(fill=tk.BOTH, expand=True)
        self.root.geometry("950x700")

    def _crear_canvas(self, marco: ttk.Frame, figura: plt.Figure) -> FigureCanvasTkAgg:
        for widget in marco.winfo_children():
            widget.destroy()
        canvas = FigureCanvasTkAgg(figura, master=marco)
        canvas.draw()
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        return canvas

    def _crear_toolbar(self, marco: ttk.Frame, canvas: FigureCanvasTkAgg) -> NavigationToolbar2Tk:
        toolbar = NavigationToolbar2Tk(canvas, marco)
        toolbar.update()
        toolbar.pack(side=tk.BOTTOM, fill=tk.X)
        return toolbar

    def _poblar_tab_comparacion(self) -> None:
        for w in self.marco_comparacion.winfo_children():
            w.destroy()

        fig, ax = plt.subplots(figsize=(9, 5), dpi=100)
        fig.patch.set_facecolor("#fafafa")

        ax.plot(self.hist_orig, color="#3a86ff", linewidth=1.8, alpha=0.85, label="Original")
        ax.fill_between(range(256), self.hist_orig.flatten(), color="#3a86ff", alpha=0.2)
        ax.plot(self.hist_proc, color=self.color_proceso, linewidth=1.8, alpha=0.85, label=self.titulo)
        ax.fill_between(range(256), self.hist_proc.flatten(), color=self.color_proceso, alpha=0.2)

        ax.set_title("Comparación de Histogramas", fontsize=13, fontweight="bold", pad=10)
        ax.set_xlim([0, 255])
        ax.set_ylim(bottom=0)
        ax.set_xlabel("Nivel de intensidad", fontsize=10, color="#444444")
        ax.set_ylabel("N° de píxeles", fontsize=10, color="#444444")
        ax.legend(fontsize=10, loc="upper right", framealpha=0.9, edgecolor="#cccccc")
        ax.grid(True, which="major", color="#e0e0e0", linestyle="-", linewidth=0.5)
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.tick_params(colors="#555555", labelsize=9)

        plt.tight_layout()

        self.canvas_comp = self._crear_canvas(self.marco_comparacion, fig)
        self.toolbar_comp = self._crear_toolbar(self.marco_comparacion, self.canvas_comp)

    def _poblar_tab_calculo(self) -> None:
        for w in self.marco_calculo.winfo_children():
            w.destroy()

        tipo = self.datos_matematicos["tipo"]
        tabla = self.datos_matematicos["tabla"]

        es_ecualizacion = tipo == "ecualizacion"
        if es_ecualizacion:
            columnas = ("r_k", "p_r", "calculo", "s_k", "p_s")
            encabezados = {
                "r_k": "Nivel Orig. (r_k)", "p_r": "p_r(r_k)",
                "calculo": "Fórmula S_k = 255·CDF",
                "s_k": "Nuevo Nivel (s_k)", "p_s": "p_s(s_k)",
            }
            anchos = {"r_k": 110, "p_r": 100, "calculo": 250, "s_k": 120, "p_s": 100}
        else:
            columnas = ("r", "calculo", "s")
            encabezados = {
                "r": "Nivel Orig. (r)", "calculo": "Fórmula T(r)", "s": "Nuevo Nivel (s)"
            }
            anchos = {"r": 130, "calculo": 450, "s": 130}

        scroll_y = ttk.Scrollbar(self.marco_calculo, orient=tk.VERTICAL)
        scroll_x = ttk.Scrollbar(self.marco_calculo, orient=tk.HORIZONTAL)

        tree = ttk.Treeview(
            self.marco_calculo, columns=columnas, show="headings",
            yscrollcommand=scroll_y.set, xscrollcommand=scroll_x.set,
        )

        for col in columnas:
            tree.heading(
                col, text=encabezados[col],
                command=lambda c=col: self._ordenar_tabla(tree, c, False)
            )
            tree.column(col, width=anchos[col], anchor=tk.CENTER, minwidth=70)

        tree.tag_configure("par", background="#f5f5f5")
        tree.tag_configure("impar", background="#ffffff")

        scroll_y.config(command=tree.yview)
        scroll_x.config(command=tree.xview)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)
        scroll_x.pack(side=tk.BOTTOM, fill=tk.X)
        tree.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 0))

        for i, fila in enumerate(tabla):
            tag = "par" if i % 2 == 0 else "impar"
            tree.insert("", tk.END, values=fila, tags=(tag,))

        marco_inf = ttk.Frame(self.marco_calculo, style="TFrame")
        marco_inf.pack(fill=tk.X, padx=10, pady=(8, 10))

        ttk.Label(
            marco_inf,
            text=f"Total: {len(tabla)} niveles  ·  Método: {'ecualización' if es_ecualizacion else 'expansión'}",
            font=("Segoe UI", 9), foreground="#666666",
        ).pack(side=tk.LEFT)

    def ejecutar_proceso(self) -> None:
        if not self.ruta_imagen or not os.path.exists(self.ruta_imagen):
            messagebox.showerror("Error", "Ruta inválida.")
            return

        img_raw = cv2.imread(self.ruta_imagen, cv2.IMREAD_GRAYSCALE)
        if img_raw is None:
            messagebox.showerror("Error", "El archivo no se pudo leer correctamente.")
            return

        metodo = "expansion" if self.opcion_metodo.get().startswith("Expansión") else "ecualizacion"
        if metodo == "expansion":
            try:
                s1_val = int(self.entry_s1.get())
                s2_val = int(self.entry_s2.get())
                if s1_val < 0 or s2_val > 255 or s1_val >= s2_val:
                    raise ValueError
            except ValueError:
                messagebox.showerror(
                    "Error de Rango",
                    "s1 y s2 deben ser enteros entre 0 y 255, y s1 debe ser menor que s2.",
                )
                return

            img_procesada, datos_matematicos = aplicar_expansion(img_raw, s1=s1_val, s2=s2_val)
            titulo = "Expansión"
        else:
            img_procesada, datos_matematicos = aplicar_ecualizacion(img_raw)
            titulo = "Ecualización"

        self.img_procesada = img_procesada
        self.datos_matematicos = datos_matematicos
        self.titulo = titulo
        self.color_proceso = "#d62728" if metodo == "ecualizacion" else "#2ca02c"

        # Pestaña Resultados
        figura, _, self.hist_orig, self.hist_proc = generar_figura_resultados(
            img_raw, self.img_procesada, titulo, color_proceso=self.color_proceso
        )
        self.canvas = self._crear_canvas(self.marco_figura, figura)
        self.toolbar = self._crear_toolbar(self.marco_figura, self.canvas)

        # Pestaña Comparación
        self._poblar_tab_comparacion()

        # Pestaña Cálculo
        self._poblar_tab_calculo()

        # Cambiar a vista resultados
        self.marco_inicio.pack_forget()
        self.marco_resultados.pack(fill=tk.BOTH, expand=True)

        self.lbl_resultado_titulo.config(text=f"{titulo} — {os.path.basename(self.ruta_imagen)}")
        self.btn_guardar.config(state=tk.NORMAL)
        self.notebook.select(0)

    def guardar_imagen(self) -> None:
        if self.img_procesada is None:
            return
        tipos = [
            ("PNG", "*.png"), ("JPEG", "*.jpg"),
            ("BMP", "*.bmp"), ("TIFF", "*.tif"),
        ]
        ruta = filedialog.asksaveasfilename(
            title="Guardar Imagen Procesada",
            defaultextension=".png", filetypes=tipos,
        )
        if ruta:
            cv2.imwrite(ruta, self.img_procesada)
            messagebox.showinfo("Guardado", f"Imagen guardada en:\n{ruta}")

    @staticmethod
    def _ordenar_tabla(tree: ttk.Treeview, col: str, reverse: bool) -> None:
        items = []
        for k in tree.get_children(""):
            val = tree.set(k, col)
            try:
                val = float(val.replace(",", ""))
            except ValueError:
                pass
            items.append((val, k))
        items.sort(key=lambda x: x[0], reverse=reverse)
        for index, (_, k) in enumerate(items):
            tree.move(k, "", index)
            tag = "par" if index % 2 == 0 else "impar"
            tree.item(k, tags=(tag,))
        tree.heading(
            col,
            command=lambda c=col, r=not reverse: AplicacionProcesamiento._ordenar_tabla(tree, c, r),
        )


if __name__ == "__main__":
    ventana = tk.Tk()
    app = AplicacionProcesamiento(ventana)
    try:
        ventana.mainloop()
    except KeyboardInterrupt:
        ventana.destroy()
