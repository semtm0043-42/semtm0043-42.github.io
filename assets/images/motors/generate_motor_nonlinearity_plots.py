"""Generate the illustrative motor non-linearity plots used by motors.html.

The measurements and response shapes are deterministic, synthetic teaching
examples. They do not represent middleware parameters or values that students
should expect to measure on their robot.

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
SHAPES_OUTPUT_PATH = OUTPUT_DIRECTORY / "motor_nonlinearity_candidate_shapes.png"
COMPARISON_OUTPUT_PATH = OUTPUT_DIRECTORY / "motor_nonlinearity_model_comparison.png"

GREEN = "#18775b"
ORANGE = "#d0643b"
BLUE = "#2f6b8a"
PURPLE = "#7a3db8"
GREY = "#65726d"
AMBER = "#f3c978"


def power_prediction(command: np.ndarray, gamma: float) -> np.ndarray:
    """Return a normalised power-law prediction."""
    return command**gamma


def illustrative_measurements(command: np.ndarray) -> np.ndarray:
    """Return deterministic data not generated exactly by any candidate model."""
    offsets = np.array(
        [0.0, 0.010, -0.012, 0.014, -0.009, 0.012,
         -0.014, 0.011, -0.008, 0.009, 0.0]
    )
    response = 0.72 * command**1.42 + 0.28 * command**2
    return np.clip(response + offsets, 0.0, 1.0)


def fit_power_law(command: np.ndarray, response: np.ndarray) -> float:
    """Estimate gamma by a deterministic grid search over plausible shapes."""
    candidates = np.linspace(0.35, 2.50, 4301)
    predictions = command[:, None] ** candidates[None, :]
    mean_squared_error = np.mean((response[:, None] - predictions) ** 2, axis=0)
    return float(candidates[np.argmin(mean_squared_error)])


def style_axis(axis: plt.Axes) -> None:
    """Apply shared site-aligned styling."""
    axis.set_xlim(0, 1)
    axis.set_xticks(np.linspace(0, 1, 6))
    axis.grid(axis="x", color="#dfe6e2", linewidth=0.8)
    axis.grid(axis="y", color="#edf1ef", linewidth=0.8)
    sns.despine(ax=axis)


def draw_candidate_shapes() -> None:
    """Show how gamma changes a normalised power-law response."""
    command = np.linspace(0, 1, 501)

    figure, axis = plt.subplots(figsize=(12, 4.5), dpi=180)
    figure.patch.set_facecolor("white")
    axis.set_facecolor("white")

    axis.plot(
        command,
        power_prediction(command, 0.50),
        color=BLUE,
        linewidth=2.8,
        label=r"$\gamma=0.5$: steepens early, then flattens",
    )
    axis.plot(
        command,
        power_prediction(command, 1.00),
        color=GREY,
        linewidth=2.2,
        linestyle=(0, (5, 4)),
        label=r"$\gamma=1$: linear shape",
    )
    axis.plot(
        command,
        power_prediction(command, 2.00),
        color=GREEN,
        linewidth=2.8,
        label=r"$\gamma=2$: flatter first, then steepens",
    )

    style_axis(axis)
    axis.set_ylim(0, 1.04)
    axis.set_xlabel(r"Normalised requested PWM, $x$")
    axis.set_ylabel(r"Predicted normalised speed, $\hat{v}$")
    axis.set_title(
        "Gamma describes the shape of a normalised power law",
        loc="left",
        weight="bold",
    )
    axis.legend(loc="upper left", frameon=False)

    figure.tight_layout(pad=1.2)
    figure.savefig(SHAPES_OUTPUT_PATH, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def draw_model_comparison() -> None:
    """Compare three fitted candidates using synthetic held-back observations."""
    command = np.linspace(0, 1, 11)
    response = illustrative_measurements(command)
    held_back_mask = np.isclose(command, 0.3) | np.isclose(command, 0.7)
    fitting_mask = ~held_back_mask

    linear_coefficients = np.polyfit(command[fitting_mask], response[fitting_mask], 1)
    quadratic_coefficients = np.polyfit(
        command[fitting_mask], response[fitting_mask], 2
    )
    gamma = fit_power_law(command[fitting_mask], response[fitting_mask])

    fine_command = np.linspace(0, 1, 501)
    predictions = {
        "Linear": np.polyval(linear_coefficients, command),
        "Quadratic": np.polyval(quadratic_coefficients, command),
        "Power law": power_prediction(command, gamma),
    }
    fine_predictions = {
        "Linear": np.polyval(linear_coefficients, fine_command),
        "Quadratic": np.polyval(quadratic_coefficients, fine_command),
        "Power law": power_prediction(fine_command, gamma),
    }
    colours = {
        "Linear": "#4f5955",
        "Quadratic": PURPLE,
        "Power law": GREEN,
    }
    line_styles = {
        "Linear": (0, (7, 4)),
        "Quadratic": (0, (2, 2)),
        "Power law": "solid",
    }
    markers = {"Linear": "o", "Quadratic": "s", "Power law": "^"}
    line_widths = {"Linear": 2.7, "Quadratic": 2.4, "Power law": 3.2}
    zorders = {"Linear": 3, "Power law": 4, "Quadratic": 5}

    figure, (response_axis, residual_axis) = plt.subplots(
        2,
        1,
        figsize=(12, 7.4),
        dpi=180,
        sharex=True,
        gridspec_kw={"height_ratios": [1.55, 1.0]},
    )
    figure.patch.set_facecolor("white")

    for axis in (response_axis, residual_axis):
        axis.set_facecolor("white")
        for held_back_command in command[held_back_mask]:
            axis.axvspan(
                held_back_command - 0.018,
                held_back_command + 0.018,
                color=AMBER,
                alpha=0.32,
                linewidth=0,
                zorder=0,
            )

    sns.scatterplot(
        x=command[fitting_mask],
        y=response[fitting_mask],
        color="#36453f",
        s=58,
        label="Illustrative fitting observations",
        ax=response_axis,
        zorder=5,
    )
    sns.scatterplot(
        x=command[held_back_mask],
        y=response[held_back_mask],
        color=ORANGE,
        marker="D",
        s=82,
        label="Held-back observations",
        ax=response_axis,
        zorder=6,
    )
    for name, prediction in fine_predictions.items():
        response_axis.plot(
            fine_command,
            prediction,
            color=colours[name],
            linewidth=line_widths[name],
            linestyle=line_styles[name],
            marker=markers[name],
            markevery=(25, 50),
            markersize=5.2,
            markerfacecolor="white",
            markeredgecolor=colours[name],
            markeredgewidth=1.1,
            label=f"{name} candidate",
            zorder=zorders[name],
        )

    style_axis(response_axis)
    response_axis.set_ylim(-0.04, 1.04)
    response_axis.set_ylabel(r"Normalised settled speed, $v$")
    response_axis.set_title(
        "Fit every candidate to the same illustrative observations",
        loc="left",
        weight="bold",
    )
    response_axis.text(
        0.98,
        0.04,
        "Quadratic and power-law predictions nearly overlap",
        transform=response_axis.transAxes,
        horizontalalignment="right",
        verticalalignment="bottom",
        color="#36453f",
        fontsize=9.5,
        bbox={"facecolor": "white", "edgecolor": "none", "alpha": 0.86, "pad": 2.5},
    )
    response_axis.legend(loc="upper left", frameon=False, ncol=2)

    residual_axis.axhline(0, color="#36453f", linewidth=1.1, zorder=1)
    marker_offsets = {"Linear": -0.008, "Quadratic": 0.0, "Power law": 0.008}
    for name, prediction in predictions.items():
        residual = response - prediction
        residual_axis.plot(
            command + marker_offsets[name],
            residual,
            color=colours[name],
            marker=markers[name],
            markersize=5.2,
            linewidth=1.8,
            linestyle=line_styles[name],
            label=f"{name} residual",
            zorder=3,
        )

    style_axis(residual_axis)
    residual_axis.set_ylim(-0.12, 0.12)
    residual_axis.set_xlabel(r"Normalised requested PWM, $x$")
    residual_axis.set_ylabel(r"Residual, $v-\hat{v}$")
    residual_axis.set_title(
        "Residual structure and held-back errors distinguish the models",
        loc="left",
        weight="bold",
    )
    residual_axis.legend(loc="lower right", frameon=False, ncol=3)

    figure.tight_layout(pad=1.2)
    figure.savefig(COMPARISON_OUTPUT_PATH, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def main() -> None:
    """Generate both website illustrations."""
    sns.set_theme(style="whitegrid", context="notebook")
    draw_candidate_shapes()
    draw_model_comparison()


if __name__ == "__main__":
    main()
