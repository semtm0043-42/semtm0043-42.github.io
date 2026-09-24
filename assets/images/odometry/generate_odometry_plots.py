"""Reproduce the synthetic teaching figures in odometry.html.

Run with Python, NumPy, Matplotlib and Seaborn. All data and parameters are
illustrative: this script does not read robot logs or hidden middleware values.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

OUTPUT = Path(__file__).resolve().parent
BLUE, ORANGE, GREEN = "#416da3", "#bc5935", "#23836d"


def save(fig, name):
    fig.suptitle("Illustrative data — not robot measurements", fontsize=11)
    fig.tight_layout(rect=(0, 0, 1, 0.95))
    fig.savefig(OUTPUT / name, dpi=160,
                metadata={"Software": "Python, Matplotlib and Seaborn"})
    plt.close(fig)


def calibration_plot(x, measured, held, nominal, fitted, labels, name):
    """Plot the same repeated observations and frozen predictions in both panels."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    grid = np.linspace(min(0, x.min()), x.max(), 200)
    for ax in axes:
        ax.axhline(0, color="0.5", lw=0.8)
    for mask, marker, label in [(~held, "o", "Calibration"),
                                (held, "X", "Held back")]:
        sns.scatterplot(x=x[mask], y=measured[mask], marker=marker,
                        color=BLUE, label=label, ax=axes[0], s=55)
    for slope, label, color in [(nominal, "Nominal", ORANGE),
                                 (fitted, "Fitted", GREEN)]:
        axes[0].plot(grid, slope * grid, color=color, label=label)
        for mask, marker in [(~held, "o"), (held, "X")]:
            sns.scatterplot(x=x[mask], y=measured[mask] - slope * x[mask],
                            marker=marker, color=color, s=55, ax=axes[1],
                            label=label if marker == "o" else None)
    axes[0].set(xlabel=labels[0], ylabel=labels[1], title="Response and model")
    axes[1].set(xlabel=labels[0], ylabel=labels[2],
                title="Measured minus estimated")
    for ax in axes:
        ax.legend(fontsize=9)
    save(fig, name)


def radius_figure():
    rng = np.random.default_rng(3103)
    counts = np.repeat([350, 650, 950, 1250, 1550], 4).astype(float)
    measured = 0.285 * counts + rng.normal(0, 2, counts.size)
    held = counts == 1250
    fitted = np.dot(counts[~held], measured[~held]) / np.dot(
        counts[~held], counts[~held])
    calibration_plot(counts, measured, held, 0.265, fitted,
                     ("Mean encoder change (counts)", "Measured distance (mm)",
                      "Distance residual (mm)"), "radius_calibration.png")


def separation_figure():
    rng = np.random.default_rng(3104)
    differential = np.repeat([-180, -120, -60, 60, 120, 180], 4).astype(float)
    measured = differential / 88 + rng.normal(0, 0.015, differential.size)
    held = np.abs(differential) == 120
    fitted = np.dot(differential[~held], measured[~held]) / np.dot(
        differential[~held], differential[~held])
    calibration_plot(differential, measured, held, 1 / 97, fitted,
                     ("Differential wheel travel (mm)", "Measured heading (rad)",
                      "Heading residual (rad)"), "separation_calibration.png")


def trajectory(left_steps, right_steps, left_scale, right_scale,
               separation=90):
    """Euler integration with the same OLD-heading ordering as the class."""
    x, y, theta = [0.0], [0.0], [0.0]
    for left, right in zip(left_steps, right_steps):
        sl, sr = left * left_scale, right * right_scale
        ds = (sl + sr) / 2
        x.append(x[-1] + ds * np.cos(theta[-1]))
        y.append(y[-1] + ds * np.sin(theta[-1]))
        theta.append(theta[-1] + (sr - sl) / separation)
    return np.array(x), np.array(y), np.array(theta)


def asymmetry_figure():
    steps = np.ones(400)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    cases = [(steps, steps, 1, 1.02, "Equal counts; unequal radii"),
             (steps, steps * 1.02, 1, 1, "Unequal counts; equal radii")]
    paths = []
    for ax, (left, right, kl, kr, title) in zip(axes, cases):
        x, y, _ = trajectory(left, right, kl, kr)
        paths.append((x, y))
        sns.lineplot(x=x, y=y, ax=ax, color=BLUE, label="Candidate path")
        ax.plot([0, 410], [0, 0], "--", color="0.45", label="Straight reference")
        ax.set(title=title, xlabel="Forward position x (mm)",
               ylabel="Lateral position y (mm)", xlim=(-10, 420), ylim=(-8, 28))
        ax.text(0.03, 0.94, "Lateral scale enlarged", transform=ax.transAxes,
                fontsize=9, va="top")
        ax.legend(loc="lower right", fontsize=9)
    assert np.allclose(paths[0], paths[1])
    save(fig, "asymmetry_candidates.png")


def model_trajectory_figure():
    """Compare predictions with endpoint observations, not an invented path."""
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    cases = [(260, np.array([0.8, -0.7]), "Calibration example"),
             (400, np.array([-1.2, 1.0]), "Held-back example")]
    for ax, (length, observation_error, title) in zip(axes, cases):
        counts = np.ones(length)
        shared = trajectory(counts, counts, 1.0, 1.0)
        separate = trajectory(counts, counts, 0.99, 1.01)
        observed = np.array([separate[0][-1], separate[1][-1]]) + observation_error

        sns.lineplot(x=shared[0], y=shared[1], ax=ax, color=ORANGE,
                     label="Shared-radius prediction")
        sns.lineplot(x=separate[0], y=separate[1], ax=ax, color=GREEN,
                     label="Separate-radius prediction")
        ax.scatter(observed[0], observed[1], marker="X", s=95, color=BLUE,
                   label="Observed endpoint", zorder=4)
        ax.scatter(0, 0, marker="o", s=35, color="0.2", label="Recorded start")
        ax.set(title=title, xlabel="x position (mm)",
               ylabel="y position (mm)")
        ax.text(0.97, 0.05, "No measured path assumed", transform=ax.transAxes,
                fontsize=9, va="bottom", ha="right")
        ax.legend(fontsize=8, loc="upper left")
    save(fig, "model_comparison_trajectories.png")


def model_residual_figure():
    """Show signed endpoint residuals for calibration and held-back trials."""
    conditions = [
        ("Forward 200", np.ones(200), np.ones(200)),
        ("Forward 350", np.ones(350), np.ones(350)),
        ("Reverse 250", -np.ones(250), -np.ones(250)),
        ("Left turn", -np.ones(70), np.ones(70)),
        ("Forward 425", np.ones(425), np.ones(425)),
        ("Right turn", np.ones(85), -np.ones(85)),
    ]
    observation_error = np.array([
        [0.8, -0.4, 0.20], [-1.0, 0.9, -0.25],
        [0.6, -0.7, 0.15], [-0.5, 0.4, -0.30],
        [1.1, -0.8, 0.20], [-0.7, 0.5, -0.20],
    ])
    models = [("Shared radii", 1.0, 1.0, ORANGE),
              ("Separate radii", 0.99, 1.01, GREEN)]
    residuals = {name: [] for name, *_ in models}

    for index, (_, left, right) in enumerate(conditions):
        physical = trajectory(left, right, 0.99, 1.01)
        observed = np.array([
            physical[0][-1] + observation_error[index, 0],
            physical[1][-1] + observation_error[index, 1],
            np.degrees(physical[2][-1]) + observation_error[index, 2],
        ])
        for name, left_scale, right_scale, _ in models:
            predicted = trajectory(left, right, left_scale, right_scale)
            estimate = np.array([
                predicted[0][-1], predicted[1][-1],
                np.degrees(predicted[2][-1]),
            ])
            residuals[name].append(observed - estimate)

    fig, axes = plt.subplots(1, 3, figsize=(12, 4.4), sharex=True)
    x_position = np.arange(len(conditions))
    for ax, column, ylabel in zip(
            axes, range(3), ["x residual (mm)", "y residual (mm)",
                             "Heading residual (degrees)"]):
        ax.axhline(0, color="0.35", lw=1, label="Perfect prediction")
        ax.axvspan(3.5, 5.5, color=BLUE, alpha=0.08)
        for model_index, (name, _, _, color) in enumerate(models):
            values = np.asarray(residuals[name])[:, column]
            offset = -0.07 + 0.14 * model_index
            sns.scatterplot(x=x_position[:4] + offset, y=values[:4], marker="o",
                            s=55, color=color, label=name, ax=ax)
            sns.scatterplot(x=x_position[4:] + offset, y=values[4:], marker="X",
                            s=75, color=color, ax=ax, legend=False)
        ax.axvline(3.5, color="0.5", ls="--", lw=0.9)
        ax.set(xlabel="Movement condition", ylabel=ylabel,
               xticks=x_position)
        ax.set_xticklabels([item[0] for item in conditions], rotation=35,
                           ha="right")
        ax.legend(fontsize=7)
    axes[0].text(0.03, 0.95, "Calibration trials", transform=axes[0].transAxes,
                 fontsize=9, va="top")
    axes[2].text(0.97, 0.95, "Held back", transform=axes[2].transAxes,
                 fontsize=9, va="top", ha="right", color=BLUE)
    save(fig, "model_comparison_residuals.png")


def integrate(values, time):
    """Left-endpoint integration with an explicit zero initial value."""
    return np.r_[0, np.cumsum(values[:-1] * np.diff(time))]


def gyro_figure():
    rng = np.random.default_rng(3106)
    time = np.linspace(0, 30, 1501)
    rate = 0.24 + 0.0015 * time + rng.normal(0, 0.035, time.size)
    fit = time < 10
    bias = rate[fit].mean()
    evaluation_time = time[~fit] - time[~fit][0]
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.4))
    sns.lineplot(x=time, y=rate, ax=axes[0], color=BLUE, lw=0.8)
    axes[0].axvspan(0, 10, color=GREEN, alpha=0.12, label="Bias calibration")
    axes[0].axhline(bias, color=GREEN, label="Calibration mean")
    axes[0].axvline(10, color="0.5", ls="--")
    axes[0].set(xlabel="Acquisition time (s)", ylabel="Gyro rate (degrees/s)",
                title="Stationary rate: bias and variation")
    for values, label, color in [(rate[~fit], "Uncorrected", ORANGE),
                                  (rate[~fit] - bias, "Fixed bias removed", GREEN)]:
        sns.lineplot(x=evaluation_time, y=integrate(values, evaluation_time),
                     ax=axes[1], color=color, label=label)
    axes[1].axhline(0, color="0.4", ls=":", label="Stationary reference")
    axes[1].set(xlabel="Time in evaluation segment (s)",
                ylabel="Estimated heading (degrees)", title="Integrated evaluation segment")
    for ax in axes:
        ax.legend(fontsize=8)
    save(fig, "gyro_drift.png")


def acceleration_figure():
    rng = np.random.default_rng(3107)
    time = np.linspace(0, 10, 1001)
    noise = rng.normal(0, 0.005, time.size)
    fig, axes = plt.subplots(1, 3, figsize=(12, 4.2))
    for acceleration, label, color in [(noise, "Zero-mean noise model", BLUE),
                                        (noise + 0.01, "Noise + constant bias", ORANGE)]:
        velocity = integrate(acceleration, time)
        displacement = integrate(velocity, time)
        for ax, values in zip(axes, [acceleration, velocity, displacement]):
            sns.lineplot(x=time, y=values, ax=ax, label=label, color=color, lw=1)
    axes[2].plot(time, 0.5 * 0.01 * time**2, ":", color="black",
                 label="Constant-bias prediction")
    for ax, title, unit in zip(axes, ["Acceleration error", "Velocity error",
                                     "Displacement error"], ["m/s²", "m/s", "m"]):
        ax.axhline(0, color="0.6", lw=0.7)
        ax.set(title=title, xlabel="Time (s)", ylabel=unit)
        ax.legend(fontsize=7, loc="upper left")
    save(fig, "acceleration_integration.png")


if __name__ == "__main__":
    sns.set_theme(style="whitegrid", context="notebook")
    radius_figure()
    separation_figure()
    asymmetry_figure()
    model_trajectory_figure()
    model_residual_figure()
    gyro_figure()
    acceleration_figure()
