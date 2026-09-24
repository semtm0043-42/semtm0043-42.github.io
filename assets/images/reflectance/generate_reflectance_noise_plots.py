"""Generate the illustrative uniform-noise figure used in Reflectance Exercise 6."""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns


OUTPUT_DIRECTORY = Path(__file__).resolve().parent
RANDOM_SEED = 20260909


def generate_uniform_candidate_figure() -> None:
    """Plot finite synthetic residuals against their uniform candidate model."""

    rng = np.random.default_rng(RANDOM_SEED)

    # These values are illustrative, not expected measurements or middleware
    # parameters. A finite sample will not make every histogram bar identical.
    lower_bound_us = -10.0
    upper_bound_us = 10.0
    residual_us = rng.uniform(lower_bound_us, upper_bound_us, size=240)
    uniform_density = 1.0 / (upper_bound_us - lower_bound_us)

    sns.set_theme(style="whitegrid")
    figure, axis = plt.subplots(figsize=(9, 5))

    sns.histplot(
        x=residual_us,
        stat="density",
        bins=20,
        kde=True,
        color=sns.color_palette("deep")[0],
        alpha=0.45,
        ax=axis,
    )

    # Include the zero-density regions so the model's bounded support is clear.
    axis.plot(
        [-15, lower_bound_us, lower_bound_us, upper_bound_us, upper_bound_us, 15],
        [0, 0, uniform_density, uniform_density, 0, 0],
        color="black",
        linewidth=1.8,
        label="Uniform candidate",
    )

    axis.set(
        xlabel="residual_us",
        ylabel="Density",
        xlim=(-15, 15),
        ylim=(0, 0.09),
    )
    axis.legend(loc="upper right")
    figure.tight_layout()
    figure.savefig(
        OUTPUT_DIRECTORY / "uniform_candidate.png",
        dpi=100,
        metadata={"Software": "Python, Matplotlib and Seaborn"},
    )
    plt.close(figure)


if __name__ == "__main__":
    generate_uniform_candidate_figure()
