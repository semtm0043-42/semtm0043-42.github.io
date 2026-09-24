"""Generate the illustrative saturation plot used in Reflectance Exercise 3.

The values are synthetic. They illustrate the evidence a saturation experiment
might produce and are not expected measurements or hidden middleware values.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


OUTPUT_PATH = Path(__file__).with_name("reflectance_saturation.png")
RANDOM_SEED = 20260922

# These values make the conceptual plateau easy to see. They are deliberately
# illustrative rather than estimates of the supplied robot's characteristics.
ILLUSTRATIVE_PLATEAU_BOUNDARY = 48
REPEATS_PER_CONDITION = 12


def illustrative_response(greyscale: np.ndarray) -> np.ndarray:
    """Return a synthetic discharge-time response with a dark-end plateau."""

    upper_plateau_us = 2200.0
    lower_response_us = 350.0
    decay_scale = 55.0

    return np.where(
        greyscale <= ILLUSTRATIVE_PLATEAU_BOUNDARY,
        upper_plateau_us,
        lower_response_us
        + (upper_plateau_us - lower_response_us)
        * np.exp(
            -(greyscale - ILLUSTRATIVE_PLATEAU_BOUNDARY) / decay_scale
        ),
    )


def main() -> None:
    """Draw repeated synthetic readings and their typical response."""

    rng = np.random.default_rng(RANDOM_SEED)
    conditions = np.array(
        [0, 16, 32, 48, 64, 80, 96, 128, 160, 192, 224, 255],
        dtype=float,
    )
    expected_reading = illustrative_response(conditions)

    repeated_conditions = np.repeat(conditions, REPEATS_PER_CONDITION)
    repeated_readings = np.repeat(
        expected_reading,
        REPEATS_PER_CONDITION,
    ) + rng.normal(0.0, 42.0, repeated_conditions.size)

    readings_by_condition = repeated_readings.reshape(
        conditions.size,
        REPEATS_PER_CONDITION,
    )
    median_reading = np.median(readings_by_condition, axis=1)
    lower_interval = np.percentile(readings_by_condition, 10, axis=1)
    upper_interval = np.percentile(readings_by_condition, 90, axis=1)

    sns.set_theme(style="whitegrid", context="notebook")
    figure, axis = plt.subplots(figsize=(12, 5.2), dpi=180)
    figure.patch.set_facecolor("white")
    axis.set_facecolor("white")

    axis.axvspan(
        0,
        ILLUSTRATIVE_PLATEAU_BOUNDARY,
        color="#f3c978",
        alpha=0.32,
        linewidth=0,
        label="Illustrative candidate plateau",
        zorder=0,
    )

    sns.scatterplot(
        x=repeated_conditions,
        y=repeated_readings,
        color="#5d8275",
        alpha=0.30,
        s=30,
        linewidth=0,
        label="Repeated synthetic readings",
        ax=axis,
        zorder=2,
    )
    axis.fill_between(
        conditions,
        lower_interval,
        upper_interval,
        color="#18775b",
        alpha=0.16,
        linewidth=0,
        label="Middle 80% of repeats",
        zorder=1,
    )
    sns.lineplot(
        x=conditions,
        y=median_reading,
        marker="o",
        markersize=6,
        color="#18775b",
        linewidth=2.6,
        label="Median reading",
        ax=axis,
        zorder=3,
    )

    axis.axvline(
        ILLUSTRATIVE_PLATEAU_BOUNDARY,
        color="#d0643b",
        linewidth=1.4,
        linestyle=(0, (4, 4)),
        zorder=1,
    )
    axis.annotate(
        "physical condition changes,\nbut reading distributions overlap",
        xy=(24, 2200),
        xytext=(84, 2440),
        ha="center",
        va="center",
        color="#7e3f28",
        fontsize=11,
        arrowprops={"arrowstyle": "->", "color": "#d0643b", "lw": 1.2},
    )
    axis.text(
        0.99,
        0.03,
        "Synthetic illustration — not expected robot data",
        transform=axis.transAxes,
        ha="right",
        va="bottom",
        color="#63716b",
        fontsize=9.5,
    )

    axis.set_xlim(-5, 260)
    axis.set_ylim(250, 2580)
    axis.set_xticks([0, 32, 64, 96, 128, 160, 192, 224, 255])
    axis.set_xlabel("Printed greyscale condition (0 = black, 255 = white)")
    axis.set_ylabel("Raw discharge time (µs)")
    axis.set_title(
        "Saturation makes distinct input conditions difficult to distinguish",
        loc="left",
        weight="bold",
    )

    axis.grid(axis="x", color="#e5ebe8", linewidth=0.8)
    axis.grid(axis="y", color="#edf1ef", linewidth=0.8)
    axis.legend(loc="center right", frameon=False)
    sns.despine(ax=axis)

    figure.tight_layout(pad=1.2)
    figure.savefig(
        OUTPUT_PATH,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "Python, Matplotlib and Seaborn"},
    )
    plt.close(figure)


if __name__ == "__main__":
    main()
