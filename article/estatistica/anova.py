import pandas as pd

from statsmodels.formula.api import ols
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.multicomp import pairwise_tukeyhsd

from loaders.data_loader import (
    build_anova_dataframe
)

from config import (
    ALPHA,
    ANOVA_DATASET,
    ANOVA_RESULTS,
    TUKEY_ALL,
    TUKEY_OLD_VS_NEW,
    INTERESTING_TUKEY_PAIRS
)


def _filter_tukey_pairs(
    tukey_df,
    interesting_pairs
):
    """
    Filters only selected Tukey comparisons.
    """

    filtered_rows = []

    for _, row in tukey_df.iterrows():

        pair = (
            row["group1"],
            row["group2"]
        )

        reverse_pair = (
            row["group2"],
            row["group1"]
        )

        if (
            pair in interesting_pairs
            or reverse_pair in interesting_pairs
        ):
            filtered_rows.append(row)

    return pd.DataFrame(
        filtered_rows
    )


def run_two_way_anova(
    all_diameters,
    samples
):
    """
    Performs:

    - Two-way ANOVA
    - Tukey HSD
    - Tukey filtering (Old vs New at same speed)

    Parameters
    ----------
    all_diameters : dict
        Dictionary containing all fiber diameters.

    samples : dict
        Sample metadata.

    Returns
    -------
    tuple

        (
            anova_results,
            tukey_df,
            filtered_tukey
        )
    """

    # =====================================
    # BUILD DATASET
    # =====================================

    anova_df = build_anova_dataframe(
        all_diameters,
        samples
    )

    anova_df.to_csv(
        ANOVA_DATASET,
        index=False
    )

    print(
        f"Saved: {ANOVA_DATASET}"
    )

    # =====================================
    # TWO-WAY ANOVA
    # =====================================

    model = ols(
        (
            "Diameter ~ "
            "C(Polymer) + "
            "C(Condition) + "
            "C(Polymer):C(Condition)"
        ),
        data=anova_df
    ).fit()

    anova_results = anova_lm(
        model,
        typ=2
    )

    anova_results.to_csv(
        ANOVA_RESULTS
    )

    print(
        f"Saved: {ANOVA_RESULTS}"
    )

    # =====================================
    # TUKEY HSD
    # =====================================

    tukey = pairwise_tukeyhsd(
        endog=anova_df["Diameter"],
        groups=anova_df["Group"],
        alpha=ALPHA
    )

    tukey_df = pd.DataFrame(
        data=tukey._results_table.data[1:],
        columns=tukey._results_table.data[0]
    )

    tukey_df.to_csv(
        TUKEY_ALL,
        index=False
    )

    print(
        f"Saved: {TUKEY_ALL}"
    )

    # =====================================
    # FILTER ONLY SAME-SPEED COMPARISONS
    # =====================================

    filtered_tukey = (
        _filter_tukey_pairs(
            tukey_df,
            INTERESTING_TUKEY_PAIRS
        )
    )

    filtered_tukey.to_csv(
        TUKEY_OLD_VS_NEW,
        index=False
    )

    print(
        f"Saved: {TUKEY_OLD_VS_NEW}"
    )


    print("\nAnalysis complete.")

    return (
        anova_results,
        tukey_df,
        filtered_tukey
    )