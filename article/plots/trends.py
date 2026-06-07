import matplotlib.pyplot as plt
import numpy as np

from config import (
    TREND_DIR,
    OLD_COLOR,
    NEW_COLOR,
    FIG_DPI
)


def _prepare_trend_data(
    all_diameters,
    samples
):
    """
    Prepares trend data grouped by polymer age
    and ordered by printing speed.

    Returns
    -------
    tuple
        (
            old_speeds,
            old_means,
            old_sems,
            new_speeds,
            new_means,
            new_sems
        )
    """

    old_speeds = []
    old_means = []
    old_sems = []

    new_speeds = []
    new_means = []
    new_sems = []

    for sample, info in samples.items():

        diameters = all_diameters[sample]

        mean = diameters.mean()

        sd = diameters.std(
            ddof=1
        )

        n = len(diameters)

        sem = sd / np.sqrt(n)

        if info["Polymer"] == "AS":

            old_speeds.append(
                info["Speed"]
            )

            old_means.append(
                mean
            )

            old_sems.append(
                sem
            )

        else:

            new_speeds.append(
                info["Speed"]
            )

            new_means.append(
                mean
            )

            new_sems.append(
                sem
            )

    old_data = sorted(
        zip(
            old_speeds,
            old_means,
            old_sems
        ),
        key=lambda x: x[0]
    )

    new_data = sorted(
        zip(
            new_speeds,
            new_means,
            new_sems
        ),
        key=lambda x: x[0]
    )

    old_speeds, old_means, old_sems = map(
        list,
        zip(*old_data)
    )

    new_speeds, new_means, new_sems = map(
        list,
        zip(*new_data)
    )

    return (
        old_speeds,
        old_means,
        old_sems,
        new_speeds,
        new_means,
        new_sems
    )


def plot_speed_vs_mean_sem(
    all_diameters,
    samples
):
    """
    Creates a line plot showing
    mean fiber diameter versus printing speed.

    Error bars represent SEM.
    """

    TREND_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    (
        old_speeds,
        old_means,
        old_sems,
        new_speeds,
        new_means,
        new_sems
    ) = _prepare_trend_data(
        all_diameters,
        samples
    )

    plt.figure(
        figsize=(8, 6)
    )

    # =====================================
    # OLD SOLUTION
    # =====================================

    plt.errorbar(
        old_speeds,
        old_means,
        yerr=old_sems,
        fmt="o-",
        color=OLD_COLOR,
        linewidth=2,
        markersize=8,
        capsize=5,
        label="Aged Solution"
    )

    # =====================================
    # NEW SOLUTION
    # =====================================

    plt.errorbar(
        new_speeds,
        new_means,
        yerr=new_sems,
        fmt="s-",
        color=NEW_COLOR,
        linewidth=2,
        markersize=8,
        capsize=5,
        label="Fresh Solution"
    )

    # =====================================
    # VALUE LABELS
    # =====================================

    for x, y in zip(
        old_speeds,
        old_means
    ):

        plt.annotate(
            f"{y:.1f}",
            (x, y),
            xytext=(0, 10),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            fontweight="bold"
        )

    for x, y in zip(
        new_speeds,
        new_means
    ):

        plt.annotate(
            f"{y:.1f}",
            (x, y),
            xytext=(0, -15),
            textcoords="offset points",
            ha="center",
            fontsize=9,
            fontweight="bold"
        )

    # =====================================
    # AXES
    # =====================================

    plt.xlabel(
        "Drawing Speed (mm/s)",
        fontsize=12
    )

    plt.ylabel(
        "Mean Fiber Diameter (μm)",
        fontsize=12
    )

    plt.title(
        "Effect of Drawing Speed on Fiber Diameter",
        fontsize=14,
        fontweight="bold"
    )

    plt.xticks(
        [21, 42, 84]
    )

    plt.grid(
        linestyle="--",
        alpha=0.3
    )

    plt.legend()

    plt.tight_layout()

    # =====================================
    # SAVE
    # =====================================

    output_file = (
        TREND_DIR /
        "speed_vs_mean_diameter_sem.png"
    )

    plt.savefig(
        output_file,
        dpi=FIG_DPI,
        bbox_inches="tight"
    )

    plt.close()

    print(
        f"Saved: {output_file}"
    )