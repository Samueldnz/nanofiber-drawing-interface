import matplotlib.pyplot as plt

from config import (
    BOXPLOT_DIR,
    OLD_COLOR,
    NEW_COLOR,
    FIG_DPI
)


def _get_box_color(polymer):
    """
    Returns the box color according to polymer age.
    """

    if polymer == "AS":
        return OLD_COLOR

    return NEW_COLOR


def plot_individual_boxplots(
    all_diameters,
    samples
):
    """
    Creates one boxplot per sample.

    Parameters
    ----------
    all_diameters : dict
        Dictionary containing fiber diameters.

    samples : dict
        Sample metadata.
    """

    BOXPLOT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for sample, info in samples.items():

        diameters = all_diameters[sample]

        mean = diameters.mean()
        sd = diameters.std(ddof=1)
        cv = (sd / mean) * 100
        n = len(diameters)

        fig, ax = plt.subplots(
            figsize=(6, 6)
        )

        box_color = _get_box_color(
            info["Polymer"]
        )

        bp = ax.boxplot(
            diameters,
            vert=True,
            patch_artist=True,
            showfliers=True,
            showmeans=True,
            widths=0.5,
            meanprops=dict(
                marker="D",
                markerfacecolor="red",
                markeredgecolor="black",
                markersize=7
            ),
            medianprops=dict(
                color="black",
                linewidth=2
            ),
            whiskerprops=dict(
                linewidth=1.5
            ),
            capprops=dict(
                linewidth=1.5
            ),
            flierprops=dict(
                marker="o",
                markersize=4,
                markerfacecolor="gray",
                markeredgecolor="black",
                alpha=0.7
            )
        )

        bp["boxes"][0].set(
            facecolor=box_color,
            alpha=0.75,
            edgecolor="black",
            linewidth=1.5
        )

        ax.set_title(
            f"Sample {sample} (N={n})\n"
            f"{info['Polymer']} | {info['Speed']} mm/s",
            fontweight="bold"
        )

        ax.set_ylabel(
            "Fiber Diameter (μm)"
        )

        stats_text = (
            f"N = {n}\n"
            f"Mean = {mean:.1f} μm\n"
            f"SD = {sd:.1f} μm\n"
            f"CV = {cv:.1f}%"
        )

        ax.text(
            0.98,
            0.98,
            stats_text,
            transform=ax.transAxes,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=dict(
                boxstyle="round",
                facecolor="white",
                alpha=0.85
            )
        )

        plt.tight_layout()

        output_file = (
            BOXPLOT_DIR /
            f"boxplot_sample_{sample}.png"
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


def plot_boxplot_comparison(
    all_diameters,
    samples
):
    """
    Creates a 2x3 boxplot comparison figure.

    Layout:

                         21      42      84
    Aged Solution        A       B       C
    Fresh Solution       D       E       F
    """

    BOXPLOT_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    global_min = min(
        diameters.min()
        for diameters in all_diameters.values()
    )

    global_max = max(
        diameters.max()
        for diameters in all_diameters.values()
    )

    padding = (
        global_max - global_min
    ) * 0.05

    fig, axes = plt.subplots(
        2,
        3,
        figsize=(14, 8),
        sharey=True
    )

    ordered_samples = [
        "A", "B", "C",
        "D", "E", "F"
    ]

    for ax, sample in zip(
        axes.flatten(),
        ordered_samples
    ):

        info = samples[sample]

        diameters = all_diameters[sample]

        mean = diameters.mean()
        sd = diameters.std(ddof=1)
        cv = (sd / mean) * 100
        n = len(diameters)

        box_color = _get_box_color(
            info["Polymer"]
        )

        bp = ax.boxplot(
            diameters,
            patch_artist=True,
            widths=0.5,
            showfliers=True,
            showmeans=True,
            meanprops=dict(
                marker="D",
                markerfacecolor="red",
                markeredgecolor="black",
                markersize=6
            ),
            medianprops=dict(
                color="black",
                linewidth=2
            )
        )

        bp["boxes"][0].set(
            facecolor=box_color,
            alpha=0.75
        )

        stats_text = (
            f"N = {n}\n"
            f"Mean = {mean:.1f} μm\n"
            f"SD = {sd:.1f} μm\n"
            f"CV = {cv:.1f}%"
        )

        ax.text(
            0.98,
            0.98,
            stats_text,
            transform=ax.transAxes,
            fontsize=8,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=dict(
                boxstyle="round",
                facecolor="white",
                alpha=0.85
            )
        )

        ax.set_ylim(
            global_min - padding,
            global_max + padding
        )

        ax.set_xticks([])

    # =====================================
    # COLUMN TITLES
    # =====================================

    axes[0, 0].set_title(
        f"21 mm/s\nA (N={len(all_diameters['A'])})",
        fontweight="bold"
    )

    axes[0, 1].set_title(
        f"42 mm/s\nB (N={len(all_diameters['B'])})",
        fontweight="bold"
    )

    axes[0, 2].set_title(
        f"84 mm/s\nC (N={len(all_diameters['C'])})",
        fontweight="bold"
    )

    axes[1, 0].set_title(
        f"D (N={len(all_diameters['D'])})",
        fontweight="bold"
    )

    axes[1, 1].set_title(
        f"E (N={len(all_diameters['E'])})",
        fontweight="bold"
    )

    axes[1, 2].set_title(
        f"F (N={len(all_diameters['F'])})",
        fontweight="bold"
    )

    # =====================================
    # ROW LABELS
    # =====================================

    axes[0, 0].set_ylabel(
        "AS\n\nFiber Diameter (μm)",
        fontsize=12,
        fontweight="bold"
    )

    axes[1, 0].set_ylabel(
        "FS\n\nFiber Diameter (μm)",
        fontsize=12,
        fontweight="bold"
    )

    # =====================================
    # GLOBAL TITLE
    # =====================================

    fig.suptitle(
        "Fiber Diameter Distribution by Solution Age and Printing Speed",
        fontsize=16,
        fontweight="bold"
    )

    plt.tight_layout()

    plt.subplots_adjust(
        top=0.90
    )

    output_file = (
        BOXPLOT_DIR /
        "boxplots_2x3_comparison.png"
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