import numpy as np
import pandas as pd

from analytics_dashboards.common.get_data import (get_engine, read_f1k_table,
                                                  read_vcdb_events)


def model_duration_data():
    """
    returns the event duration from the model data
    """
    query = """
    select
    event_duration/(60*24) as duration,
    event_type as event_type
    from
    model_events
    """
    df = pd.read_sql(query, con=get_engine())
    df["source"] = "model"
    return df


def annotate_advisen_events():
    """
    annotate availability events - required as the classification for Advisen is not reliable

    Returns
    -------
    pd.DataFrame
        advisen data annotated with availability events
    """
    events = read_f1k_table()
    availability_event_ids = [
        36744,
        3439,
        28762,
        8299,
        44321,
        47261,
        27619,
        12681,
        54226,
        16055,
        15842,
        1398,
        21726,
        21729,
        15850,
        47715,
        3997,
        51734,
        16060,
        46479,
        16549,
        63570,
        13826,
        27620,
        16724,
        14498,
        33910,
        8211,
        7663,
        63814,
        48399,
        63898,
        23300,
    ]
    events["availability_duration_days_fixed"] = (
        events["event_end_date"] - events["event_start_date"]
    )
    events["availability_duration_days_fixed"] = events[
        "availability_duration_days_fixed"
    ].dt.days
    events.loc[
        events["event_id"].isin(availability_event_ids), "annotated_availability_events"
    ] = True
    events["source"] = "Advisen"
    advisen_events = events.loc[
        events["annotated_availability_events"] == True,
        ["availability_duration_days_fixed", "source"],
    ]
    return advisen_events


def convert_duration_to_days(df, unit_col, val_col, create_col):
    """
    convert event duration from given units to days

    Parameters
    ----------
    df : pd.Dataframe
        event duration dataset
    unit_col : str
        column name containing the unit of duration
    val_col : str
        column name containing the duration values
    create_col : str
        column name to create that will contain duration in days

    Returns
    -------
    pd.Dataframe
        dataframe containing event duration in days
    """
    df = df.copy()
    mapping = {
        "Days": 1,
        "Hours": 1 / 24,
        "Weeks": 7,
        "Minutes": 1 / (24 * 60),
        "Months": 30,
        "Years": 365,
        "Never": np.nan,
    }
    for units, values in mapping.items():
        df.loc[df[unit_col] == units, create_col] = df[val_col] * values
    return df


def annotate_vcdb_events():
    """
    get vcdb events from database and annotate availability duration

    Returns
    -------
    pd.DataFrame
        vcdb data annotated with availability events
    """
    vcdb_availability = read_vcdb_events()
    vcdb_availability_duration_fixed = convert_duration_to_days(
        df=vcdb_availability,
        unit_col="attribute_availability_duration_unit",
        val_col="attribute_availability_duration_value",
        create_col="availability_duration_days",
    )
    availability_event_ids = [
        "B040AF5E-E527-4193-A95D-01592F7B6FA1",
        "48789bf0-c8f4-11e9-9c16-3f32faecab86",
        "7C360C78-68FA-483D-B354-1A74E994F692",
        "9D6229B5-D8F4-4B6B-91FF-BBF8A9B7061D",
        "f82ee030-de12-11e9-92e6-b7a271e742aa",
        "2DE6C6B9-260C-4F42-B870-0D30BB87962A",
        "90778723-9EEB-42D3-A3C1-1E45360B926C",
        "C2440E4F-0A77-429D-9F19-3390D484C01E",
        "B1232E61-68AC-4B75-897E-20961AE49E6C",
        "5EC74643-0F36-4F2A-BEBD-98A0110162C2",
        "9C2C2351-AC07-4EFD-9964-2EB451C8654D",
        "10b98c60-15de-11ea-ba54-075d8b11bbd2",
        "AEF76670-CA82-469B-BE0A-B5EFA2381D0F",
        "66650162-DAB0-4C82-A32A-0DEC83735370",
        "1EF9CAD4-E31D-4506-83FD-7DC218929CB3",
        "E8D5A222-6138-4997-A50D-127DC7A4963D",
        "13188709-C0E4-43C8-881F-F00F330353E1",
        "B4883BFB-38A6-49FE-9766-5E53C020D1BA",
        "7710424D-5278-4C35-857F-732E8F0BF30F",
        "A4146679-35A9-45C5-A788-5E58E49C331E",
        "61BCDB75-75F7-4B2D-9BEB-53E126E667DD",
        "59CA466B-70E9-4F28-A6D8-4102BBE87197",
        "89B5C0FB-ED32-46D4-911C-8370B9EA4549",
        "48B10AED-D009-43FE-A6EC-43347E2CFE14",
        "9242C268-4AB8-4B18-B3B6-316FEED63778",
        "B64B656E-64EA-46DD-A7BC-8BAAB6595E8B",
        "98C6344E-7D1A-42B8-9F06-76D5643B15A6",
        "A695E842-89AD-4547-B767-076CF8EE6205",
        "F68EF982-454F-46D2-8545-85FE1E908CD7",
        "7866B7EE-A40E-463B-A4BD-B0DEC7A3DB94",
        "973575F9-F725-4B3F-B497-AE648836756E",
        "E5D427C6-B22B-47E8-8A3A-9FF7B99C07EC",
        "19E55526-D875-4A1A-9E6D-D454DD72508F",
        "15561EDD-EE92-4866-BDFC-6548969EC5BA",
        "18bfa490-07e5-11eb-9be5-67f56bbd8cb4",
        "12679140-8aae-11e8-874b-dd84fb61b260",
        "B356D3E7-A041-427F-9477-D25AF2F6E9C6",
        "E68565A5-6CB5-411B-A952-4EA430D4531C",
        "e4d7cfc0-761c-11e7-9d88-ab89f89c69db",
        "950bc800-de09-11e9-92e6-b7a271e742aa",
        "16618345-9E76-4D8E-9674-BF1E07C3C56F",
        "AE0AF7D6-B863-4605-A5D3-8087ACD7CA56",
        "78ee4940-6c82-11e7-8419-7d473c8dcba3",
        "F47262C8-EADB-4358-8282-A2A0AFAA7FE9",
        "fce9a620-85f6-11e8-ae9b-a1b647b0d464",
        "AE263091-A728-4455-88D5-4EBD1F8B480E",
        "6fbb5ec0-ce65-11e9-b4e5-4769cce343a0",
        "376F9AAD-7EA1-4B15-8BDC-EE457BFCF152",
        "AE327DA0-FFE9-4577-A894-F7C972E401A0",
        "FCA43278-6D87-4ABF-A918-3FA416F7551C",
        "553E7277-4C8B-4210-A3C0-8FE8FEEE5B65",
        "2DFBAD24-12AD-4256-85FC-D8EC2D8C71FB",
        "07c93380-1061-11ea-9257-5f79bcff5761",
        "2640A6B4-7F2D-43AF-93E6-DD9CBE19658F",
        "B81E60C1-5020-4DEA-9CF4-BABF44C3D1DF",
        "ef191cc0-9748-11e8-8342-0f8f10fcd812",
        "91A96A06-599D-4F10-8A43-909D1EC7D0F0",
        "5BC06D9F-21C1-4725-AE20-B27355CAEB72",
        "01468660-8ea4-11e8-8003-e3ff5269fee2",
        "E2CFF8F0-7478-497A-B0FE-07D97E8BBA9E",
        "504ff4e0-0fc6-11ea-997d-ff527b87f439",
        "DC18C7D0-E10A-4F1F-A242-D95572D5AF8C",
        "1F3704A1-771D-4E77-9B71-2C76DA743381",
        "4F2D1D4A-3FD6-46DC-B2B8-D296DEE0463D",
        "24CDDAD9-E931-44F8-8AF8-21AE8ACC426C",
        "268E0C6F-BA8B-43F4-B980-BB135AF9F98D",
        "38c01350-72f7-11e7-a859-bd14321ac1c3",
        "438607BB-8961-417E-B895-F68F9A396569",
        "BD71EF22-F735-4AE9-A9A4-3F39DABF6169",
        "9281EA6E-9A68-4074-8F31-9FE98076972E",
        "AF108731-F2F5-4B1E-B75E-0FC9FFFDE9D9",
        "E7A11807-6EE6-47AB-88BD-0C56682BABEC",
        "BB7833CC-EA6B-47C5-864B-62D775458F45",
        "BAF6581E-08D3-4AAB-9757-0C1CA854F4EF",
        "E6F5FEBB-A2A3-43B0-8283-AED0F67A9841",
        "CBC156D3-9481-4E80-8A80-B77FD64F1F5A",
        "cb5f7460-89a1-11e7-bf1d-81579668407a",
        "CACCA87D-8FC7-4722-81D7-C84BC9F45C88",
        "788C3B36-0C11-4398-AA3C-F8E70787DEF3",
        "4D630A26-B2FC-4A39-BD6E-7D7DA968B17C",
        "4AFFBDC8-59BE-46A8-B9B9-EA4337770B8D",
        "C108305E-4753-4279-A5AA-BB5F11C0F9B8",
        "f17d2ad0-c55a-11e7-8460-859aaa890f03",
        "0385F25B-DDEF-4838-AAA4-8539F6462DBE",
        "88409FC9-A75B-4F77-959F-04CDB4EE179B",
        "a2d88230-0c70-11ea-bb2f-edf349509116",
        "5B4505C3-A9DD-453D-92DC-EA1AA8AA2996",
        "8b0b0b80-c335-11e8-be54-d7fc81504f5e",
        "43702e60-2385-11eb-b77f-316b5c5dd5eb",
        "aca94ed0-8116-11e7-9cfb-2f8f443557c3",
        "2B6D006F-BE4B-4240-B011-226DB23247E5",
    ]
    vcdb_availability_duration_fixed.loc[
        vcdb_availability_duration_fixed["incident_id"].isin(availability_event_ids),
        "annotated_availability_events",
    ] = True
    vcdb_availability_duration_fixed["source"] = "VCDB"
    return vcdb_availability_duration_fixed


def event_duration_plot_data():
    """
    concatenates the model data to vcdb and advisen data

    Returns
    -------
    pd.DataFrame
        data to be used for plotting
    """
    advisen_events = annotate_advisen_events()
    vcdb_events = annotate_vcdb_events()
    advisen_events = advisen_events.rename(
        columns={"availability_duration_days_fixed": "availability_duration_days"}
    )
    vcdb_events = vcdb_events.loc[
        (vcdb_events["annotated_availability_events"] == True)
        & (
            vcdb_events["timeline_incident_year"].between(
                left=2010, right=2020, inclusive="both"
            )
        ),
        ["availability_duration_days", "source"],
    ]
    events_data = pd.concat([advisen_events, vcdb_events], ignore_index=True).rename(
        columns={"availability_duration_days": "duration"}
    )
    model_data = model_duration_data()[["duration", "source"]]
    plot_data = pd.concat([model_data, events_data], ignore_index=True)
    return plot_data
