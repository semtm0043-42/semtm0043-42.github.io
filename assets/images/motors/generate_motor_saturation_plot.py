"""Generate the conceptual motor-saturation plot used by motors.html.

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

# This position is chosen only to make the saturated region visually clear. It
# is not a disclosed middleware parameter or a value students should expect to
# measure.
ILLUSTRATIVE_SATURATION_PWM = 130

OUTPUT_PATH = Path(__file__).with_name("motor_saturation.png")


def saturation_response(commands: np.ndarray) -> np.ndarray:
    """Return a normalised illustration of a response with an upper limit."""
    proportional_response = commands / ILLUSTRATIVE_SATURATION_PWM
    return np.minimum(proportional_response, 1.0)


def main() -> None:
    """Draw and save the website illustration."""
    sns.set_theme(style="whitegrid", context="notebook")

    commands = np.linspace(0, COMMAND_LIMIT_PWM, 801)
    response = saturation_response(commands)
    proportional_response = commands / ILLUSTRATIVE_SATURATION_PWM

    figure, axis = plt.subplots(figsize=(12, 4.5), dpi=180)
    figure.patch.set_facecolor("white")
    axis.set_facecolor("white")

    axis.axvspan(
        ILLUSTRATIVE_SATURATION_PWM,
        COMMAND_LIMIT_PWM,
        color="#f3c978",
        alpha=0.34,
        linewidth=0,
        zorder=0,
    )
    axis.plot(
        commands,
        proportional_response,
        color="#8a9691",
        linewidth=1.8,
        linestyle=(0, (5, 4)),
        label="Proportional response without a limit",
        zorder=1,
    )
    sns.lineplot(
        x=commands,
        y=response,
        color="#18775b",
        linewidth=3.0,
        label="Illustrative motor response",
        ax=axis,
        zorder=3,
    )

    axis.axvline(
        ILLUSTRATIVE_SATURATION_PWM,
        color="#d0643b",
        linewidth=1.5,
        linestyle=(0, (4, 4)),
        zorder=2,
    )
    axis.axhline(0, color="#36453f", linewidth=1.0, zorder=1)

    axis.annotate(
        "illustrative saturation boundary",
        xy=(ILLUSTRATIVE_SATURATION_PWM, 1.0),
        xytext=(103, 1.30),
        ha="center",
        color="#9c4528",
        fontsize=11,
        arrowprops={"arrowstyle": "->", "color": "#d0643b", "lw": 1.2},
    )
    axis.text(
        168,
        0.89,
        "additional PWM\nlittle or no additional speed",
        ha="center",
        va="top",
        color="#604d27",
        fontsize=11,
        weight="bold",
    )

    axis.set_xlim(0, COMMAND_LIMIT_PWM)
    axis.set_ylim(0, 1.58)
    axis.set_xticks([0, 50, 100, 150, 200])
    axis.set_yticks([0.0, 0.5, 1.0, 1.5])
    axis.set_xlabel("Requested motor PWM")
    axis.set_ylabel("Settled wheel speed (normalised)")
    axis.set_title("An idealised motor response with saturation", loc="left", weight="bold")

    axis.grid(axis="x", color="#dfe6e2", linewidth=0.8)
    axis.grid(axis="y", color="#edf1ef", linewidth=0.8)
    axis.legend(loc="upper left", frameon=False)
    sns.despine(ax=axis)

    figure.tight_layout(pad=1.2)
    figure.savefig(OUTPUT_PATH, bbox_inches="tight", facecolor="white")
    plt.close(figure)


if __name__ == "__main__":
    main()
