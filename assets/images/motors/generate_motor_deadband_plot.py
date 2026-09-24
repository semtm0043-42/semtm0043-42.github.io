"""Generate the conceptual motor-deadband plot used by motors.html.

Requires NumPy, Matplotlib, and Seaborn. Seaborn installs the other two as
dependencies in a normal Python environment.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


COMMAND_LIMIT_PWM = 200

# This position is chosen only to make the deadband visually clear. It is not a
# disclosed middleware parameter or a value students should expect to measure.
ILLUSTRATIVE_THRESHOLD_PWM = 40

OUTPUT_PATH = Path(__file__).with_name("motor_deadband.png")


def deadband_response(commands: np.ndarray) -> np.ndarray:
    """Return a continuous, normalised illustration of a centred deadband."""
    magnitudes = np.abs(commands)
    moving_response = (
        (magnitudes - ILLUSTRATIVE_THRESHOLD_PWM)
        / (COMMAND_LIMIT_PWM - ILLUSTRATIVE_THRESHOLD_PWM)
    )
    return np.where(
        magnitudes <= ILLUSTRATIVE_THRESHOLD_PWM,
        0.0,
        np.sign(commands) * moving_response,
    )


def main() -> None:
    """Draw and save the website illustration."""
    sns.set_theme(style="whitegrid", context="notebook")

    commands = np.linspace(-COMMAND_LIMIT_PWM, COMMAND_LIMIT_PWM, 1601)
    response = deadband_response(commands)

    figure, axis = plt.subplots(figsize=(12, 4.5), dpi=180)
    figure.patch.set_facecolor("white")
    axis.set_facecolor("white")

    axis.axvspan(
        -ILLUSTRATIVE_THRESHOLD_PWM,
        ILLUSTRATIVE_THRESHOLD_PWM,
        color="#f3c978",
        alpha=0.34,
        linewidth=0,
        zorder=0,
    )
    sns.lineplot(
        x=commands,
        y=response,
        color="#18775b",
        linewidth=3.0,
        ax=axis,
        zorder=3,
    )

    for threshold in (-ILLUSTRATIVE_THRESHOLD_PWM, ILLUSTRATIVE_THRESHOLD_PWM):
        axis.axvline(
            threshold,
            color="#d0643b",
            linewidth=1.5,
            linestyle=(0, (4, 4)),
            zorder=2,
        )

    axis.axhline(0, color="#36453f", linewidth=1.0, zorder=1)
    axis.axvline(0, color="#8a9691", linewidth=0.9, zorder=1)

    axis.annotate(
        "negative threshold",
        xy=(-ILLUSTRATIVE_THRESHOLD_PWM, 0),
        xytext=(-103, 0.34),
        ha="center",
        color="#9c4528",
        fontsize=11,
        arrowprops={"arrowstyle": "->", "color": "#d0643b", "lw": 1.2},
    )
    axis.annotate(
        "positive threshold",
        xy=(ILLUSTRATIVE_THRESHOLD_PWM, 0),
        xytext=(103, -0.34),
        ha="center",
        color="#9c4528",
        fontsize=11,
        arrowprops={"arrowstyle": "->", "color": "#d0643b", "lw": 1.2},
    )
    axis.text(
        0,
        0.12,
        "deadband region\nno sustained motion",
        ha="center",
        va="bottom",
        color="#604d27",
        fontsize=11,
        weight="semibold",
    )

    axis.set_xlim(-COMMAND_LIMIT_PWM, COMMAND_LIMIT_PWM)
    axis.set_ylim(-1.08, 1.08)
    axis.set_xticks([-200, -100, 0, 100, 200])
    axis.set_yticks([-1.0, -0.5, 0.0, 0.5, 1.0])
    axis.set_xlabel("Requested motor PWM")
    axis.set_ylabel("Wheel response (normalised)")
    axis.set_title("An idealised motor deadband centred on zero", loc="left", weight="bold")

    axis.grid(axis="x", color="#dfe6e2", linewidth=0.8)
    axis.grid(axis="y", color="#edf1ef", linewidth=0.8)
    sns.despine(ax=axis)

    figure.tight_layout(pad=1.2)
    figure.savefig(OUTPUT_PATH, bbox_inches="tight", facecolor="white")
    plt.close(figure)


if __name__ == "__main__":
    main()
