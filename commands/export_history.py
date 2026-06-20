from csv_export import (
    export_history_csv
)


def export_history():

    path = export_history_csv()

    return (

        f"History exported "

        f"to {path}"

    )