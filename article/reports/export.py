from pathlib import Path


def export_dataframe(
    dataframe,
    output_file,
    excel=False
):
    """
    Exports a dataframe to CSV.

    Optionally exports XLSX.
    """

    output_file.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    dataframe.to_csv(
        output_file,
        index=False
    )

    print(
        f"Saved: {output_file}"
    )