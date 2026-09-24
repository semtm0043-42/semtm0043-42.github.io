"""Generate the illustrative motor-gain plots used by motors.html.

The plotted measurements are deterministic, synthetic teaching data. The
chosen thresholds, response shape, and scale are not middleware parameters or
values that students should expect to measure.

Requires NumPy, Matplotlib, and Seaborn. Seaborn installs the other two as
dependencies in a normal Python environment.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


OUTPUT_DIRECTORY = Path(__file__).parent
FIT_OUTPUT_PATH = OUTPUT_DIRECTORY / "motor_gain_linear_fit.png"
RESIDUAL_OUTPUT_PATH = OUTPUT_DIRECTORY / "motor_gain_residuals.png"

COMMANDS_PWM = np.arange(0, 201, 10, dtype=float)
ILLUSTRATIVE_DEADBAND_END_PWM = 40
ILLUSTRATIVE_FIT_MIN_PWM = 60
ILLUSTRATIVE_FIT_MAX_PWM = 130
ILLUSTRATIVE_HELD_BACK_PWM = 100
ILLUSTRATIVE_SATURATION_START_PWM = 160

# Fixed offsets make the points look like repeated physical measurements while
# keeping the generated files byte-for-byte reproducible.
ILLUSTRATIVE_MEASUREMENT_OFFSETS = np.array(
    [
        0, 0, 0, 0, 0, 12, -9, 8, -13, 6, -10,
        14, -7, 9, -11, 5, -6, 8, -5, 4, -3,
    ],
    dtype=float,
)


def illustrative_speed(commands: np.ndarray) -> np.ndarray:
    """Return a synthetic response containing deadband, curvature, and saturation."""
    moving_speed = (
        9.0 * (commands - ILLUSTRATIVE_DEADBAND_END_PWM)
        + 0.016 * (commands - 85.0) ** 2
    )
    response = np.where(
        commands <= ILLUSTRATIVE_DEADBAND_END_PWM,
        0.0,
        moving_speed,
    )
    return np.clip(response, 0.0, 1120.0)


def configure_axis(axis: plt.Axes) -> None:
    """Apply shared site-aligned styling to a plot axis."""
    axis.set_xlim(0, 200)
    axis.set_xticks([0, 50, 100, 150, 200])
    axis.set_xlabel("Requested motor PWM, $u$")
    axis.grid(axis="x", color="#dfe6e2", linewidth=0.8)
    axis.grid(axis="y", color="#edf1ef", linewidth=0.8)
    sns.despine(ax=axis)


def add_operating_regions(axis: plt.Axes) -> None:
    """Mark illustrative regions excluded from the local gain fit."""
    axis.axvspan(
        0,
        ILLUSTRATIVE_DEADBAND_END_PWM,
        color="#d9dfdc",
        alpha=0.55,
        linewidth=0,
        zorder=0,
    )
    axis.axvspan(
        ILLUSTRATIVE_FIT_MIN_PWM,
        ILLUSTRATIVE_FIT_MAX_PWM,
        color="#cce6dc",
        alpha=0.42,
        linewidth=0,
        zorder=0,
    )
    axis.axvspan(
        ILLUSTRATIVE_SATURATION_START_PWM,
        200,
        color="#f3c978",
        alpha=0.34,
        linewidth=0,
        zorder=0,
    )


def main() -> None:
    """Draw and save the local-fit and full-range residual illustrations."""
    sns.set_theme(style="whitegrid", context="notebook")

    measured_speed = (
        illustrative_speed(COMMANDS_PWM) + ILLUSTRATIVE_MEASUREMENT_OFFSETS
    )
    fitting_mask = (
        (COMMANDS_PWM >= ILLUSTRATIVE_FIT_MIN_PWM)
        & (COMMANDS_PWM <= ILLUSTRATIVE_FIT_MAX_PWM)
        & (COMMANDS_PWM != ILLUSTRATIVE_HELD_BACK_PWM)
    )
    held_back_mask = COMMANDS_PWM == ILLUSTRATIVE_HELD_BACK_PWM

    slope, intercept = np.polyfit(
        COMMANDS_PWM[fitting_mask], measured_speed[fitting_mask], 1
    )
    predicted_speed = slope * COMMANDS_PWM + intercept
    residuals = measured_speed - predicted_speed

    figure, axis = plt.subplots(figsize=(12, 4.5), dpi=180)
    figure.patch.set_facecolor("white")
    axis.set_facecolor("white")
    add_operating_regions(axis)

    sns.scatterplot(
        x=COMMANDS_PWM,
        y=measured_speed,
        color="#65726d",
        s=48,
        label="Illustrative measurements",
        ax=axis,
        zorder=3,
    )
    sns.scatterplot(
        x=COMMANDS_PWM[fitting_mask],
        y=measured_speed[fitting_mask],
        color="#18775b",
        s=62,
        label="Points used for the local fit",
        ax=axis,
        zorder=4,
    )
    sns.scatterplot(
        x=COMMANDS_PWM[held_back_mask],
        y=measured_speed[held_back_mask],
        color="#d0643b",
        marker="D",
        s=82,
        label="Held-back observation",
        ax=axis,
        zorder=5,
    )
    axis.plot(
        COMMANDS_PWM,
        predicted_speed,
        color="#18775b",
        linewidth=2.6,
        label="Local straight-line model",
        zorder=2,
    )

    axis.text(
        19,
        1060,
        "deadband\nregion",
        ha="center",
        va="top",
        color="#59645f",
        fontsize=10,
        weight="bold",
    )
    axis.text(
        95,
        1060,
        "chosen fitting region",
        ha="center",
        va="top",
        color="#18775b",
        fontsize=10,
        weight="bold",
    )
    axis.text(
        180,
        1060,
        "saturation\nregion",
        ha="center",
        va="top",
        color="#604d27",
        fontsize=10,
        weight="bold",
    )

    configure_axis(axis)
    axis.set_ylim(-40, 1160)
    axis.set_ylabel("Settled encoder speed (counts s$^{-1}$)")
    axis.set_title(
        "A local gain fit within an illustrative usable range",
        loc="left",
        weight="bold",
    )
    axis.legend(loc="lower right", frameon=False)

    figure.tight_layout(pad=1.2)
    figure.savefig(FIT_OUTPUT_PATH, bbox_inches="tight", facecolor="white")
    plt.close(figure)

    figure, axis = plt.subplots(figsize=(12, 4.5), dpi=180)
    figure.patch.set_facecolor("white")
    axis.set_facecolor("white")
    add_operating_regions(axis)

    axis.axhline(0, color="#36453f", linewidth=1.2, zorder=1)
    sns.scatterplot(
        x=COMMANDS_PWM,
        y=residuals,
        color="#65726d",
        s=52,
        label="Measured − predicted",
        ax=axis,
        zorder=3,
    )
    sns.scatterplot(
        x=COMMANDS_PWM[fitting_mask],
        y=residuals[fitting_mask],
        color="#18775b",
        s=65,
        label="Residuals in the fitting region",
        ax=axis,
        zorder=4,
    )
    sns.scatterplot(
        x=COMMANDS_PWM[held_back_mask],
        y=residuals[held_back_mask],
        color="#d0643b",
        marker="D",
        s=82,
        label="Held-back residual",
        ax=axis,
        zorder=5,
    )

    configure_axis(axis)
    residual_limit = float(np.ceil(np.max(np.abs(residuals)) / 100.0) * 100.0)
    axis.set_ylim(-residual_limit, residual_limit)
    axis.set_ylabel(r"Residual, $\omega-\hat{\omega}$ (counts s$^{-1}$)")
    axis.set_title(
        "Residuals test where the local gain model remains useful",
        loc="left",
        weight="bold",
    )
    axis.legend(loc="lower left", frameon=False)

    figure.tight_layout(pad=1.2)
    figure.savefig(RESIDUAL_OUTPUT_PATH, bbox_inches="tight", facecolor="white")
    plt.close(figure)


if __name__ == "__main__":
    main()
