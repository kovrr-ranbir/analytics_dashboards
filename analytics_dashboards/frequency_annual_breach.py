import pandas as pd

from analytics_dashboards.common.get_data import get_engine, read_f1k_table


def events_data():
    """
    get the frequency of annual breach data from Advisen

    Returns
    -------
    pd.DataFrame
        frequency of annual breach data from Advisen
    """
    event_cols = [
        "event_id",
        "event_start_date",
        "impact_type_availability",
        "impact_type_confidentiality",
        "impact_type_extortion",
        "impact_type_integrity",
    ]
    df_events = read_f1k_table()[event_cols]
    df_events.rename(
        {
            "event_id": "",
            "impact_type_availability": "availability",
            "impact_type_confidentiality": "confidentiality",
            "impact_type_extortion": "extortion",
            "impact_type_integrity": "integrity",
        },
        axis="columns",
        inplace=True,
    )
    # adjust columns
    df_events["year"] = df_events["event_start_date"].dt.year
    count_of_years = len(df_events["year"].unique())
    df_events["frequency"] = 1 / count_of_years / 1000
    df_events["source"] = "events"
    return df_events


def model_data():
    """
    get the event frequency data from the model

    Returns
    -------
    pd.DataFrame
        event frequency data from the model
    """
    query = """
        select
        run_id::text as entity,
        'model' as source,
        'model' as year,
        confidentiality,
        integrity,
        availability,
        extortion
    from
        model_events
    """
    df_model = pd.read_sql(query, con=get_engine())
    df_model["frequency"] = 1 / 10000 / 1000
    return df_model


def join_datasets():
    """
    join event data to model data with aggregated event types

    Returns
    -------
    pd.DataFrame
        joined events and model datasets
    """
    df_events = events_data().copy()
    df_model = model_data().copy()
    joined_data = pd.concat(
        [
            df_events[
                [
                    "availability",
                    "confidentiality",
                    "extortion",
                    "integrity",
                    "year",
                    "frequency",
                    "source",
                ]
            ],
            df_model[
                [
                    "availability",
                    "confidentiality",
                    "extortion",
                    "integrity",
                    "year",
                    "frequency",
                    "source",
                ]
            ],
        ]
    ).reset_index()
    return joined_data


def overall_frequency_plot_data():
    """
    generate overall frequency plot data

    Returns
    -------
    pd.DataFrame
        overall frequency plot data
    """
    df_comb = join_datasets().copy()
    df_comb["availability"] = df_comb["availability"].astype(bool)
    df_comb["confidentiality"] = df_comb["confidentiality"].astype(bool)
    df_comb["extortion"] = df_comb["extortion"].astype(bool)
    df_comb["integrity"] = df_comb["integrity"].astype(bool)
    df_plot = (
        df_comb.groupby(["confidentiality", "source"])
        .agg({"frequency": "sum"})
        .reset_index()
    )
    return df_plot
