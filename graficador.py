import cv2
import matplotlib.pyplot as plt
import numpy as np


def mostrar_resultados(img_orig: np.ndarray, img_proc: np.ndarray, titulo_metodo: str):

    hist_orig = cv2.calcHist([img_orig], [0], None, [256], [0, 256])
    hist_proc = cv2.calcHist([img_proc], [0], None, [256], [0, 256])

    fig, axs = plt.subplots(2, 2, figsize=(12, 8), dpi=100)
    fig.suptitle(f'{titulo_metodo} Teórica de Histograma', fontsize=16, fontweight='bold')

    axs[0, 0].imshow(img_orig, cmap='gray', vmin=0, vmax=255)
    axs[0, 0].set_title("Imagen Original", fontweight='semibold')
    axs[0, 0].axis('off')

    axs[0, 1].imshow(img_proc, cmap='gray', vmin=0, vmax=255)
    axs[0, 1].set_title(f"Imagen con {titulo_metodo}", fontweight='semibold')
    axs[0, 1].axis('off')

    def mostrar_histograma(ax, hist, color, titulo):
        ax.plot(hist, color=color, linewidth=1.5)
        ax.fill_between(range(256), hist.flatten(), color=color, alpha=0.3)
        ax.set_title(titulo, fontsize=11, fontweight='semibold')
        ax.set_xlim([0, 255])
        ax.set_ylim(bottom=0)
        ax.grid(True, which='major', color='#cccccc', linestyle='-', linewidth=0.5)

    mostrar_histograma(axs[1, 0], hist_orig, '#1f77b4', 'Histograma Original')

    color_proceso = '#d62728' if titulo_metodo == 'Ecualización' else '#2ca02c'
    mostrar_histograma(axs[1, 1], hist_proc, color_proceso, f'Histograma ({titulo_metodo})')

    plt.tight_layout()
    fig.subplots_adjust(top=0.90)
    plt.show()