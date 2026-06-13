import matplotlib.pyplot as plt
import numpy as np

from config import (
    HISTOGRAM_DIR,
    SCALE100_DIR,
    SCALE30_DIR,
    HISTOGRAM_BINS,
    FIG_DPI
)

def plot_individual_histograms_scale_100um(
    all_diameters,
    samples
):
    """
    Creates one histogram per sample.
    """

    SCALE100_DIR.mkdir(
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
            figsize=(8, 5)
        )
        custom_bins = np.arange(0, 111, 10)

        diameters_plot = np.clip(
            diameters,
            None,
            109.999
        )

        ax.hist(
            diameters_plot,
            bins=custom_bins,
            edgecolor="black"
        )

        plt.xlim(0,110)

        plt.xticks(
            [0,10,20,30,40,50,60,70,80,90,100],
            ["0","10","20","30","40","50",
            "60","70","80","90",">100"]
        )

        ax.axvline(
            mean,
            linestyle="--",
            linewidth=2,
            label=f"Mean = {mean:.2f}"
        )

        stats_text = (
            f"Mean = {mean:.1f} μm\n"
            f"SD = {sd:.1f} μm\n"
            f"CV = {cv:.1f}%"
        )

        ax.text(
            0.98,
            0.95,
            stats_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=dict(
                boxstyle="round",
                facecolor="white",
                alpha=0.85
            )
        )

        plt.title(
            f"Sample {sample} | "
            f"{info['Polymer']} | "
            f"{info['Speed']} mm/s | "
            f"N={n}"
        )

        plt.xlabel(
            "Fiber Diameter (μm)"
        )

        plt.ylabel(
            "Frequency"
        )

        plt.ylim(0, 100)

        plt.yticks(
            np.arange(0, 101, 10)
        )

        plt.legend()

        plt.tight_layout()

        output_file = (
            SCALE100_DIR /
            f"sample_{sample}_histogram.png"
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


def plot_histogram_comparison_scale_100um(
    all_diameters,
    samples
):
    """
    Creates a 2x3 histogram comparison figure
    using frequency.
    """

    SCALE100_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    fig, axes = plt.subplots(
        2,
        3,
        figsize=(16, 8),
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

        diameters = all_diameters[sample]

        mean = diameters.mean()
        sd = diameters.std(ddof=1)
        cv = (sd / mean) * 100
        n = len(diameters)

        custom_bins = np.arange(0, 111, 10)

        diameters_plot = np.clip(
            diameters,
            None,
            109.999
        )
        
        ax.hist(
            diameters_plot,
            bins=custom_bins,
            edgecolor="black"
        )

        ax.set_xlim(0, 110)

        ax.set_xticks(
            [0,10,20,30,40,50,60,70,80,90,100]
        )

        ax.set_xticklabels(
            ["0","10","20","30","40","50",
            "60","70","80","90","≥100"]
        )

        ax.set_ylim(0, 100)
        ax.set_yticks(np.arange(0, 101, 10))

        ax.tick_params(
            axis='both',
            labelsize=8,
            labelleft=True,
            labelbottom=True
        )

        ax.axvline(
            mean,
            linestyle="--",
            linewidth=2
        )

        stats_text = (
            f"Mean = {mean:.1f} μm\n"
            f"SD = {sd:.1f} μm\n"
            f"CV = {cv:.1f}%"
        )

        ax.text(
            0.98,
            0.95,
            stats_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=dict(
                boxstyle="round",
                facecolor="white",
                alpha=0.85
            )
        )

    axes[0,0].set_title("21 mm/s\nSample A")
    axes[0,1].set_title("42 mm/s\nSample B")
    axes[0,2].set_title("84 mm/s\nSample C")

    axes[1,0].set_title("Sample D")
    axes[1,1].set_title("Sample E")
    axes[1,2].set_title("Sample F")

    axes[0,0].set_ylabel(
        "AS\n\nFrequency",
        fontsize=12,
        fontweight="bold"
    )

    axes[1,0].set_ylabel(
        "FS\n\nFrequency",
        fontsize=12,
        fontweight="bold"
    )

    for ax in axes[1]:
        ax.set_xlabel(
            "Fiber Diameter (μm)"
        )

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
        SCALE100_DIR /
        "histograms_2x3_comparison.png"
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



def plot_individual_histograms_scale_30um(
    all_diameters,
    samples
):
    """
    Creates one histogram per sample.
    """

    SCALE30_DIR.mkdir(
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
            figsize=(8, 5)
        )
        custom_bins = np.arange(0, 31, 1)

        ax.hist(
            diameters,
            bins=custom_bins,
            edgecolor="black"
        )

        plt.xlim(0,30)

        plt.xticks(np.arange(0, 31, 1))

        ax.axvline(
            mean,
            linestyle="--",
            linewidth=2,
            label=f"Mean = {mean:.2f}"
        )

        stats_text = (
            f"Mean = {mean:.1f} μm\n"
            f"SD = {sd:.1f} μm\n"
            f"CV = {cv:.1f}%"
        )

        ax.text(
            0.98,
            0.95,
            stats_text,
            transform=ax.transAxes,
            fontsize=9,
            verticalalignment="top",
            horizontalalignment="right",
            bbox=dict(
                boxstyle="round",
                facecolor="white",
                alpha=0.85
            )
        )

        plt.title(
            f"Sample {sample} | "
            f"{info['Polymer']} | "
            f"{info['Speed']} mm/s | "
            f"N={n}"
        )

        plt.xlabel(
            "Fiber Diameter (μm)"
        )

        plt.ylabel(
            "Frequency"
        )

        plt.ylim(0, 100)

        plt.yticks(
            np.arange(0, 101, 10)
        )

        plt.legend()

        plt.tight_layout()

        output_file = (
            SCALE30_DIR /
            f"sample_{sample}_histogram.png"
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




