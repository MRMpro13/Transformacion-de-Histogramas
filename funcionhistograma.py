import numpy as np


def aplicar_expansion(imagen: np.ndarray) -> np.ndarray:

    imagen_float = imagen.astype(np.float32)

    r1 = np.percentile(imagen_float, 1)
    r2 = np.percentile(imagen_float, 99)

    if r1 == r2:
        return imagen.copy()

    transformada = ((imagen_float - r1) / (r2 - r1)) * 255.0

    transformada_restringida = np.clip(np.round(transformada), 0, 255)

    return transformada_restringida.astype(np.uint8)


def aplicar_ecualizacion(imagen: np.ndarray) -> np.ndarray:

    M, N = imagen.shape
    MN = M * N

    n_k = np.bincount(imagen.flatten(), minlength=256)

    p_r = n_k / MN

    S_k = np.round(255.0 * np.cumsum(p_r)).astype(np.uint8)

    return S_k[imagen]