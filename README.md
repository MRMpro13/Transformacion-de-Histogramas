# Transformación de Histogramas

Aplicación GUI para realizar expansión y ecualización de histogramas en imágenes, construida con Python, tkinter, OpenCV, NumPy y Matplotlib.

## Requisitos

- Python 3.9+
- pip

## Instalación

```bash
pip install -r requirements.txt
```

## Uso

```bash
python main.py
```

1. Haz clic en **Buscar Archivo** y selecciona una imagen (PNG, JPG, BMP, TIFF).
2. Elige el método:
   - **Expansión de Histograma** – asigna el rango de intensidades de la imagen `[r1, r2]` a un rango de salida personalizado `[s1, s2]`. Por defecto `s1=0`, `s2=255` (máximo contraste).
   - **Ecualización de Histograma** – redistribuye los niveles de gris para que el histograma de salida sea aproximadamente uniforme.
3. Presiona **Procesar y Mostrar Resultados**.
4. En la ventana de resultados puedes:
   - Ver la imagen original, la procesada y sus histogramas.
   - Abrir la **tabla de cálculo** con la fórmula matemática aplicada a cada nivel de pixel.
   - **Guardar la imagen procesada** en PNG, JPG, BMP o TIFF.

**Nota:** El programa convierte la imagen a escala de grises automáticamente antes de procesarla.

## Estructura del proyecto

```
├── main.py                   # Interfaz gráfica (tkinter)
├── funcionhistograma.py      # Algoritmos de expansión y ecualización
├── graficador.py             # Visualización con matplotlib
├── requirements.txt          # Dependencias
└── tests/
    └── test_funcionhistograma.py  # Tests unitarios
```

## Algoritmos

### Expansión (contrast stretching)

$s = \frac{(r - r_1)}{(r_2 - r_1)} \cdot (s_2 - s_1) + s_1$

Donde $r$ es el nivel original, $r_1$ y $r_2$ son los valores mínimo y máximo de la imagen, y $s_1$, $s_2$ son los límites del rango de salida.

### Ecualización

$s_k = \text{round}(255 \cdot \text{CDF}(r_k))$

La función de distribución acumulativa (CDF) se calcula a partir del histograma normalizado de la imagen original.

## Licencia

MIT
