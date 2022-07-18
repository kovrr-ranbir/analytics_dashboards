import pandas as pd

from analytics_dashboards.common.get_data import get_engine, read_f1k_table


def events_data():
    """
    get the event severity data from Advisen

    Returns
    -------
    pd.DataFrame
        event severity data
    """
    df_events = read_f1k_table()
    df_events.rename(
        {
            "total_cost_usd": "event_impact",
        },
        axis="columns",
        inplace=True,
    )
    df_events["event_impact"] = df_events["total_cost_millions_usd"] * 1e6
    df_events["source"] = "events"
    return df_events


def model_data():
    """
    get the event severity data from the model

    Returns
    -------
    pd.DataFrame
        event severity data from the model
    """
    query = """
    select
        model_events.run_id::text as entity,
        model_entities.revenue_band,
        model_events.confidentiality,
        model_events.targeted_event_type,
        gu_mean as event_impact,
        event_type as event_type,
        gu_bi_ratio * gu_mean as gu_bi,
        gu_contingent_bi_ratio * gu_mean as gu_cbi,
        gu_extortion_ratio * gu_mean as gu_extortion,
        gu_liability_ratio * gu_mean as gu_liability,
        gu_privacy_ratio * gu_mean as gu_privacy,
        gu_regulatory_ratio * gu_mean as gu_regulatory
    from
        model_events
    join
        model_entities
        on model_entities.run_id = model_events.run_id
    """
    df_model = pd.read_sql(query, con=get_engine())
    df_model["source"] = "model"
    return df_model


def aggregate_model_event_types():
    """
    aggregate model event types

    Returns
    -------
    pd.DataFrame
        model data with aggregated event types
    """
    df_model = model_data().copy()
    df_model["targeted_event_type"] = df_model["targeted_event_type"].fillna("systemic")
    df_model["targeted_event_type"] = df_model["targeted_event_type"].replace(
        "service_provider_data_breach", "data_breach"
    )
    df_model["targeted_event_type"] = df_model["targeted_event_type"].replace(
        "service_provider_interruption", "interruption"
    )
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
    df_model = aggregate_model_event_types().copy()
    common_cols = ["event_impact", "source"]
    joined_data = pd.concat(
        [
            df_events.loc[df_events["impact_type_confidentiality"] == True][
                common_cols
            ],
            df_model.loc[df_model["confidentiality"] == 1][common_cols],
        ],
        sort=False,
    ).reset_index()
    return joined_data


def overall_severity_plot_data():
    """
    generate overall severity plot data

    Returns
    -------
    pd.DataFrame
        overall severity plot data
    """
    minimum = 1_000_000
    limit = 100_000_000
    bins = 30
    plot_data = join_datasets().copy()
    plot_data = plot_data.loc[
        (plot_data["event_impact"] <= limit) & (plot_data["event_impact"] > minimum)
    ]
    return plot_data


def cost_components():
    """
    map out cost components in the event and model datasets

    Returns
    -------
    tuple
        tuple of events and model data with cost components mapped
    """
    df_events_TP = events_data().copy()
    df_model_TP = aggregate_model_event_types().copy()
    # Event cost mapping
    df_events_TP["gu_liability"] = (
        df_events_TP["liability_third_party_cost_millions_usd"] * 1e6
        + df_events_TP["injury_cost_millions_usd"] * 1e6
        + df_events_TP["settlement_amount_paid_millions_usd"] * 1e6
        + df_events_TP["liability_first_party_cost_millions_usd"] * 1e6
    )
    df_events_TP["gu_bi"] = (
        df_events_TP["lost_income_cost_millions_usd"] * 1e6
        + df_events_TP["property_cost_millions_usd"] * 1e6
    )
    df_events_TP["gu_privacy"] = (
        df_events_TP["other_costs_millions_usd"] * 1e6
        + df_events_TP["response_cost_millions_usd"] * 1e6
    )
    df_events_TP["gu_regulatory"] = df_events_TP["regulatory_costs_millions_usd"] * 1e6
    df_events_TP["gu_extortion"] = df_events_TP["extortion_paid_millions_usd"] * 1e6
    # Model cost Mapping
    df_model_TP["gu_bi"] = df_model_TP["gu_bi"] + df_model_TP["gu_cbi"]
    return df_events_TP, df_model_TP


def join_cost_component_datasets():
    """
    join model and event cost component datasets

    Returns
    -------
    pd.DataFrame
        model and events cost components dataset
    """
    df_events_TP, df_model_TP = cost_components()
    df_costs = pd.concat(
        [
            df_model_TP[
                [
                    "gu_liability",
                    "gu_regulatory",
                    "gu_bi",
                    "gu_extortion",
                    "gu_privacy",
                    "source",
                ]
            ].reset_index(),
            df_events_TP[
                [
                    "gu_liability",
                    "gu_regulatory",
                    "gu_bi",
                    "gu_extortion",
                    "gu_privacy",
                    "source",
                ]
            ].reset_index(),
        ],
        sort=False,
    ).reset_index()
    return df_costs


def liability_costs():
    """
    generate liability costs plot data

    Returns
    -------
    pd.DataFrame
        liability costs dataset
    """
    minimum = 1_000_000
    limit = 100_000_000
    liability_costs_data = join_cost_component_datasets().copy()
    param = "gu_liability"
    plot_data = liability_costs_data.loc[
        (liability_costs_data[param] <= limit) & (liability_costs_data[param] > minimum)
    ]
    return plot_data


def regulatory_costs():
    """
    generate regulatory costs plot data

    Returns
    -------
    pd.DataFrame
        regulatory costs dataset
    """
    minimum = 100_000
    limit = 100_000_000
    regulatory_costs_data = join_cost_component_datasets().copy()
    param = "gu_regulatory"
    plot_data = regulatory_costs_data.loc[
        (regulatory_costs_data[param] <= limit)
        & (regulatory_costs_data[param] > minimum)
    ]
    return plot_data


def privacy_costs():
    """
    generate privacy costs plot data

    Returns
    -------
    pd.DataFrame
        privacy costs dataset
    """
    minimum = 100_000
    limit = 100_000_000
    privacy_costs_data = join_cost_component_datasets().copy()
    param = "gu_privacy"
    plot_data = privacy_costs_data.loc[
        (privacy_costs_data[param] <= limit) & (privacy_costs_data[param] > minimum)
    ]
    return plot_data


def bi_costs():
    """
    generate business interruption costs plot data

    Returns
    -------
    pd.DataFrame
        business interruption costs dataset
    """
    minimum = 100_000
    limit = 100_000_000
    bi_costs_data = join_cost_component_datasets().copy()
    param = "gu_bi"
    plot_data = bi_costs_data.loc[
        (bi_costs_data[param] <= limit) & (bi_costs_data[param] > minimum)
    ]
    return plot_data


def extortion_costs():
    """
    generate extortion costs plot data

    Returns
    -------
    pd.DataFrame
        extortion costs dataset
    """
    minimum = 100_000
    limit = 100_000_000
    extortion_costs_data = join_cost_component_datasets().copy()
    param = "gu_extortion"
    plot_data = extortion_costs_data.loc[
        (extortion_costs_data[param] <= limit) & (extortion_costs_data[param] > minimum)
    ]
    return plot_data


def model_cost_split():
    """
    split model data by cost components

    Returns
    -------
    pd.DataFrame
        model data split by cost components
    """
    df_model_cost = aggregate_model_event_types().copy()
    df_model_cost = df_model_cost.reset_index()[
        [
            "index",
            "gu_bi",
            "gu_cbi",
            "gu_extortion",
            "gu_liability",
            "gu_privacy",
            "gu_regulatory",
            "event_impact",
        ]
    ]
    df_model_cost = df_model_cost.melt(
        id_vars="index", var_name="cost_component", value_name="value"
    )
    return df_model_cost


def model_cost_plot_data():
    """
    generate plot data for model costs split

    Returns
    -------
    pd.DataFrame
        model costs split plot data
    """
    minimum = 1_000_000
    limit = 100_000_000
    plot_data = model_cost_split().copy()
    plot_data = plot_data.loc[
        (plot_data["value"] <= limit) & (plot_data["value"] > minimum)
    ]
    return plot_data
