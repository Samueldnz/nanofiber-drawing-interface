from pathlib import Path
import shutil

from config import OUTPUT_DIR

from config import (
    DATA_DIR,
    SAMPLES,
    DESCRIPTIVE_CSV
)

from loaders.data_loader import (
    load_all_samples
)

from estatistica.descriptive import (
    calculate_descriptive_stats
)

from estatistica.anova import (
    run_two_way_anova
)

from plots.histogram import (
    plot_individual_histograms,
    plot_histogram_comparison
)

from plots.boxplot import (
    plot_individual_boxplots,
    plot_boxplot_comparison
)

from plots.trends import (
    plot_speed_vs_mean_sem
)

from reports.export import (
    export_dataframe
)

def clear_output_directory():
    """
    Removes all generated files from output directory.
    Keeps folder structure intact.
    """

    if not OUTPUT_DIR.exists():

        print(
            "\nOutput directory does not exist."
        )

        return

    confirmation = input(
        "\nAre you sure you want to delete all generated files? (y/n): "
    ).strip().lower()

    if confirmation != "y":

        print(
            "\nOperation cancelled."
        )

        return

    deleted_files = 0

    for item in OUTPUT_DIR.rglob("*"):

        try:

            if item.is_file():

                item.unlink()
                deleted_files += 1

        except Exception as error:

            print(
                f"Could not remove {item}: {error}"
            )

    print(
        f"\n{deleted_files} file(s) removed from output."
    )


def print_menu():

    print("\n" + "=" * 50)
    print("FIBER DATA ANALYSIS")
    print("=" * 50)

    print("1 - Descriptive Statistics")
    print("2 - Individual Histograms")
    print("3 - Histogram Comparison (2x3)")
    print("4 - Individual Boxplots")
    print("5 - Boxplot Comparison (2x3)")
    print("6 - Trend Plot (Mean ± SEM)")
    print("7 - Two-Way ANOVA + Tukey")
    print("8 - Run Everything")
    print("9 - Clear Output Folder")
    print("0 - Exit")

    print("=" * 50)


def run_descriptive_statistics(
    all_diameters
):

    summary_df = calculate_descriptive_stats(
        all_diameters,
        SAMPLES
    )

    export_dataframe(
        summary_df,
        DESCRIPTIVE_CSV,
        excel=True
    )

    print("\nDescriptive statistics completed.")


def run_everything(
    all_diameters
):

    print("\nRunning complete analysis...\n")

    # ---------------------------------
    # Descriptive Statistics
    # ---------------------------------

    summary_df = calculate_descriptive_stats(
        all_diameters,
        SAMPLES
    )

    export_dataframe(
        summary_df,
        DESCRIPTIVE_CSV,
    )

    # ---------------------------------
    # Histograms
    # ---------------------------------

    plot_individual_histograms(
        all_diameters,
        SAMPLES
    )

    plot_histogram_comparison(
        all_diameters,
        SAMPLES
    )

    # ---------------------------------
    # Boxplots
    # ---------------------------------

    plot_individual_boxplots(
        all_diameters,
        SAMPLES
    )

    plot_boxplot_comparison(
        all_diameters,
        SAMPLES
    )

    # ---------------------------------
    # Trends
    # ---------------------------------

    plot_speed_vs_mean_sem(
        all_diameters,
        SAMPLES
    )

    # ---------------------------------
    # ANOVA
    # ---------------------------------

    run_two_way_anova(
        all_diameters,
        SAMPLES
    )

    print("\nComplete analysis finished.")


def main():

    print("\nLoading data...")

    all_diameters = load_all_samples(
        DATA_DIR,
        SAMPLES
    )

    print("Data loaded successfully.")

    while True:

        print_menu()

        choice = input(
            "\nSelect an option: "
        ).strip()

        try:

            if choice == "1":

                run_descriptive_statistics(
                    all_diameters
                )

            elif choice == "2":

                plot_individual_histograms(
                    all_diameters,
                    SAMPLES
                )

            elif choice == "3":

                plot_histogram_comparison(
                    all_diameters,
                    SAMPLES
                )


            elif choice == "4":

                plot_individual_boxplots(
                    all_diameters,
                    SAMPLES
                )

            elif choice == "5":

                plot_boxplot_comparison(
                    all_diameters,
                    SAMPLES
                )

            elif choice == "6":

                plot_speed_vs_mean_sem(
                    all_diameters,
                    SAMPLES
                )

            elif choice == "7":

                run_two_way_anova(
                    all_diameters,
                    SAMPLES
                )

            elif choice == "8":

                run_everything(
                    all_diameters
                )

            elif choice == "9":

                clear_output_directory()

            elif choice == "0":

                print(
                    "\nClosing application..."
                )

                break

            else:

                print(
                    "\nInvalid option."
                )

        except Exception as error:

            print(
                f"\nERROR: {error}"
            )


if __name__ == "__main__":
    main()