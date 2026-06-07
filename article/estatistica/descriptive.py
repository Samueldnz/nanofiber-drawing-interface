import pandas as pd
import numpy as np


def calculate_descriptive_stats(
    all_diameters,
    samples
):
    """
    Calculates descriptive statistics
    for all samples.

    Parameters
    ----------
    all_diameters : dict
        Dictionary containing fiber diameters.

    samples : dict
        Sample metadata.

    Returns
    -------
    pandas.DataFrame
    """

    results = []

    for sample, diameters in all_diameters.items():

        info = samples[sample]

        n = len(diameters)

        mean = diameters.mean()

        sd = diameters.std(
            ddof=1
        )

        sem = sd / np.sqrt(n)

        cv = (
            sd / mean
        ) * 100

        median = diameters.median()

        q1 = diameters.quantile(
            0.25
        )

        q3 = diameters.quantile(
            0.75
        )

        iqr = q3 - q1

        min_value = diameters.min()

        max_value = diameters.max()

        results.append({

            "Sample":
                sample,

            "Polymer":
                info["Polymer"],

            "Speed (mm/s)":
                info["Speed"],

            "N":
                n,

            "Mean (μm)":
                round(mean, 2),

            "SD (μm)":
                round(sd, 2),

            "SEM (μm)":
                round(sem, 2),

            "CV (%)":
                round(cv, 2),

            "Median (μm)":
                round(median, 2),

            "Q1 (μm)":
                round(q1, 2),

            "Q3 (μm)":
                round(q3, 2),

            "IQR (μm)":
                round(iqr, 2),

            "Min (μm)":
                round(min_value, 2),

            "Max (μm)":
                round(max_value, 2)
        })

    return pd.DataFrame(
        results
    )