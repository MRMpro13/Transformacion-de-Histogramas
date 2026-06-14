import cv2
import matplotlib.pyplot as plt
import numpy as np


def mostrar_histograma(
    ax: plt.Axes, hist: np.ndarray, color: str, titulo: str
) -> None:
    ax.plot(hist, color=color, linewidth=1.8)
    ax.fill_between(range(256), hist.flatten(), color=color, alpha=0.25)

    ax.set_title(titulo, fontsize=11, fontweight="semibold", pad=8)
    ax.set_xlim([0, 255])
    ax.set_ylim(bottom=0)
    ax.grid(True, which="major", color="#e0e0e0", linestyle="-", linewidth=0.5)
    ax.set_xlabel("Nivel de intensidad", fontsize=8.5, color="#666666", labelpad=4)
    ax.set_ylabel("N° de píxeles", fontsize=8.5, color="#666666", labelpad=4)

    ax.spines["top"].set_visible(False)
    ax.spines["right"].set_visible(False)
    ax.spines["left"].set_color("#cccccc")
    ax.spines["bottom"].set_color("#cccccc")
    ax.tick_params(colors="#555555", labelsize=9)


def generar_figura_resultados(
    img_orig: np.ndarray,
    img_proc: np.ndarray,
    titulo_metodo: str,
    color_proceso: str = "#2ca02c",
) -> tuple:
    hist_orig = cv2.calcHist([img_orig], [0], None, [256], [0, 256])
    hist_proc = cv2.calcHist([img_proc], [0], None, [256], [0, 256])

    fig, axs = plt.subplots(2, 2, figsize=(10, 6), dpi=100)

    fig.suptitle(
        f"{titulo_metodo} de Histograma",
        fontsize=16, fontweight="bold", y=0.97
    )

    axs[0, 0].imshow(img_orig, cmap="gray", vmin=0, vmax=255)
    axs[0, 0].set_title("Imagen Original", fontweight="semibold")
    axs[0, 0].axis("off")

    axs[0, 1].imshow(img_proc, cmap="gray", vmin=0, vmax=255)
    axs[0, 1].set_title(f"Imagen con {titulo_metodo}", fontweight="semibold")
    axs[0, 1].axis("off")

    mostrar_histograma(axs[1, 0], hist_orig, "#3a86ff", "Histograma Original")
    mostrar_histograma(
        axs[1, 1], hist_proc, color_proceso, f"Histograma ({titulo_metodo})"
    )

    plt.tight_layout()
    fig.subplots_adjust(top=0.90)

    return fig, axs, hist_orig, hist_proc
