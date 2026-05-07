import numpy as np


def aplicar_expansion(imagen: np.ndarray, s1: int = 0, s2: int = 255):
    imagen_float = imagen.astype(np.float32)

    r1 = np.min(imagen_float)
    r2 = np.max(imagen_float)

    if r1 == r2:
        return imagen.copy(), {"tipo": "expansion", "tabla": []}

    transformada = ((imagen_float - r1) / (r2 - r1)) * (s2 - s1) + s1
    img_procesada = np.clip(np.round(transformada), 0, 255).astype(np.uint8)

    niveles_presentes = np.unique(imagen)
    tabla = []

    for r in niveles_presentes:
        s_float = ((r - r1) / (r2 - r1)) * (s2 - s1) + s1
        s_rounded = int(np.clip(np.round(s_float), 0, 255))

        formula = f"(( {r} - {r1:.1f} ) / {r2 - r1:.1f}) * {s2 - s1} + {s1} = {s_float:.2f}"
        tabla.append((r, formula, s_rounded))

    return img_procesada, {"tipo": "expansion", "tabla": tabla}


def aplicar_ecualizacion(imagen: np.ndarray):
    M, N = imagen.shape
    MN = M * N

    n_k = np.bincount(imagen.flatten(), minlength=256)
    p_r = n_k / MN

    cdf = np.cumsum(p_r)
    s_float = 255.0 * cdf
    s_rounded = np.round(s_float).astype(np.uint8)

    p_s = np.zeros(256)
    for r in range(256):
        p_s[s_rounded[r]] += p_r[r]

    niveles_presentes = np.unique(imagen)
    tabla = []

    for r in niveles_presentes:
        formula = f"255 * {cdf[r]:.4f} = {s_float[r]:.2f}"
        tabla.append((r, f"{p_r[r]:.4f}", formula, s_rounded[r], f"{p_s[s_rounded[r]]:.4f}"))

    img_procesada = s_rounded[imagen]
    return img_procesada, {"tipo": "ecualizacion", "tabla": tabla}