"""Generate the illustrative motor-dynamics plots used by motors.html.

All responses and observations are deterministic, synthetic teaching examples.
They illustrate a model-comparison workflow and do not represent middleware
parameters or values that students should expect to measure on their robot.

Requires NumPy, Matplotlib, and Seaborn.
"""

from pathlib import Path

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


OUTPUT_DIRECTORY = Path(__file__).parent
CANDIDATE_OUTPUT_PATH = OUTPUT_DIRECTORY / "motor_dynamics_candidate_responses.png"
COMPARISON_OUTPUT_PATH = OUTPUT_DIRECTORY / "motor_dynamics_model_comparison.png"

GREEN = "#18775b"
ORANGE = "#d0643b"
BLUE = "#2f6b8a"
GREY = "#65726d"
AMBER = "#f3c978"
DARK = "#36453f"


def slew_response(time: np.ndarray, initial: float, final: float, rate: float) -> np.ndarray:
    """Return a response whose magnitude changes at no more than rate per second."""
    direction = np.sign(final - initial)
    travelled = np.minimum(rate * np.maximum(time, 0.0), abs(final - initial))
    return initial + direction * travelled


def lag_response(time: np.ndarray, initial: float, final: float, tau: float) -> np.ndarray:
    """Return an analytical first-order step response."""
    elapsed = np.maximum(time, 0.0)
    return initial + (final - initial) * (1.0 - np.exp(-elapsed / tau))


def combined_response(
    time: np.ndarray,
    initial: float,
    final: float,
    rate: float,
    tau: float,
) -> np.ndarray:
    """Numerically combine a slew-limited target with first-order lag."""
    if len(time) == 0:
        return np.array([])

    simulation_step = 0.002
    fine_time = np.arange(0.0, float(np.max(time)) + simulation_step, simulation_step)
    limited_target = slew_response(fine_time, initial, final, rate)
    response = np.empty_like(fine_time)
    response[0] = initial
    alpha = 1.0 - np.exp(-simulation_step / tau)
    for index in range(1, len(fine_time)):
        response[index] = response[index - 1] + alpha * (
            limited_target[index] - response[index - 1]
        )
    return np.interp(time, fine_time, response)


def style_axis(axis: plt.Axes) -> None:
    """Apply shared site-aligned styling."""
    axis.set_facecolor("white")
    axis.grid(axis="x", color="#dfe6e2", linewidth=0.8)
    axis.grid(axis="y", color="#edf1ef", linewidth=0.8)
    sns.despine(ax=axis)


def draw_candidate_responses() -> None:
    """Contrast ideal, slew-limited, lagged, and combined candidates."""
    time = np.linspace(-0.25, 1.75, 1001)
    elapsed = np.maximum(time, 0.0)
    initial, final = 0.12, 0.88
    rate, tau = 1.25, 0.30

    ideal = np.where(time < 0.0, initial, final)
    slew = np.where(time < 0.0, initial, slew_response(elapsed, initial, final, rate))
    lag = np.where(time < 0.0, initial, lag_response(elapsed, initial, final, tau))
    combined = np.where(
        time < 0.0,
        initial,
        combined_response(elapsed, initial, final, rate, tau),
    )

    figure, axis = plt.subplots(figsize=(12, 5.2), dpi=180)
    figure.patch.set_facecolor("white")
    style_axis(axis)

    axis.axvline(0.0, color=ORANGE, linewidth=1.4, linestyle=(0, (3, 3)))
    axis.axhline(final, color="#bcc8c2", linewidth=1.1, linestyle=(0, (3, 3)))
    axis.plot(time, ideal, color=GREY, linewidth=2.1, linestyle=(0, (5, 4)), label="Instantaneous candidate")
    axis.plot(time, slew, color=BLUE, linewidth=2.7, label="Slew-limited candidate")
    axis.plot(time, lag, color=GREEN, linewidth=2.7, label="First-order lag candidate")
    axis.plot(time, combined, color=ORANGE, linewidth=2.9, label="Combined candidate")

    axis.annotate(
        "requested step",
        xy=(0.0, final),
        xytext=(0.12, 0.98),
        arrowprops={"arrowstyle": "->", "color": ORANGE, "linewidth": 1.1},
        color=ORANGE,
    )
    axis.text(1.72, final + 0.025, "final settled response", ha="right", color=GREY)
    axis.set_xlim(-0.25, 1.75)
    axis.set_ylim(0.0, 1.05)
    axis.set_xlabel("Elapsed time after the command change (illustrative seconds)")
    axis.set_ylabel("Normalised wheel-speed response")
    axis.set_title(
        "A command step can support several candidate response shapes",
        loc="left",
        weight="bold",
    )
    axis.legend(loc="lower right", frameon=False, ncol=2)

    figure.tight_layout(pad=1.2)
    figure.savefig(CANDIDATE_OUTPUT_PATH, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def fit_candidates(time: np.ndarray, response: np.ndarray, initial: float, final: float):
    """Fit all candidate parameters to the same synthetic observations."""
    rate_values = np.linspace(0.45, 2.60, 216)
    tau_values = np.linspace(0.06, 0.75, 231)

    slew_errors = [
        np.mean((response - slew_response(time, initial, final, rate)) ** 2)
        for rate in rate_values
    ]
    fitted_slew_rate = float(rate_values[int(np.argmin(slew_errors))])

    lag_errors = [
        np.mean((response - lag_response(time, initial, final, tau)) ** 2)
        for tau in tau_values
    ]
    fitted_lag_tau = float(tau_values[int(np.argmin(lag_errors))])

    best_combined = (np.inf, rate_values[0], tau_values[0])
    for rate in rate_values[::3]:
        for tau in tau_values[::3]:
            prediction = combined_response(time, initial, final, float(rate), float(tau))
            error = float(np.mean((response - prediction) ** 2))
            if error < best_combined[0]:
                best_combined = (error, float(rate), float(tau))

    return fitted_slew_rate, fitted_lag_tau, best_combined[1], best_combined[2]


def illustrative_observations(
    time: np.ndarray,
    initial: float,
    final: float,
    rate: float,
    tau: float,
    phase: float,
) -> np.ndarray:
    """Return deterministic observations not exactly equal to any candidate."""
    response = combined_response(time, initial, final, rate, tau)
    offsets = 0.009 * np.sin(17.0 * time + phase) + 0.004 * np.cos(31.0 * time)
    return np.clip(response + offsets, 0.0, 1.0)


def draw_model_comparison() -> None:
    """Fit one synthetic step and test the frozen models on a different step."""
    fitting_time = np.arange(0.0, 1.51, 0.06)
    fitting_initial, fitting_final = 0.12, 0.88
    fitting_observed = illustrative_observations(
        fitting_time, fitting_initial, fitting_final, 1.30, 0.24, 0.2
    )

    fitted_slew_rate, fitted_lag_tau, combined_rate, combined_tau = fit_candidates(
        fitting_time, fitting_observed, fitting_initial, fitting_final
    )

    held_time = np.arange(0.0, 1.51, 0.06)
    held_initial, held_final = 0.78, 0.28
    held_observed = illustrative_observations(
        held_time, held_initial, held_final, 1.30, 0.24, 1.1
    )

    fine_time = np.linspace(0.0, 1.5, 751)
    models = {
        "Slew only": (
            BLUE,
            lambda t, y0, y1: slew_response(t, y0, y1, fitted_slew_rate),
        ),
        "Lag only": (
            GREEN,
            lambda t, y0, y1: lag_response(t, y0, y1, fitted_lag_tau),
        ),
        "Combined": (
            ORANGE,
            lambda t, y0, y1: combined_response(t, y0, y1, combined_rate, combined_tau),
        ),
    }
    line_styles = {"Slew only": (0, (4, 3)), "Lag only": (0, (2, 2)), "Combined": "solid"}

    figure, axes = plt.subplots(
        2,
        2,
        figsize=(12, 7.6),
        dpi=180,
        sharex="col",
        gridspec_kw={"height_ratios": [1.55, 1.0]},
    )
    figure.patch.set_facecolor("white")
    fitting_axis, held_axis = axes[0]
    fitting_residual_axis, held_residual_axis = axes[1]

    for axis in axes.flat:
        style_axis(axis)

    fitting_axis.scatter(
        fitting_time,
        fitting_observed,
        color=DARK,
        s=32,
        zorder=5,
        label="Synthetic observations",
    )
    held_axis.scatter(
        held_time,
        held_observed,
        color=DARK,
        s=32,
        zorder=5,
        label="Held-back observations",
    )

    for name, (colour, model) in models.items():
        fitting_axis.plot(
            fine_time,
            model(fine_time, fitting_initial, fitting_final),
            color=colour,
            linewidth=2.4,
            linestyle=line_styles[name],
            label=name,
        )
        held_axis.plot(
            fine_time,
            model(fine_time, held_initial, held_final),
            color=colour,
            linewidth=2.4,
            linestyle=line_styles[name],
            label=name,
        )

        fitting_residual = fitting_observed - model(
            fitting_time, fitting_initial, fitting_final
        )
        held_residual = held_observed - model(held_time, held_initial, held_final)
        fitting_residual_axis.plot(
            fitting_time,
            fitting_residual,
            color=colour,
            marker="o",
            markersize=3.7,
            linewidth=1.6,
            linestyle=line_styles[name],
        )
        held_residual_axis.plot(
            held_time,
            held_residual,
            color=colour,
            marker="o",
            markersize=3.7,
            linewidth=1.6,
            linestyle=line_styles[name],
        )

    fitting_axis.set_title("Fit: one rising step", loc="left", weight="bold")
    held_axis.set_title("Test: a held-back falling step", loc="left", weight="bold")
    fitting_axis.set_ylabel("Normalised wheel speed")
    fitting_residual_axis.set_ylabel("Residual\n(observed − predicted)")
    fitting_residual_axis.set_xlabel("Elapsed time after step (illustrative seconds)")
    held_residual_axis.set_xlabel("Elapsed time after step (illustrative seconds)")

    for axis in (fitting_axis, held_axis):
        axis.set_xlim(0.0, 1.5)
        axis.set_ylim(0.0, 1.0)
    for axis in (fitting_residual_axis, held_residual_axis):
        axis.axhline(0.0, color=DARK, linewidth=1.0)
        axis.set_ylim(-0.20, 0.20)

    fitting_axis.legend(loc="lower right", frameon=False)
    held_axis.legend(loc="upper right", frameon=False)
    figure.suptitle(
        "Judge temporal models by residuals and a genuinely new transition",
        x=0.06,
        ha="left",
        weight="bold",
    )

    figure.tight_layout(rect=(0, 0, 1, 0.96), pad=1.2)
    figure.savefig(COMPARISON_OUTPUT_PATH, bbox_inches="tight", facecolor="white")
    plt.close(figure)


def main() -> None:
    """Write both teaching figures beside this script."""
    sns.set_theme(context="notebook", style="whitegrid", font_scale=1.0)
    draw_candidate_responses()
    draw_model_comparison()


if __name__ == "__main__":
    main()
