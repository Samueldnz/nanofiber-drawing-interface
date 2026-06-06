import pandas as pd


def load_sample(file_path):
    """
    Loads a single sample CSV file and returns
    the fiber diameter column as a numeric Series.

    Parameters
    ----------
    file_path : Path
        CSV file path.

    Returns
    -------
    pandas.Series
        Fiber diameter values.
    """

    df = pd.read_csv(file_path)

    diameters = pd.to_numeric(
        df.iloc[:, 2],
        errors="coerce"
    ).dropna()

    return diameters


def load_all_samples(data_dir, samples):
    """
    Loads all sample CSV files.

    Parameters
    ----------
    data_dir : Path
        Data directory.

    samples : dict
        Sample metadata dictionary.

    Returns
    -------
    dict

        {
            "A": Series,
            "B": Series,
            ...
        }
    """

    all_diameters = {}

    for sample in samples:

        file_path = data_dir / f"{sample}.csv"

        all_diameters[sample] = load_sample(
            file_path
        )

    return all_diameters


def build_anova_dataframe(all_diameters, samples):
    """
    Builds a long-format dataframe suitable for:
        - ANOVA
        - Tukey HSD
        - Interaction plots
        - Group comparisons

    Output columns:
        Diameter
        Polymer
        Condition
        Group

    Returns
    -------
    pandas.DataFrame
    """

    rows = []

    for sample, diameters in all_diameters.items():

        info = samples[sample]

        for diameter in diameters:

            rows.append({
                "Diameter": diameter,
                "Polymer": info["Polymer"],
                "Condition": str(info["Speed"]),
                "Group": (
                    f"{info['Polymer']}"
                    f"-{info['Speed']}"
                )
            })

    return pd.DataFrame(rows)