"""Generate the illustrative offset plot used in reflectance Exercise 2."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


OUTPUT_PATH = Path(__file__).with_name("reflectance_offset.png")
SEED = 20260922


def main() -> None:
    """Create a deterministic example of channel-dependent sensor offsets."""
    rng = np.random.default_rng(SEED)
    sensors = ["DN1", "DN2", "DN3", "DN4", "DN5"]
    means = [315, 380, 345, 425, 365]
    standard_deviations = [16, 20, 15, 22, 18]
    repeats = 18

    records = []
    for sensor, mean, standard_deviation in zip(
        sensors, means, standard_deviations, strict=True
    ):
        readings = rng.normal(mean, standard_deviation, repeats)
        records.extend(
            {"sensor": sensor, "reading_us": reading} for reading in readings
        )

    data = pd.DataFrame.from_records(records)
    medians = data.groupby("sensor", sort=False)["reading_us"].median()

    sns.set_theme(style="whitegrid", context="talk")
    figure, axis = plt.subplots(figsize=(12, 5.2), dpi=180)

    sns.boxplot(
        data=data,
        x="sensor",
        y="reading_us",
        order=sensors,
        width=0.55,
        showfliers=False,
        color="#b8d8cd",
        linecolor="#18775b",
        linewidth=1.5,
        ax=axis,
    )
    sns.stripplot(
        data=data,
        x="sensor",
        y="reading_us",
        order=sensors,
        color="#18775b",
        alpha=0.48,
        jitter=0.16,
        size=5.5,
        ax=axis,
    )
    axis.scatter(
        range(len(sensors)),
        medians.reindex(sensors),
        marker="D",
        s=48,
        color="#e07a2f",
        edgecolor="white",
        linewidth=0.8,
        zorder=5,
        label="Median baseline",
    )

    bracket_y = 485
    axis.plot([0, 0, 3, 3], [472, bracket_y, bracket_y, 472], color="#48545c", lw=1.2)
    axis.text(
        1.5,
        bracket_y + 5,
        "Different channels can have different baselines",
        ha="center",
        va="bottom",
        color="#48545c",
        fontsize=12,
    )

    axis.set(
        title="The same reference condition can produce different channel baselines",
        xlabel="Sensor channel — same white reference condition",
        ylabel="Raw discharge time (µs)",
        ylim=(250, 530),
    )
    axis.legend(loc="lower right", frameon=True, fontsize=11)
    axis.text(
        0.995,
        0.965,
        "Synthetic illustration — not expected robot data",
        transform=axis.transAxes,
        ha="right",
        va="top",
        color="#647078",
        fontsize=10,
    )
    axis.grid(axis="x", visible=False)
    sns.despine(ax=axis)
    figure.tight_layout()
    figure.savefig(
        OUTPUT_PATH,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "Matplotlib and seaborn"},
    )
    plt.close(figure)


if __name__ == "__main__":
    main()
