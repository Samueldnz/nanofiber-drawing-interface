import matplotlib.pyplot as plt
import numpy as np

from config import (
    HISTOGRAM_DIR,
    HISTOGRAM_BINS,
    FIG_DPI
)


def _get_global_frequency_scale(
    all_diameters
):
    """
    Finds the maximum histogram frequency
    among all samples.
    """

    max_frequency = 0

    for diameters in all_diameters.values():

        counts, _ = np.histogram(
            diameters,
            bins=HISTOGRAM_BINS
        )

        max_frequency = max(
            max_frequency,
            counts.max()
        )

    return max_frequency


def _get_global_density_scale(
    all_diameters
):
    """
    Finds the maximum histogram density
    among all samples.
    """

    max_density = 0

    for diameters in all_diameters.values():

        counts, _ = np.histogram(
            diameters,
            bins=HISTOGRAM_BINS,
            density=True
        )

        max_density = max(
            max_density,
            counts.max()
        )

    return max_density


def plot_individual_histograms(
    all_diameters,
    samples
):
    """
    Creates one histogram per sample.
    """

    HISTOGRAM_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    for sample, info in samples.items():

        diameters = all_diameters[sample]

        mean = diameters.mean()
        n = len(diameters)

        plt.figure(
            figsize=(8, 5)
        )

        plt.hist(
            diameters,
            bins=HISTOGRAM_BINS,
            edgecolor="black"
        )

        plt.axvline(
            mean,
            linestyle="--",
            linewidth=2,
            label=f"Mean = {mean:.2f}"
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

        plt.legend()

        plt.tight_layout()

        output_file = (
            HISTOGRAM_DIR /
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


def plot_histogram_comparison(
    all_diameters,
    samples
):
    """
    Creates a 2x3 histogram comparison figure
    using frequency.
    """

    HISTOGRAM_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    max_frequency = (
        _get_global_frequency_scale(
            all_diameters
        )
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

        ax.hist(
            diameters,
            bins=HISTOGRAM_BINS,
            edgecolor="black"
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

        ax.set_ylim(
            0,
            max_frequency * 1.10
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
        HISTOGRAM_DIR /
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


def plot_density_histogram_comparison(
    all_diameters,
    samples
):
    """
    Creates a 2x3 histogram comparison
    using probability density.
    """

    HISTOGRAM_DIR.mkdir(
        parents=True,
        exist_ok=True
    )

    max_density = (
        _get_global_density_scale(
            all_diameters
        )
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

        ax.hist(
            diameters,
            bins=HISTOGRAM_BINS,
            density=True,
            alpha=0.75,
            edgecolor="black"
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

        ax.set_ylim(
            0,
            max_density * 1.10
        )

    axes[0,0].set_title("21 mm/s\nA")
    axes[0,1].set_title("42 mm/s\nB")
    axes[0,2].set_title("84 mm/s\nC")

    axes[1,0].set_title("D")
    axes[1,1].set_title("E")
    axes[1,2].set_title("F")

    axes[0,0].set_ylabel(
        "AS\n\nDensity",
        fontsize=12,
        fontweight="bold"
    )

    axes[1,0].set_ylabel(
        "FS\n\nDensity",
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
        HISTOGRAM_DIR /
        "histograms_2x3_density.png"
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