"""Illustrate strip-width effects on peak response and plateau width.

Run from the repository root:
MPLCONFIGDIR=/tmp/reflectance-plot-cache .venv/bin/python \
    website/assets/images/reflectance/generate_reflectance_footprint_plot.py

This is an ideal, uniform one-dimensional window with an unsaturated readout
proportional to black coverage. It is not a fit or a sensor specification.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


OUTPUT_DIRECTORY = Path(__file__).resolve().parent
FOOTPRINT_MM = 5.0
WHITE_US = 300.0
BLACK_US = 1700.0
STRIP_WIDTHS_MM = (2.0, 5.0, 10.0)
RESPONSE_COLOUR = "#18775b"
ANNOTATION_COLOUR = "#a84c1e"
TEXT_COLOUR = "#364b43"


def strip_response(position_mm, strip_width_mm, footprint_mm=FOOTPRINT_MM):
    """Return the fraction of a uniform window overlapping a centred strip."""
    position_mm = np.asarray(position_mm, dtype=float)
    if strip_width_mm <= 0 or footprint_mm <= 0:
        raise ValueError("Strip and footprint widths must be positive.")
    left = np.maximum(-strip_width_mm / 2, position_mm - footprint_mm / 2)
    right = np.minimum(strip_width_mm / 2, position_mm + footprint_mm / 2)
    return np.maximum(0.0, right - left) / footprint_mm


def main():
    sns.set_theme(style="whitegrid", context="notebook", font_scale=1.03)
    plt.rcParams["svg.fonttype"] = "none"
    positions_mm = np.linspace(-9, 9, 1801)
    figure, axes = plt.subplots(3, 1, figsize=(10.5, 12), sharex=True, sharey=True)
    titles = (
        "(a) Narrow strip: w = 2 mm < L — diminished peak",
        "(b) Equal widths: w = L = 5 mm — black reference at one position",
        "(c) Wide strip: w = 10 mm > L — plateau at the black reference",
    )
    for axis, width_mm, title in zip(axes, STRIP_WIDTHS_MM, titles):
        response = strip_response(positions_mm, width_mm)
        readings_us = WHITE_US + (BLACK_US - WHITE_US) * response
        axis.axvspan(-width_mm / 2, width_mm / 2, color="#dce4e0", alpha=0.65, zorder=0)
        for edge in (-width_mm / 2, width_mm / 2):
            axis.axvline(edge, color="#8c9c94", linestyle=(0, (2, 3)), lw=1.1)
        axis.axhline(BLACK_US, color="#59656e", linestyle=(0, (5, 4)), lw=1.4)
        axis.axhline(WHITE_US, color="#87928b", linestyle=(0, (2, 3)), lw=1.1)
        sns.lineplot(
            x=positions_mm, y=readings_us, ax=axis,
            color=RESPONSE_COLOUR, linewidth=3, estimator=None,
        )
        axis.text(-8.6, BLACK_US + 45, "Black reference B = 1700 µs", color=TEXT_COLOUR, fontsize=10)
        axis.text(-8.6, 100, "White reference W = 300 µs", color=TEXT_COLOUR, fontsize=10)
        axis.set_title(title, loc="left", weight="bold", fontsize=12, pad=14)
        axis.set_ylabel("Illustrative reading (µs)")
        axis.set_ylim(0, 2200)
        axis.set_xlim(-9, 9)
        axis.set_yticks([300, 860, 1300, 1700])
        axis.set_xticks(np.arange(-8, 9, 2))
        axis.grid(axis="x", visible=False)
        axis.grid(axis="y", color="#edf1ef")
        sns.despine(ax=axis)

    narrow_peak = WHITE_US + (BLACK_US - WHITE_US) * STRIP_WIDTHS_MM[0] / FOOTPRINT_MM
    axes[0].text(0, 530, "Peak = 860 µs\nWhite still contributes", ha="center",
                 color=RESPONSE_COLOUR, fontsize=11)
    axes[0].annotate(
        "", xy=(3.5, BLACK_US), xytext=(3.5, narrow_peak),
        arrowprops={"arrowstyle": "<->", "color": ANNOTATION_COLOUR, "lw": 1.5},
    )
    axes[0].text(3.9, 1270, "Below the\nblack reference", va="center",
                 color=ANNOTATION_COLOUR, fontsize=11)
    axes[0].plot([1.5, 3.5], [narrow_peak, narrow_peak], color=ANNOTATION_COLOUR, lw=0.9, ls=":")

    axes[1].scatter([0], [BLACK_US], color=RESPONSE_COLOUR, s=55, zorder=5)
    axes[1].annotate(
        "Reaches B only when centred\nNo finite-width plateau", xy=(0, BLACK_US),
        xytext=(2.3, 1120), color=ANNOTATION_COLOUR, fontsize=11,
        arrowprops={"arrowstyle": "->", "color": ANNOTATION_COLOUR, "lw": 1.2},
    )

    axes[2].text(0, 1100, "The whole spatial footprint remains over black\nwhile the sensor moves through this span",
                 ha="center", color=RESPONSE_COLOUR, fontsize=11)
    axes[2].set_xlabel("Sensor position across the strip, x (mm) — strip centre at x = 0", labelpad=12)

    figure.suptitle("Strip width changes both peak height and plateau width", fontsize=17,
                     weight="bold", color=TEXT_COLOUR, y=0.98)
    figure.text(0.5, 0.945, "Same uniform footprint in every panel: L = 5 mm   •   Grey shading marks the black strip",
                ha="center", fontsize=11, color=TEXT_COLOUR)
    figure.text(0.5, 0.028,
                "Illustrative model, not robot measurements: equal spatial weighting and an unsaturated,\n"
                "proportional readout. Clipping or unequal sensitivity can change these profiles.",
                ha="center", fontsize=10.5, color=TEXT_COLOUR)
    figure.subplots_adjust(top=0.895, bottom=0.105, left=0.105, right=0.975, hspace=0.30)
    for extension in ("png", "svg"):
        path = OUTPUT_DIRECTORY / f"footprint_strip_response.{extension}"
        figure.savefig(path, dpi=180, facecolor="white", bbox_inches="tight")
        print(path)
    plt.close(figure)


if __name__ == "__main__":
    main()
