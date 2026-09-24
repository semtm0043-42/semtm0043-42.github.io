"""Generate the paired linear-fit and residual plots for Reflectance Exercise 4.

The readings are synthetic and illustrate how residuals can reveal where a
linear gain model is and is not a useful approximation.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns


OUTPUT_DIRECTORY = Path(__file__).parent
FIT_PLOT_PATH = OUTPUT_DIRECTORY / "linear_fit_nonlinear_region.png"
RESIDUAL_PLOT_PATH = OUTPUT_DIRECTORY / "residuals_nonlinear_region.png"
RANDOM_SEED = 20260922
FIT_MINIMUM = 2
FIT_MAXIMUM = 8
REPEATS_PER_CONDITION = 14

DATA_COLOUR = "#18775b"
FIT_COLOUR = "#e07a2f"
TEXT_COLOUR = "#48545c"
REGION_COLOUR = "#dcebe5"


def illustrative_response(condition: np.ndarray) -> np.ndarray:
    """Return a mostly linear response with stronger curvature at both ends."""

    response = 450.0 + 155.0 * condition - 4.0 * (condition - 5.0) ** 2
    response -= np.where(
        condition < FIT_MINIMUM,
        40.0 * (FIT_MINIMUM - condition) ** 2,
        0.0,
    )
    response -= np.where(
        condition > FIT_MAXIMUM,
        35.0 * (condition - FIT_MAXIMUM) ** 2,
        0.0,
    )
    return response


def create_data() -> tuple[pd.DataFrame, float, float]:
    """Create repeated readings and fit a line only over the selected region."""

    rng = np.random.default_rng(RANDOM_SEED)
    conditions = np.arange(0, 11, dtype=float)
    repeated_conditions = np.repeat(conditions, REPEATS_PER_CONDITION)
    expected_readings = illustrative_response(repeated_conditions)
    readings = expected_readings + rng.normal(0.0, 18.0, repeated_conditions.size)
    horizontal_jitter = rng.uniform(-0.065, 0.065, repeated_conditions.size)

    data = pd.DataFrame(
        {
            "condition": repeated_conditions,
            "plot_condition": repeated_conditions + horizontal_jitter,
            "reading_us": readings,
        }
    )
    fit_data = data.loc[
        data["condition"].between(FIT_MINIMUM, FIT_MAXIMUM)
    ]
    slope, intercept = np.polyfit(
        fit_data["condition"], fit_data["reading_us"], 1
    )
    data["predicted_us"] = slope * data["condition"] + intercept
    data["residual_us"] = data["reading_us"] - data["predicted_us"]
    return data, slope, intercept


def prepare_axis(
    axis: plt.Axes,
    notice_y: float = 0.025,
    notice_vertical_alignment: str = "bottom",
) -> None:
    """Apply the visual treatment shared by both figures."""

    axis.set_facecolor("white")
    axis.axvspan(
        FIT_MINIMUM,
        FIT_MAXIMUM,
        color=REGION_COLOUR,
        alpha=0.72,
        linewidth=0,
        zorder=0,
    )
    for boundary in (FIT_MINIMUM, FIT_MAXIMUM):
        axis.axvline(
            boundary,
            color=DATA_COLOUR,
            linewidth=1.2,
            linestyle=(0, (2, 3)),
            alpha=0.8,
            zorder=1,
        )
    axis.grid(axis="x", color="#e5ebe8", linewidth=0.8)
    axis.grid(axis="y", color="#edf1ef", linewidth=0.8)
    axis.set_xlim(-0.35, 10.35)
    axis.set_xticks(np.arange(0, 11, 1))
    axis.text(
        0.99,
        notice_y,
        "Synthetic illustration — not expected robot data",
        transform=axis.transAxes,
        ha="right",
        va=notice_vertical_alignment,
        color="#63716b",
        fontsize=9.5,
    )
    sns.despine(ax=axis)


def generate_fit_plot(data: pd.DataFrame, slope: float, intercept: float) -> None:
    """Plot repeated readings and the line fitted over the selected region."""

    figure, axis = plt.subplots(figsize=(12, 5.2), dpi=180)
    figure.patch.set_facecolor("white")
    prepare_axis(axis)

    sns.scatterplot(
        data=data,
        x="plot_condition",
        y="reading_us",
        color=DATA_COLOUR,
        alpha=0.24,
        s=28,
        linewidth=0,
        label="Repeated synthetic readings",
        ax=axis,
        zorder=2,
    )
    medians = data.groupby("condition", as_index=False)["reading_us"].median()
    sns.scatterplot(
        data=medians,
        x="condition",
        y="reading_us",
        marker="D",
        s=48,
        color=DATA_COLOUR,
        edgecolor="white",
        linewidth=0.8,
        label="Median reading",
        ax=axis,
        zorder=4,
    )

    inside_x = np.linspace(FIT_MINIMUM, FIT_MAXIMUM, 160)
    axis.plot(
        inside_x,
        slope * inside_x + intercept,
        color=FIT_COLOUR,
        linewidth=2.7,
        label="Linear fit using x = 2 to x = 8",
        zorder=3,
    )
    for outside_x in (
        np.linspace(0, FIT_MINIMUM, 50),
        np.linspace(FIT_MAXIMUM, 10, 50),
    ):
        axis.plot(
            outside_x,
            slope * outside_x + intercept,
            color=FIT_COLOUR,
            linewidth=2.0,
            linestyle=(0, (5, 4)),
            zorder=3,
        )

    axis.annotate(
        "selected region used to estimate gain",
        xy=(5, slope * 5 + intercept),
        xytext=(5, 1920),
        ha="center",
        va="center",
        color=TEXT_COLOUR,
        fontsize=11,
        arrowprops={"arrowstyle": "->", "color": TEXT_COLOUR, "lw": 1.1},
    )
    axis.set_ylim(50, 2070)
    axis.set_xlabel("Illustrative surface condition, x")
    axis.set_ylabel("Sensor reading, y (µs)")
    axis.set_title(
        "Fit the gain only where a straight line is a useful approximation",
        loc="left",
        weight="bold",
    )
    axis.legend(loc="upper left", frameon=False, fontsize=10.5)

    figure.tight_layout(pad=1.2)
    figure.savefig(
        FIT_PLOT_PATH,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "Python, Matplotlib and Seaborn"},
    )
    plt.close(figure)


def generate_residual_plot(data: pd.DataFrame) -> None:
    """Plot residuals from the same fitted line over the complete input range."""

    figure, axis = plt.subplots(figsize=(12, 5.2), dpi=180)
    figure.patch.set_facecolor("white")
    prepare_axis(
        axis,
        notice_y=0.965,
        notice_vertical_alignment="top",
    )

    axis.axhline(
        0,
        color=FIT_COLOUR,
        linewidth=1.8,
        linestyle=(0, (5, 4)),
        label="Perfect prediction (residual = 0)",
        zorder=1,
    )
    sns.scatterplot(
        data=data,
        x="plot_condition",
        y="residual_us",
        color=DATA_COLOUR,
        alpha=0.28,
        s=28,
        linewidth=0,
        label="Residual from each repeat",
        ax=axis,
        zorder=2,
    )
    median_residuals = data.groupby("condition", as_index=False)[
        "residual_us"
    ].median()
    sns.lineplot(
        data=median_residuals,
        x="condition",
        y="residual_us",
        marker="D",
        markersize=5.5,
        color=DATA_COLOUR,
        linewidth=2.0,
        label="Median residual",
        ax=axis,
        zorder=3,
    )

    axis.annotate(
        "structured errors outside the fitted region",
        xy=(
            9.7,
            median_residuals.loc[
                median_residuals["condition"] == 10,
                "residual_us",
            ].iloc[0],
        ),
        xytext=(7.3, -285),
        ha="center",
        va="center",
        color=TEXT_COLOUR,
        fontsize=11,
        arrowprops={"arrowstyle": "->", "color": TEXT_COLOUR, "lw": 1.1},
    )
    residual_limit = max(
        330.0,
        np.ceil(data["residual_us"].abs().max() / 50) * 50,
    )
    axis.set_ylim(-residual_limit, residual_limit)
    axis.set_xlabel("Illustrative surface condition, x")
    axis.set_ylabel("Residual, y − ŷ (µs)")
    axis.set_title(
        "Residuals reveal structure hidden by the response scale",
        loc="left",
        weight="bold",
    )
    axis.legend(loc="upper left", frameon=False, fontsize=10.5)

    figure.tight_layout(pad=1.2)
    figure.savefig(
        RESIDUAL_PLOT_PATH,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "Python, Matplotlib and Seaborn"},
    )
    plt.close(figure)


def main() -> None:
    """Generate both Exercise 4 figures from the same synthetic dataset."""

    sns.set_theme(style="whitegrid", context="notebook")
    data, slope, intercept = create_data()
    generate_fit_plot(data, slope, intercept)
    generate_residual_plot(data)


if __name__ == "__main__":
    main()
