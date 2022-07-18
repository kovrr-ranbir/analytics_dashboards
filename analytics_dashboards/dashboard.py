import matplotlib as mpl
import panel as pn
import plotly.graph_objects as go
import seaborn as sns
from matplotlib.figure import Figure

from analytics_dashboards.common.get_data import set_colours
from analytics_dashboards.event_duration import event_duration_plot_data
from analytics_dashboards.event_severity import (bi_costs, extortion_costs,
                                                 liability_costs,
                                                 model_cost_plot_data,
                                                 overall_severity_plot_data,
                                                 privacy_costs,
                                                 regulatory_costs)
from analytics_dashboards.events_annual_frequency import (
    box_plot_data, confidentiality_events_cia_sankey_plot_data,
    confidentiality_events_sankey_plot_data,
    confidentiality_model_cia_sankey_plot_data,
    confidentiality_model_sankey_plot_data, model_cia_barplot_data,
    model_version)
from analytics_dashboards.events_per_year import events_per_year_plot_data
from analytics_dashboards.exposure_comparison import (division_sic_data,
                                                      geographic_data,
                                                      join_datasets, sic_data)
from analytics_dashboards.frequency_annual_breach import \
    overall_frequency_plot_data


def cache_plot_data(df, data_name):
    """
    cache data for plotting

    Parameters
    ----------
    df : pd.DataFrame
        data to cache
    data_name : str
        identifier for cached data
    """
    if data_name not in pn.state.cache.keys():
        pn.state.cache[data_name] = df.copy()
        return df
    else:
        df_copy = pn.state.cache[data_name]
    return df_copy


def event_duration_box_plot(plot_data):
    """
    box plots comparing event duration in days between model and events data

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel boxplot pane
    """

    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.boxplot(
        data=plot_data,
        x="duration",
        y="source",
        orient="h",
        ax=ax,
    )
    ax.set_xlabel("duration(days)")
    mpl_boxplot_pane = pn.pane.Matplotlib(fig)
    return mpl_boxplot_pane


def event_duration_ecdf_plot(plot_data):
    """
    ecdf plots comparing event duration in days between model and events data

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel ecdf pane
    """
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.ecdfplot(
        data=plot_data,
        x="duration",
        hue="source",
        stat="proportion",
        ax=ax,
    )
    ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
    ax.set_xlabel("duration(days)")
    ax.set_ylabel("probability")
    mpl_ecdf_pane = pn.pane.Matplotlib(fig)
    return mpl_ecdf_pane


def event_duration_hist_plot(plot_data):
    """
    histogram plots comparing event duration in days between model and events data

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel histplot pane
    """
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.histplot(
        data=plot_data,
        x="duration",
        hue="source",
        stat="probability",
        binwidth=5,
        alpha=0.2,
        common_norm=False,
        ax=ax,
    )
    ax.axvspan(xmin=15, xmax=23, alpha=0.2, color="grey", linestyle="dashed", lw=1)
    ax.annotate(
        "avg duration of downtime after a ransomware attack(Coveware): 15-23 days",
        xy=(23, 0.4),
        xytext=(30, 0.4),
        xycoords="data",
        bbox=dict(boxstyle="round", fc="none", ec="gray"),
        arrowprops=dict(arrowstyle="->"),
        wrap=True,
    )
    ax.set_xlabel("duration(days)")
    ax.xaxis.set_major_formatter(mpl.ticker.StrMethodFormatter("{x:,.0f}"))
    mpl_histplot_pane = pn.pane.Matplotlib(fig)
    return mpl_histplot_pane


def event_exposure_revenue(plot_data):
    """
    histogram plot comparing revenue of companies in model and events data

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel histplot pane
    """
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.histplot(
        data=plot_data,
        x="revenue",
        hue="source",
        common_norm=False,
        stat="probability",
        ax=ax,
    )
    ax.set_xlim(-1, 100000)
    mpl_histplot_pane = pn.pane.Matplotlib(fig)
    return mpl_histplot_pane


def event_exposure_sic_count(plot_data):
    """
    bar plot comparing count of entities by sic name in model and events data

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel barplot pane
    """
    fig = Figure(figsize=(12, 7))
    ax = fig.subplots(1, 1)
    sns.barplot(
        data=plot_data,
        x="Code Desc. Short",
        y="entity_count_normalised",
        hue="source",
        ax=ax,
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=60)
    mpl_barplot_pane = pn.pane.Matplotlib(fig)
    return mpl_barplot_pane


def event_exposure_sic_division_count(plot_data):
    """
    bar plot comparing count of entities by sic division in model and events data

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel barplot pane
    """
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.barplot(
        data=plot_data,
        x="Division Desc.",
        y="entity_count_normalised",
        hue="source",
        ax=ax,
    )
    ax.set_xticklabels(ax.get_xticklabels(), rotation=60)
    mpl_barplot_pane = pn.pane.Matplotlib(fig)
    return mpl_barplot_pane


def event_exposure_geography(plot_data):
    """
    bar plot comparing count of entities by geography in model and events data

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel barplot pane
    """
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.barplot(
        data=plot_data,
        x="geography",
        y="entity_count_normalised",
        hue="source",
        ax=ax,
    )
    ax.set_xlim(-0.5, 10.5)
    mpl_barplot_pane = pn.pane.Matplotlib(fig)
    return mpl_barplot_pane


def events_per_year_bar_plot(plot_data):
    """
    bar plot showing the number of events per year

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel barplot pane
    """
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.barplot(data=plot_data, x="no_events", y="value", hue="source", ax=ax)
    ax.set_xlim(-1, 10)
    mpl_barplot_pane = pn.pane.Matplotlib(fig)
    return mpl_barplot_pane


def event_severity_overall_hist_plot(plot_data):
    """
    histplot showing the overall event severity

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel histplot pane
    """
    limit = 100_000_000
    bins = 30
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.histplot(
        data=plot_data,
        x="event_impact",
        hue="source",
        stat="probability",
        binwidth=limit / bins,
        alpha=0.5,
        common_norm=False,
        ax=ax,
    )
    ax.set_ylim(0, 0.4)
    mpl_histplot_pane = pn.pane.Matplotlib(fig)
    return mpl_histplot_pane


def event_severity_annotated_overall_hist_plot(plot_data):
    """
    annotated histplot showing the overall event severity

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel histplot pane
    """
    limit = 100_000_000
    bins = 30
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.histplot(
        data=plot_data,
        x="event_impact",
        hue="source",
        stat="probability",
        binwidth=limit / bins,
        alpha=0.5,
        common_norm=False,
        ax=ax,
    )
    ax.set_ylim(0, 0.4)
    # IBM Cost of data breach report 2021
    ax.axvline(3.6e6, color="purple", ls="--")
    ax.text(3.6e6 + 5e5, 0.33, "IBM Low Range")
    ax.axvline(58.8e6, color="purple", ls="--")
    ax.text(58.8e6 + 5e5, 0.33, "IBM High Range")
    ax.axvline(18.9e6, color="purple", ls="-")
    ax.text(18.9e6 + 5e5, 0.35, "IBM Mean")
    mpl_histplot_pane = pn.pane.Matplotlib(fig)
    return mpl_histplot_pane


def event_severity_liability_histplot(plot_data):
    """
    liability cost component histplot

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel histplot pane
    """
    param = "gu_liability"
    limit = 100_000_000
    bins = 30
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.histplot(
        data=plot_data,
        x=param,
        hue="source",
        stat="probability",
        binwidth=limit / bins,
        alpha=0.5,
        common_norm=False,
        ax=ax,
    )
    ax.set_title("liability costs")
    mpl_histplot_pane = pn.pane.Matplotlib(fig)
    return mpl_histplot_pane


def event_severity_regulatory_histplot(plot_data):
    """
    regulatory cost component histplot

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel histplot pane
    """
    param = "gu_regulatory"
    limit = 100_000_000
    bins = 30
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.histplot(
        data=plot_data,
        x=param,
        hue="source",
        stat="probability",
        binwidth=limit / bins,
        alpha=0.5,
        common_norm=False,
        ax=ax,
    )
    ax.set_title("regulatory costs")
    mpl_histplot_pane = pn.pane.Matplotlib(fig)
    return mpl_histplot_pane


def event_severity_privacy_histplot(plot_data):
    """
    privacy cost component histplot

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel histplot pane
    """
    param = "gu_privacy"
    limit = 100_000_000
    bins = 30
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.histplot(
        data=plot_data,
        x=param,
        hue="source",
        stat="probability",
        binwidth=limit / bins,
        alpha=0.5,
        common_norm=False,
        ax=ax,
    )
    ax.set_title("privacy costs")
    mpl_histplot_pane = pn.pane.Matplotlib(fig)
    return mpl_histplot_pane


def event_severity_bi_histplot(plot_data):
    """
    business interruption cost component histplot

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel histplot pane
    """
    param = "gu_bi"
    limit = 100_000_000
    bins = 30
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.histplot(
        data=plot_data,
        x=param,
        hue="source",
        stat="probability",
        binwidth=limit / bins,
        alpha=0.5,
        common_norm=False,
        ax=ax,
    )
    ax.set_title("business interruption costs")
    mpl_histplot_pane = pn.pane.Matplotlib(fig)
    return mpl_histplot_pane


def event_severity_extortion_histplot(plot_data):
    """
    extortion cost component histplot

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel histplot pane
    """
    param = "gu_extortion"
    limit = 100_000_000
    bins = 30
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.histplot(
        data=plot_data,
        x=param,
        hue="source",
        stat="probability",
        binwidth=limit / bins,
        alpha=0.5,
        common_norm=False,
        ax=ax,
    )
    ax.set_title("extortion costs")
    mpl_histplot_pane = pn.pane.Matplotlib(fig)
    return mpl_histplot_pane


def event_severity_model_costs_histplot(plot_data):
    """
    histplot showing the split of model cost components

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel histplot pane
    """
    limit = 100_000_000
    bins = 30
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.histplot(
        data=plot_data,
        x="value",
        hue="cost_component",
        stat="probability",
        binwidth=limit / bins,
        alpha=1,
        common_norm=True,
        element="step",
        fill=False,
        ax=ax,
    )
    mpl_histplot_pane = pn.pane.Matplotlib(fig)
    return mpl_histplot_pane


def event_frequency_overall_barplot(plot_data):
    """
    barplot showing the annual breach frequency

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel barplot pane
    """
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.barplot(
        data=plot_data,
        x="source",
        y=plot_data["frequency"],
        hue="confidentiality",
        ax=ax,
    )
    mpl_barplot_pane = pn.pane.Matplotlib(fig)
    return mpl_barplot_pane


def event_frequency_confidentiality_barplot(plot_data):
    """
    barplot showing the annual breach frequency for confidentiality events

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel barplot pane
    """
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.barplot(
        data=plot_data[plot_data["confidentiality"] == True],
        x="source",
        y=plot_data["frequency"],
        ax=ax,
    )
    mpl_barplot_pane = pn.pane.Matplotlib(fig)
    return mpl_barplot_pane


def event_frequency_annotated_confidentiality_barplot(plot_data):
    """
    barplot showing the annual breach frequency for non-confidentiality events

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel barplot pane
    """
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.barplot(
        data=plot_data[plot_data["confidentiality"] == False],
        x="source",
        y=plot_data["frequency"],
        ax=ax,
    )
    event_confidentiality_frequency = plot_data.loc[
        (plot_data["confidentiality"] == True) & (plot_data["source"] == "events"),
        "frequency",
    ].values[0]
    # bands estimated from the Verizon 2022 DBIR report p18
    event_breach_freq_high = (
        event_confidentiality_frequency / 0.50 - event_confidentiality_frequency
    )
    event_breach_freq_mid = (
        event_confidentiality_frequency / 0.55 - event_confidentiality_frequency
    )
    event_breach_freq_low = (
        event_confidentiality_frequency / 0.60 - event_confidentiality_frequency
    )
    ax.axhline(event_breach_freq_high, ls="--")
    ax.axhline(event_breach_freq_mid)
    ax.axhline(event_breach_freq_low, ls="--")
    mpl_barplot_pane = pn.pane.Matplotlib(fig)
    return mpl_barplot_pane


def events_annual_frequency_boxplot(plot_data):
    """
    boxplots showing the annual event frequency for model and events data

    Parameters
    ----------
    plot_data : pd.DataFrame
        data to be plotted

    Returns
    -------
    panel.pane.plot.Matplotlib
        panel boxplot pane
    """
    fig = Figure(figsize=(8, 5))
    ax = fig.subplots(1, 1)
    sns.boxplot(data=plot_data, x="source", y="frequency", ax=ax)
    ax.set_title(model_version())
    mpl_barplot_pane = pn.pane.Matplotlib(fig)
    return mpl_barplot_pane


def events_annual_frequency_sankey_plot(plot_data):
    """
    sankey plot showing split of model data by confidentiality

    Parameters
    ----------
    plot_data : tuple
        tuple of processed dataframe and dictionary of labels

    Returns
    -------
    panel.pane.plotly.Plotly
        panel sankeyplot pane
    """
    df_links = plot_data[0]
    label_dict = plot_data[1]
    fig = go.Figure(
        go.Sankey(
            node={"label": list(label_dict.keys())},
            link={
                "source": df_links["source"].values,
                "target": df_links["target"].values,
                "value": df_links["value"].values,
            },
        )
    )

    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), width=600, height=400)
    plotly_pane = pn.pane.Plotly(fig)
    return plotly_pane


def events_annual_frequency_model_cia_barplot(plot_data):
    """
    bar plot showing split of model data by confidentiality, availability and integrity

    Parameters
    ----------
    plot_data : pd.DataFrame
        normalized model cia data to be plotted

    Returns
    -------
    panel.pane.plotly.Plotly
        panel barplot pane
    """
    fig = go.Figure(go.Bar(x=plot_data.index, y=plot_data.values))

    fig.update_layout(margin=dict(l=10, r=10, t=10, b=10), width=400, height=400)
    plotly_pane = pn.pane.Plotly(fig)
    return plotly_pane


def load_dashboard():
    """
    configure and serve dashboard
    """
    # event duration plots
    event_duration_data = cache_plot_data(
        df=event_duration_plot_data(), data_name="event_duration_plot_data"
    )
    colors = set_colours()
    sns.set_palette(sns.color_palette(colors))
    event_duration_box_plot_pane = event_duration_box_plot(
        plot_data=event_duration_data
    )
    event_duration_ecdf_plot_pane = event_duration_ecdf_plot(
        plot_data=event_duration_data
    )
    event_duration_hist_plot_pane = event_duration_hist_plot(
        plot_data=event_duration_data
    )

    # event exposure plots
    exposure_revenue_data = cache_plot_data(
        df=join_datasets(), data_name="event_exposure_revenue_data"
    )
    exposure_sic_data = cache_plot_data(
        df=sic_data(), data_name="event_exposure_sic_data"
    )
    exposure_division_sic_data = cache_plot_data(
        df=division_sic_data(), data_name="event_exposure_division_sic_data"
    )
    exposure_geographic_data = cache_plot_data(
        df=geographic_data(), data_name="event_exposure_geographic_data"
    )

    event_exposure_revenue_hist_plot = event_exposure_revenue(
        plot_data=exposure_revenue_data
    )
    event_exposure_sic_count_bar_plot = event_exposure_sic_count(
        plot_data=exposure_sic_data
    )
    event_exposure_sic_division_bar_plot = event_exposure_sic_division_count(
        plot_data=exposure_division_sic_data
    )
    event_exposure_geography_bar_plot = event_exposure_geography(
        plot_data=exposure_geographic_data
    )

    # events per year plot
    events_per_year_data = cache_plot_data(
        df=events_per_year_plot_data(), data_name="events_per_year_plot_data"
    )
    events_per_year_plot = events_per_year_bar_plot(plot_data=events_per_year_data)

    # event severity plots
    overall_event_severity_data = cache_plot_data(
        df=overall_severity_plot_data(), data_name="overall_severity_plot_data"
    )

    event_severity_liability_data = cache_plot_data(
        df=liability_costs(), data_name="liability_costs"
    )
    event_severity_regulatory_data = cache_plot_data(
        df=regulatory_costs(), data_name="regulatory_costs"
    )
    event_severity_privacy_data = cache_plot_data(
        df=privacy_costs(), data_name="privacy_costs"
    )
    event_severity_bi_data = cache_plot_data(df=bi_costs(), data_name="bi_costs")
    event_severity_extortion_data = cache_plot_data(
        df=extortion_costs(), data_name="extortion_costs"
    )
    event_severity_model_costs_data = cache_plot_data(
        df=model_cost_plot_data(), data_name="model_cost_plot_data"
    )

    event_severity_overall_plot = event_severity_overall_hist_plot(
        plot_data=overall_event_severity_data
    )
    event_severity_annotated_overall_plot = event_severity_annotated_overall_hist_plot(
        plot_data=overall_event_severity_data
    )
    event_severity_liability_plot = event_severity_liability_histplot(
        plot_data=event_severity_liability_data
    )
    event_severity_regulatory_plot = event_severity_regulatory_histplot(
        plot_data=event_severity_regulatory_data
    )
    event_severity_privacy_plot = event_severity_privacy_histplot(
        plot_data=event_severity_privacy_data
    )
    event_severity_bi_plot = event_severity_bi_histplot(
        plot_data=event_severity_bi_data
    )
    event_severity_extortion_plot = event_severity_extortion_histplot(
        plot_data=event_severity_extortion_data
    )
    event_severity_model_costs_plot = event_severity_model_costs_histplot(
        plot_data=event_severity_model_costs_data
    )
    # event frequency plots
    event_frequency_data = cache_plot_data(
        df=overall_frequency_plot_data(), data_name="overall_frequency_plot_data"
    )
    event_frequency_overall_plot = event_frequency_overall_barplot(
        plot_data=event_frequency_data
    )
    event_frequency_confidentiality_plot = event_frequency_confidentiality_barplot(
        plot_data=event_frequency_data
    )
    event_frequency_annotated_confidentiality_plot = (
        event_frequency_annotated_confidentiality_barplot(
            plot_data=event_frequency_data
        )
    )
    # events frequency confidentiality plots
    events_annual_frequency_data = cache_plot_data(
        df=box_plot_data(), data_name="event_annual_frequency_data"
    )

    events_annual_model_cia_barplot_data = cache_plot_data(
        df=model_cia_barplot_data(), data_name="events_annual_model_cia_barplot_data"
    )

    events_annual_frequency_plot = events_annual_frequency_boxplot(
        plot_data=events_annual_frequency_data
    )
    events_annual_model_frequency_sankey_confidentiality_plot = (
        events_annual_frequency_sankey_plot(
            plot_data=confidentiality_model_sankey_plot_data(),
        )
    )
    events_annual_event_frequency_sankey_confidentiality_plot = (
        events_annual_frequency_sankey_plot(
            plot_data=confidentiality_events_sankey_plot_data(),
        )
    )
    events_annual_model_cia_frequency_sankey_confidentiality_plot = (
        events_annual_frequency_sankey_plot(
            plot_data=confidentiality_model_cia_sankey_plot_data(),
        )
    )

    events_annual_events_cia_frequency_sankey_confidentiality_plot = (
        events_annual_frequency_sankey_plot(
            plot_data=confidentiality_events_cia_sankey_plot_data(),
        )
    )

    events_annual_model_cia_plot = events_annual_frequency_model_cia_barplot(
        plot_data=events_annual_model_cia_barplot_data,
    )
    template = pn.template.FastListTemplate(
        title="Analytics - Dashboard",
        busy_indicator=pn.indicators.LoadingSpinner(
            width=50, height=50, value=True, color="primary", bgcolor="light"
        ),
        main=[
            pn.pane.Markdown(
                "###Event Duration - comparison of event duration between the F-1000 using FQ model v2022.2.3 and events data",
                width=1200,
                style={"color": "#5451f7"},
            ),
            pn.Row(
                pn.Tabs(
                    ("box-plot", event_duration_box_plot_pane),
                    ("ecdf_plot", event_duration_ecdf_plot_pane),
                    ("histogram_plot", event_duration_hist_plot_pane),
                )
            ),
            pn.pane.Markdown(
                "### Exposure Comparisons - comparison of revenue, SIC and geographical distribution  between the F-1000 using FQ model v2022.2.3 and events data",
                width=1200,
                style={"color": "#5451f7"},
            ),
            pn.Row(
                pn.Tabs(
                    (
                        "entity distribution by revenue",
                        event_exposure_revenue_hist_plot,
                    ),
                    (
                        "entity count by sic description",
                        event_exposure_sic_count_bar_plot,
                    ),
                    (
                        "entity count by sic division",
                        event_exposure_sic_division_bar_plot,
                    ),
                    ("entity count by geography", event_exposure_geography_bar_plot),
                )
            ),
            pn.pane.Markdown(
                "### Events per year - comparison of the count of events per year between the F-1000 using FQ model v2022.2.3 and events data",
                width=1200,
                style={"color": "#5451f7"},
            ),
            pn.Row(events_per_year_plot),
            pn.pane.Markdown(
                "### Event Severity - comparison of the overall event impact and impact by cost component between the F-1000 using FQ model v2022.2.3 and events data",
                width=1200,
                style={"color": "#5451f7"},
            ),
            pn.Row(
                pn.Tabs(
                    ("overall event severity", event_severity_overall_plot),
                    (
                        "annotated overall event severity",
                        event_severity_annotated_overall_plot,
                    ),
                    ("liability costs", event_severity_liability_plot),
                    ("regulatory costs", event_severity_regulatory_plot),
                    ("privacy costs", event_severity_privacy_plot),
                    ("bi costs", event_severity_bi_plot),
                    ("extortion costs", event_severity_extortion_plot),
                    ("model costs by component", event_severity_model_costs_plot),
                )
            ),
            pn.pane.Markdown(
                "### Event Frequency - comparison of the frequency of annual breaches between the F-1000 using FQ model v2022.2.3 and events data",
                width=1200,
                style={"color": "#5451f7"},
            ),
            pn.Row(
                pn.Tabs(
                    ("annual frequency breaches", event_frequency_overall_plot),
                    (
                        "annual frequency confidentiality breaches",
                        event_frequency_confidentiality_plot,
                    ),
                    (
                        "annual frequency non-confidentiality breaches",
                        event_frequency_annotated_confidentiality_plot,
                    ),
                )
            ),
            pn.pane.Markdown(
                "### Event Frequency - distribution and flow of data by confidentiality, integrity and availability for the F-1000 using FQ model v2022.2.3 and events data",
                width=1200,
                style={"color": "#5451f7"},
            ),
            pn.Row(
                pn.Tabs(
                    ("frequency box plot", events_annual_frequency_plot),
                    (
                        "confidentiality model sankey plot",
                        events_annual_model_frequency_sankey_confidentiality_plot,
                    ),
                    (
                        "confidentiality event sankey plot",
                        events_annual_event_frequency_sankey_confidentiality_plot,
                    ),
                    (
                        "confidentiality model cia sankey plot",
                        events_annual_model_cia_frequency_sankey_confidentiality_plot,
                    ),
                    (
                        "confidentiality events cia sankey plot",
                        events_annual_events_cia_frequency_sankey_confidentiality_plot,
                    ),
                    ("model cia bar plot", events_annual_model_cia_plot),
                )
            ),
        ],
        accent_base_color="#5451f7",
        header_background="#5451f7",
    )
    return template
