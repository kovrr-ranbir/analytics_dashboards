import pandas as pd

from analytics_dashboards.common.get_data import get_engine, read_f1k_table


def model_version():
    """
    get the model version number

    Returns
    -------
    str
        model version number
    """
    query = """
    select 
    value 
    from 
    model_metadata 
    where item = 'model_version'
    """
    model_version = pd.read_sql(query, con=get_engine())
    model_version = model_version.iloc[0][0]
    return model_version


def events_data():
    """
    get the frequency of annual events from Advisen

    Returns
    -------
    pd.DataFrame
        frequency of annual events from Advisen
    """

    df_events = read_f1k_table()
    df_events["year"] = df_events["event_start_date"].dt.year
    df_events = (
        (df_events.groupby("year").agg({"event_id": "count"}) / 1000)
        .rename({"event_id": "frequency"}, axis="columns")
        .reset_index()
    )
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
        count(*)::float/10000 as frequency,
        'Model_events' as source
    from
        model_events
    group by run_id::text
    """
    df_model = pd.read_sql(query, con=get_engine())
    return df_model


def box_plot_data():
    """
    join event data to model data with aggregated event types

    Returns
    -------
    pd.DataFrame
        joined events and model datasets
    """
    df_events = events_data().copy()
    df_model = model_data().copy()
    df_plot = pd.concat(
        [
            df_events[["year", "frequency", "source"]],
            df_model[["entity", "frequency", "source"]],
        ]
    )
    return df_plot


def model_data_by_cost_component():
    """
    get the event frequency by cost component from the model

    Returns
    -------
    pd.DataFrame
        event frequency data from the model by cost component
    """
    query = """
        select
        confidentiality,
        availability,
        integrity,
        extortion
        event_type,
        targeted_event_type,
        1 as count
    from
        model_events
    """
    df_model = pd.read_sql(query, con=get_engine())
    return df_model


def event_data_by_cost_component():
    """
    get the event frequency by cost component from Advisen

    Returns
    -------
    pd.DataFrame
        event frequency data from Advisen by cost component
    """
    query = """
    select
        impact_type_confidentiality,
        impact_type_availability,
        impact_type_integrity,
        event_type,
        1 as count
    from
        data_sources_events
    """
    df_events = pd.read_sql(query, con=get_engine())
    return df_events


def map_event_types():
    """
    map event types to event data by cost component

    Returns
    -------
    pd.DataFrame
        event frequency by cost component with mapped event types
    """
    event_map = {
        "['Data Breach']": "data breach",
        "['Infrastructure Attack']": "infrastructure attack",
        "['Financial Theft']": "financial",
        "['Ransomware']": "ransomware",
        "['Interruption']": "interruption",
        "['Ransomware' 'Data Breach']": "ransomware",
        "['Data Breach' 'Ransomware']": "ransomware",
        "['Data Breach' 'Financial Theft']": "data breach",
        "['Data Breach' 'Interruption']": "data breach",
        "['Ransomware' 'Interruption']": "ransomware",
        "['Infrastructure Attack' 'Data Breach']": "data breach",
        "['Data Breach' 'Ransomware' 'Interruption']": "ransomware",
        "['Data Breach' 'Interruption' 'Ransomware']": "ransomware",
        None: "unknown",
    }
    df_events = event_data_by_cost_component().copy()
    df_events["impact_type_confidentiality"] = df_events[
        "impact_type_confidentiality"
    ].replace(True, "confidentiality impacted")
    df_events["impact_type_confidentiality"] = df_events[
        "impact_type_confidentiality"
    ].replace(False, "no confidentiality impact")
    df_events["event_type"] = df_events["event_type"].replace(event_map)
    return df_events


def model_labels():
    """
    generate labels for model event types

    Returns
    -------
    pd.DataFrame
        model data with labelled event types
    """
    df_model_et = model_data_by_cost_component().copy()
    df_model_et["confidentiality"] = df_model_et["confidentiality"].replace(
        1, "confidentiality impacted"
    )
    df_model_et["confidentiality"] = df_model_et["confidentiality"].replace(
        0, "no confidential impact"
    )
    df_model_et["event_type"] = df_model_et["event_type"].replace(
        "provider", "systemic"
    )
    df_model_et["event_type"] = df_model_et["event_type"].replace("tech", "systemic")
    df_model_et["targeted_event_type"] = df_model_et["targeted_event_type"].fillna(
        "systemic"
    )
    df_model_et["targeted_event_type"] = df_model_et["targeted_event_type"].replace(
        "service_provider_data_breach", "data_breach"
    )
    df_model_et["targeted_event_type"] = df_model_et["targeted_event_type"].replace(
        "service_provider_interruption", "interruption"
    )
    return df_model_et


def model_cia():
    """
    classifies model data into confidenitality, availability and integrity

    Returns
    -------
    pd.DataFrame
        classified model data into cia
    """
    df_model_cia = model_data_by_cost_component().copy()
    df_model_cia["confidentiality"] = df_model_cia["confidentiality"].replace(
        1, "confidentiality"
    )
    df_model_cia["confidentiality"] = df_model_cia["confidentiality"].replace(
        0, "no confidentiality impact"
    )
    df_model_cia["availability"] = df_model_cia["availability"].replace(
        1, "availability"
    )
    df_model_cia["availability"] = df_model_cia["availability"].replace(
        0, "no availability impact"
    )
    df_model_cia["integrity"] = df_model_cia["integrity"].replace(1, "integrity")
    df_model_cia["integrity"] = df_model_cia["integrity"].replace(
        0, "no integrity impact"
    )
    return df_model_cia


def events_cia():
    """
     classifies event data into confidenitality, availability and integrity

    Returns
    -------
    pd.DataFrame
        classified event data into cia
    """
    df_events_cia = map_event_types().copy()
    df_events_cia["impact_type_confidentiality"] = df_events_cia[
        "impact_type_confidentiality"
    ].replace(1, "confidentiality")
    df_events_cia["impact_type_confidentiality"] = df_events_cia[
        "impact_type_confidentiality"
    ].replace(0, "none")
    df_events_cia["impact_type_confidentiality"] = df_events_cia[
        "impact_type_confidentiality"
    ].fillna("c - unknown")
    df_events_cia["impact_type_availability"] = df_events_cia[
        "impact_type_availability"
    ].replace(1, "availability")
    df_events_cia["impact_type_availability"] = df_events_cia[
        "impact_type_availability"
    ].replace(0, "no availability impact")
    df_events_cia["impact_type_availability"] = df_events_cia[
        "impact_type_availability"
    ].fillna("a - unknown")
    df_events_cia["impact_type_integrity"] = df_events_cia[
        "impact_type_integrity"
    ].replace(1, "integrity")
    df_events_cia["impact_type_integrity"] = df_events_cia[
        "impact_type_integrity"
    ].replace(0, "no integrity impact")
    df_events_cia["impact_type_integrity"] = df_events_cia[
        "impact_type_integrity"
    ].fillna("i - unknown")
    return df_events_cia


def build_sankey(index_cols, target_col, df):
    """
    generate data to be used for sankey plots

    Parameters
    ----------
    index_cols : list
        fields to use as an index
    target_col : str
        field to use as the target
    df : pd.DataFrame
        data to use to build the sankey plot

    Returns
    -------
    tuple
        tuple of processed dataframe and dictionary of labels
    """
    input_df = df.copy()
    # build target/source relationships
    df_links = pd.DataFrame()
    for pos in range(0, len(index_cols) - 1):
        temp_df = (
            input_df.groupby([index_cols[pos], index_cols[pos + 1]])
            .agg({target_col: "sum"})
            .reset_index()
        )
        temp_df.columns = ["source", "target", "value"]
        df_links = pd.concat([df_links, temp_df])
    df_links["value"] = df_links["value"] / df_links["value"].sum()

    # label encoding:
    label_list = list(df_links["source"])
    label_list.extend(list(df_links["target"]))
    label_list = list(dict.fromkeys(label_list))
    label_dict = {}
    i = 0
    for item in label_list:
        label_dict[item] = i
        i += 1
    df_links["source"] = df_links["source"].replace(label_dict)
    df_links["target"] = df_links["target"].replace(label_dict)
    return df_links, label_dict


def confidentiality_model_sankey_plot_data(
    index_cols=["confidentiality", "targeted_event_type"],
    target_col="count",
    df=model_labels(),
):
    """
    generate data to use for the model confidentiality sankey plot

    Parameters
    ----------
    index_cols : list, optional
       fields to use as an index  , by default ['confidentiality', 'targeted_event_type']
    target_col : str, optional
       field to use as the target , by default 'count'
    df : pd.DataFrame, optional
        dataframe with model labels, by default model_labels()

    Returns
    -------
    tuple
        tuple of processed dataframe and dictionary of labels
    """
    df_links, label_dict = build_sankey(index_cols, target_col, df)
    return df_links, label_dict


def confidentiality_events_sankey_plot_data(
    index_cols=["impact_type_confidentiality", "event_type"],
    target_col="count",
    df=map_event_types(),
):
    """
    generate data to use for the event confidentiality sankey plot

    Parameters
    ----------
    index_cols : list, optional
       fields to use as an index, by default ['impact_type_confidentiality','event_type']
    target_col : str, optional
       field to use as the target, by default 'count'
    df : pd.DataFrame, optional
        dataframe with model labels, by default map_event_types()

    Returns
    -------
    tuple
        tuple of processed dataframe and dictionary of labels
    """
    df_links, label_dict = build_sankey(index_cols, target_col, df)
    return df_links, label_dict


def confidentiality_model_cia_sankey_plot_data(
    index_cols=["confidentiality", "availability", "integrity"],
    target_col="count",
    df=model_cia(),
):
    """
      generate data to use for the model cia confidentiality sankey plot

     Parameters
     ----------
     index_cols : list, optional
         fields to use as an index, by default ["confidentiality", "availability", "integrity"]
     target_col : str, optional
         field to use as the target, by default "count"
     df : pd.DataFrame, optional
         dataframe with model labels, by default model_cia()

     Returns
     -------
    tuple
         tuple of processed dataframe and dictionary of labels
    """
    df_links, label_dict = build_sankey(index_cols, target_col, df)
    return df_links, label_dict


def confidentiality_events_cia_sankey_plot_data(
    index_cols=[
        "impact_type_confidentiality",
        "impact_type_availability",
        "impact_type_integrity",
    ],
    target_col="count",
    df=events_cia(),
):
    """
      generate data to use for the events cia confidentiality sankey plot

     Parameters
     ----------
     index_cols : list, optional
         fields to use as an index, by default ['impact_type_confidentiality','impact_type_availability', 'impact_type_integrity']
     target_col : str, optional
         field to use as the target, by default "count"
     df : pd.DataFrame, optional
         dataframe with model labels, by default events_cia()

     Returns
     -------
    tuple
         tuple of processed dataframe and dictionary of labels
    """
    df_links, label_dict = build_sankey(index_cols, target_col, df)
    return df_links, label_dict


def model_cia_barplot_data():
    """
    generate data to use for the model cia bar plot

    Returns
    -------
    pd.DataFrame
        dataframe with normalized model cia data
    """
    df_model = model_data_by_cost_component().copy()
    cia_bar_model = df_model[
        ["confidentiality", "availability", "integrity"]
    ].sum() / len(df_model)
    return cia_bar_model
