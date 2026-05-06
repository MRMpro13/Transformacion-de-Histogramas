import numpy as np


def aplicar_expansion(imagen: np.ndarray) -> np.ndarray:

    r1 = np.percentile(imagen, 1)
    r2 = np.percentile(imagen, 99)

    # Evitar división por cero
    if r1 == r2:
        return imagen.copy()

    transformada = ((imagen.astype(np.float32) - r1) / (r2 - r1)) * 255.0

    return np.clip(np.round(transformada), 0, 255).astype(np.uint8)


def aplicar_ecualizacion(imagen: np.ndarray) -> np.ndarray:

    M, N = imagen.shape
    MN = M * N

    n_k = np.bincount(imagen.flatten(), minlength=256)

    p_r = n_k / MN

    S_k = np.round(255.0 * np.cumsum(p_r)).astype(np.uint8)

    return S_k[imagen]