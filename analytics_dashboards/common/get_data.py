# builds the connection to azure:

import json
import os

import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
import seaborn as sns
import sqlalchemy as sa
from sqlalchemy import create_engine
from sshtunnel import SSHTunnelForwarder

# setup connection
secrets_path = os.path.join(
    os.path.dirname(__file__), "../../../", "secrets", "analytics_staging_db.json"
)
with open(secrets_path) as f:
    secret_analytics_staging_db = json.load(f)

# load config
config_path = os.path.join(
    os.path.dirname(__file__), "../../", "configuration", "config.json"
)
with open(config_path) as config_file:
    config = json.load(config_file)

# ssh private-key
ssh_private_key_path = os.path.join(
    os.path.dirname(__file__), "../../../", "secrets", "id_rsa"
)


def select_connection(db_name, local_connection=False):
    """
    connect to the staging database

    Parameters
    ----------
    local_connection : bool, optional
        specifies whether the connection is made with an Azure compute instance, by default False

    Returns
    -------
    sqlalchemy.engine.url.URL
        sqlalchemy connection object
    """
    if local_connection:
        try:
            tunnel = SSHTunnelForwarder(
                (
                    secret_analytics_staging_db["ssh-server"],
                    secret_analytics_staging_db["ssh-port"],
                ),
                ssh_private_key=ssh_private_key_path,
                ssh_username=secret_analytics_staging_db["ssh-username"],
                remote_bind_address=(
                    secret_analytics_staging_db["db-host"],
                    secret_analytics_staging_db["db-port"],
                ),
            )
            tunnel.start()
            print("server connected")
            conn = sa.engine.URL.create(
                drivername=secret_analytics_staging_db["db-driver"],
                username=secret_analytics_staging_db["db-username"],
                password=secret_analytics_staging_db["db-password"],
                host="localhost",
                port=tunnel.local_bind_port,
                database=db_name,
            )
            return conn
        except Exception as e:
            print(e)

    else:
        conn = sa.engine.URL.create(
            drivername=secret_analytics_staging_db["db-driver"],
            username=secret_analytics_staging_db["db-username"],
            password=secret_analytics_staging_db["db-password"],
            host=secret_analytics_staging_db["db-host"],
            port=secret_analytics_staging_db["db-port"],
            database=db_name,
        )
        return conn


def read_f1k_table(date_limits=True):
    """get all events related to the fortune 1000 proxy-list entities"""
    engine = create_engine(
        select_connection(
            db_name="postgres", local_connection=config["local_connection"]
        )
    )
    query = """
    select 
        *,
        date_part('year', event_start_date)::int as year_start
    from 
        data_sources_events
    join
        data_sources_entities
        on data_sources_events.company_instance_id = data_sources_entities.company_instance_id
    where 
        company_revenue_millions_usd >= 2000
        and company_country_code = 'US'
        and left(company_sic::text,2)::int < 90
        and date_part('year', event_start_date) >= 2010
        and date_part('year', event_start_date) <= 2020
    """

    if date_limits == False:
        query = """
        select 
            *,
            date_part('year', event_start_date)::int as year_start
        from 
            data_sources_events
        join
            data_sources_entities
            on data_sources_events.company_instance_id = data_sources_entities.company_instance_id
        where 
            company_revenue_millions_usd >= 2000
            and company_country_code = 'US'
            and left(company_sic::text,2)::int < 90
        --    and date_part('year', event_start_date) >= 2010
        --    and date_part('year', event_start_date) <= 2020
        """

    df = pd.read_sql_query(query, engine)

    return df


def read_f1k_entities():
    """get the entities table for the fortune 1000 proxy-list, no events"""
    engine = engine = create_engine(
        select_connection(
            db_name="postgres", local_connection=config["local_connection"]
        )
    )
    query = """
    select 
        *
    from 
        data_sources_entities
    where 
        company_revenue_millions_usd >= 2000
        and company_country_code = 'US'
        and left(company_sic::text,2)::int < 90
--        and date_part('year', event_start_date) >= 2010
--        and date_part('year', event_start_date) <= 2020
    """
    return pd.read_sql_query(query, engine)


def read_vcdb_events():
    """get availability duration data from vcdb"""
    engine = create_engine(
        select_connection(
            db_name="data_sources", local_connection=config["local_connection"]
        )
    )
    query = """
    select
    incident_id,
    victim_victim_id,
    victim_country,
    victim_government,
    victim_industry,
    victim_state,
    action_misuse_variety,
    attribute_availability_variety,
    attribute_confidentiality_data,
    attribute_confidentiality_data_disclosure,
    timeline_incident_year,
    timeline_containment_unit,
    timeline_containment_value,
    attribute_availability_duration_value,
    attribute_availability_duration_unit,
    attribute_availability_notes,
    summary
    from vcdb
    where attribute_availability_duration_value is not null;
    """
    return pd.read_sql_query(query, engine)


def get_engine():
    return create_engine(
        select_connection(
            db_name="postgres", local_connection=config["local_connection"]
        )
    )


def model_version():
    """
    returns the model version number
    """
    query = """
    select value from model_metadata where item = 'model_version' 
    """
    df = pd.read_sql(query, con=get_engine())
    model_version = df.iloc[0][0]
    return model_version


def set_colours():
    # Create an array with the colors you want to use
    return [
        "#5551F7",
        "#E0502B",
        "#86A0FF",
        "#FC8639",
        "#6E6BFF",
        "#157A55",
        "#FF9900",
        "#FF2323",
    ]
    # Set your custom color palette
    # sns.set_palette(sns.color_palette(colors))
