import pandas as pd

from analytics_dashboards.common.get_data import get_engine, read_f1k_table


def events_data():
    """
    get the count of events by year from Advisen

    Returns
    -------
    pd.DataFrame
        count of events by year
    """
    df_events = read_f1k_table()
    df_events["year"] = df_events["event_start_date"].dt.year
    df_events_byyear = (
        df_events.groupby(["year", "company_name"])
        .agg({"event_id": "count"})
        .reset_index()
    )
    df_events_byyear.rename({"event_id": "no_events"}, axis="columns", inplace=True)
    df_events_byyear["source"] = "events"
    return df_events_byyear


def model_data():
    """
    get the count of events by year from the model data

    Returns
    -------
    pd.DataFrame
        count of events by year
    """
    query = """
    select
    year_x as year,
    run_id::text as company_name,
    count(*)::float as no_events,
    'model' as source
    from 
    model_events
    group by run_id::text, year_x
    """
    df_model_byyear = pd.read_sql(query, con=get_engine())
    return df_model_byyear


def join_datasets():
    """
    joined event and model data

    Returns
    -------
    pd.DataFrame
        returns the joined event and model dataset
    """
    df_model = model_data()
    df_events = events_data()
    joined_data = pd.concat([df_model, df_events]).reset_index()
    joined_data["no_events"] = joined_data["no_events"].astype(int)
    return joined_data


def events_per_year_plot_data():
    """
    generate count fo events plot data

    Returns
    -------
    pd.DataFrame
        events per year plot data
    """
    df_by_year_summary = (
        join_datasets()
        .groupby(["source", "no_events"])
        .agg({"company_name": "count"})
        .reset_index()
    )
    df_by_year_summary = df_by_year_summary.pivot_table(
        index=["no_events"], values="company_name", columns="source"
    )
    df_by_year_summary = (
        (df_by_year_summary / df_by_year_summary.sum()).fillna(0).reset_index()
    )
    df_by_year_summary_melt = (
        df_by_year_summary.melt(id_vars="no_events")
        .set_index("no_events")
        .reset_index()
    )
    return df_by_year_summary_melt
