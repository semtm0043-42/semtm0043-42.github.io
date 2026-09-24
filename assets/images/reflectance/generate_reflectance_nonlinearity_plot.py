"""Generate the conceptual linear and non-linear response plot for Exercise 5."""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


OUTPUT_PATH = Path(__file__).with_name("linear_and_nonlinear_response.png")

RESPONSE_COLOUR = "#18775b"
GAIN_COLOUR = "#e07a2f"
TEXT_COLOUR = "#48545c"


def nonlinear_response(input_value: np.ndarray) -> np.ndarray:
    """Return a normalised sigmoid used only as a conceptual response shape."""

    raw_response = 1.0 / (1.0 + np.exp(-10.0 * (input_value - 0.5)))
    minimum = 1.0 / (1.0 + np.exp(5.0))
    maximum = 1.0 / (1.0 + np.exp(-5.0))
    return (raw_response - minimum) / (maximum - minimum)


def local_tangent(
    input_value: float,
    response_function,
    half_width: float,
) -> tuple[np.ndarray, np.ndarray]:
    """Calculate a short numerical tangent segment at one input value."""

    step = 1e-4
    slope = float(
        (
            response_function(np.array([input_value + step]))
            - response_function(np.array([input_value - step]))
        )[0]
        / (2.0 * step)
    )
    centre = float(response_function(np.array([input_value]))[0])
    segment_x = np.array([input_value - half_width, input_value + half_width])
    segment_y = centre + slope * (segment_x - input_value)
    return segment_x, segment_y


def style_axis(axis: plt.Axes, title: str) -> None:
    """Apply the shared presentation used for the two response panels."""

    axis.set(
        xlim=(-0.03, 1.03),
        ylim=(-0.04, 1.08),
        xticks=[0, 0.25, 0.5, 0.75, 1.0],
        yticks=[0, 0.25, 0.5, 0.75, 1.0],
        xlabel="Normalised input",
        ylabel="Normalised response",
        title=title,
    )
    axis.title.set_weight("bold")
    axis.title.set_ha("left")
    axis.title.set_position((0, 1.0))
    axis.grid(axis="x", color="#e5ebe8", linewidth=0.8)
    axis.grid(axis="y", color="#edf1ef", linewidth=0.8)
    axis.set_aspect("equal", adjustable="box")
    sns.despine(ax=axis)


def main() -> None:
    """Draw constant and changing local gain on matched axes."""

    sns.set_theme(style="whitegrid", context="notebook")
    input_values = np.linspace(0.0, 1.0, 401)
    linear_values = input_values
    nonlinear_values = nonlinear_response(input_values)

    figure, axes = plt.subplots(
        1,
        2,
        figsize=(12, 5.2),
        dpi=180,
        sharex=True,
        sharey=True,
    )
    figure.patch.set_facecolor("white")

    for axis in axes:
        axis.set_facecolor("white")

    style_axis(axes[0], "Linear response")
    sns.lineplot(
        x=input_values,
        y=linear_values,
        color=RESPONSE_COLOUR,
        linewidth=3.0,
        ax=axes[0],
    )
    axes[0].plot(
        [0.36, 0.64, 0.64],
        [0.36, 0.36, 0.64],
        color=GAIN_COLOUR,
        linewidth=2.0,
    )
    axes[0].annotate(
        "constant sensitivity\n(constant gain)",
        xy=(0.64, 0.50),
        xytext=(0.69, 0.35),
        ha="left",
        va="center",
        color=TEXT_COLOUR,
        fontsize=11,
        arrowprops={"arrowstyle": "->", "color": GAIN_COLOUR, "lw": 1.2},
    )

    style_axis(axes[1], "Non-linear response")
    sns.lineplot(
        x=input_values,
        y=nonlinear_values,
        color=RESPONSE_COLOUR,
        linewidth=3.0,
        ax=axes[1],
    )

    tangent_specs = [
        (0.17, 0.10, "shallow slope\nlow gain", (0.08, 0.29)),
        (0.50, 0.075, "steep slope\nhigh gain", (0.67, 0.49)),
        (0.83, 0.10, "shallow slope\nlow gain", (0.47, 0.91)),
    ]
    for index, (position, half_width, label, text_position) in enumerate(
        tangent_specs
    ):
        tangent_x, tangent_y = local_tangent(
            position,
            nonlinear_response,
            half_width,
        )
        axes[1].plot(
            tangent_x,
            tangent_y,
            color=GAIN_COLOUR,
            linewidth=2.5,
            solid_capstyle="round",
            label="Local slope (gain)" if index == 0 else None,
            zorder=3,
        )
        response_at_position = float(
            nonlinear_response(np.array([position]))[0]
        )
        axes[1].annotate(
            label,
            xy=(position, response_at_position),
            xytext=text_position,
            ha="center",
            va="center",
            color=TEXT_COLOUR,
            fontsize=10.5,
            arrowprops={"arrowstyle": "->", "color": GAIN_COLOUR, "lw": 1.1},
        )

    figure.text(
        0.985,
        0.015,
        "Conceptual response shapes — not measured robot data",
        ha="right",
        va="bottom",
        color="#63716b",
        fontsize=9.5,
    )
    figure.tight_layout(rect=(0, 0.045, 1, 1), w_pad=2.6)
    figure.savefig(
        OUTPUT_PATH,
        bbox_inches="tight",
        facecolor="white",
        metadata={"Software": "Python, Matplotlib and Seaborn"},
    )
    plt.close(figure)


if __name__ == "__main__":
    main()
