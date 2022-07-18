import os

import pandas as pd

from analytics_dashboards.common.get_data import get_engine, read_f1k_table


def event_exposure_data():
    """
    returns event exposure data from Advisen

    Returns
    -------
    pd.DataFrame
        event exposure data from Advisen
    """
    df_events_raw = read_f1k_table().sort_values("event_start_date", ascending=True)
    df_events_filtered = (
        df_events_raw.groupby("company_name")
        .agg(
            {
                "company_revenue_millions_usd": "last",
                "company_sic": "last",
                "company_state": "last",
            }
        )
        .reset_index()
    )
    df_events = df_events_filtered[
        ["company_name", "company_revenue_millions_usd", "company_sic", "company_state"]
    ]
    df_events = df_events.rename(
        {
            "company_name": "company_name",
            "company_revenue_millions_usd": "revenue",
            "company_sic": "sic",
            "company_state": "geography",
        },
        axis="columns",
    )
    df_events["sic"] = df_events["sic"].apply(lambda x: str(int(x))[:2], 2).astype(int)
    df_events["source"] = "data"
    return df_events


def model_exposure_data():
    """
    returns the event exposure data from the model

    Returns
    -------
    pd.DataFrame
        event exposure data from model
    """
    query = """
    select
    entity_name as company_name,
    entity_revenue/1e6 as revenue,
    sic_code as sic,
    countries as geography
    from
    model_entities
    """
    df_model = pd.read_sql(query, con=get_engine())
    df_model["geography"] = df_model["geography"].str.replace("US-", "")
    df_model["source"] = "model"
    return df_model


def join_datasets():
    """
    joined event and model data

    Returns
    -------
    pd.DataFrame
        returns the joined event and model dataset
    """
    df_model = model_exposure_data()
    df_events = event_exposure_data()
    joined_data = pd.concat([df_model, df_events]).reset_index()
    return joined_data


def sic_data():
    """
    creates event exposure data by sic code

    Returns
    -------
    pd.DataFrame
        event exposure data by sic code
    """
    data_sic = (
        join_datasets()
        .groupby(["source", "sic"])["company_name"]
        .agg("count")
        .reset_index()
    )
    data_sic["sic"] = data_sic["sic"].astype(int)
    data_sic.rename({"company_name": "entitiy_count"}, axis="columns", inplace=True)
    sic_map = pd.read_csv(
        os.path.join(os.path.dirname(__file__), "..", "resources", "SIC_code_map.csv")
    )
    data_sic = data_sic.merge(sic_map, how="left", left_on="sic", right_on="SIC Code")
    data_sic["source_total"] = 0
    data_sic.loc[data_sic["source"] == "data", "source_total"] = data_sic.loc[
        data_sic["source"] == "data", "entitiy_count"
    ].sum()
    data_sic.loc[data_sic["source"] == "model", "source_total"] = data_sic.loc[
        data_sic["source"] == "model", "entitiy_count"
    ].sum()
    data_sic["entity_count_normalised"] = (
        data_sic["entitiy_count"] / data_sic["source_total"]
    )
    data_sic[["source", "entity_count_normalised"]].groupby("source").agg("sum")
    return data_sic


def division_sic_data():
    """
    creates event exposure data by sic code division grouping

    Returns
    -------
    pd.DataFrame
        event exposure data by sic code division
    """
    data_sic_div = (
        sic_data()
        .groupby(["source", "Division Desc."])["entity_count_normalised"]
        .agg("sum")
        .reset_index()
    )
    data_sic_div["Division Desc."].replace(
        "Finance, Insurance, And Real Estate", "Finance & Property", inplace=True
    )
    return data_sic_div


def geographic_data():
    """
    creates event exposure data grouped by geography

    Returns
    -------
    pd.DataFrame
        event exposure data grouped by geography
    """
    data_geo = (
        join_datasets()
        .groupby(["source", "geography"])["company_name"]
        .agg("count")
        .reset_index()
    )
    data_geo.rename({"company_name": "entitiy_count"}, axis="columns", inplace=True)
    data_geo["source_total"] = 0
    data_geo.loc[data_geo["source"] == "data", "source_total"] = data_geo.loc[
        data_geo["source"] == "data", "entitiy_count"
    ].sum()
    data_geo.loc[data_geo["source"] == "model", "source_total"] = data_geo.loc[
        data_geo["source"] == "model", "entitiy_count"
    ].sum()
    data_geo["entity_count_normalised"] = (
        data_geo["entitiy_count"] / data_geo["source_total"]
    )
    data_geo[["source", "entity_count_normalised"]].groupby("source").agg("sum")
    data_geo.sort_values(
        ["source", "entity_count_normalised"], ascending=False, inplace=True
    )
    return data_geo
