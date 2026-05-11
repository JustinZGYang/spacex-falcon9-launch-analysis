# SpaceX Falcon 9 Launch Success Analysis Dashboard
# This Dash app focuses on representative factors that may influence Falcon 9 landing outcomes:
# launch site, payload mass, orbit type, and launch sequence.

from pathlib import Path

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px


# -----------------------------
# Project paths and data loading
# -----------------------------

PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
DATA_PATH = DATA_DIR / "spacex_launches_cleaned.csv"

spacex_df = pd.read_csv(DATA_PATH)

spacex_df["Date"] = pd.to_datetime(spacex_df["Date"], errors="coerce")

# Keep payload slider dynamic.
min_payload = int(spacex_df["PayloadMass"].min())
max_payload = int(spacex_df["PayloadMass"].max())

payload_marks = {
    int(value): f"{int(value):,}"
    for value in range(0, int(max_payload) + 2500, 2500)
}

site_options = [{"label": "All Sites", "value": "ALL"}] + [
    {"label": site, "value": site}
    for site in sorted(spacex_df["LaunchSite"].dropna().unique())
]


# -----------------------------
# Global dashboard colors
# -----------------------------

PRIMARY_BLUE = "#4E79A7"
SUCCESS_GREEN = "#59A14F"
FAILURE_RED = "#E15759"
WARNING_ORANGE = "#F28E2B"
NEUTRAL_GRAY = "#B0B0B0"

OUTCOME_COLOR_MAP = {
    "Success": SUCCESS_GREEN,
    "Failure": FAILURE_RED,
}

PLOTLY_TEMPLATE = "plotly_white"


# -----------------------------
# Helper functions
# -----------------------------

def filter_data(selected_site, payload_range):
    """Filter launch data by selected launch site and payload range."""
    low, high = payload_range

    filtered_df = spacex_df[
        (spacex_df["PayloadMass"] >= low)
        & (spacex_df["PayloadMass"] <= high)
    ]

    if selected_site != "ALL":
        filtered_df = filtered_df[filtered_df["LaunchSite"] == selected_site]

    return filtered_df


def format_figure(fig):
    """Apply consistent styling to Plotly figures."""
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title_x=0.5,
        font=dict(family="Arial", size=13, color="#333333"),
        margin=dict(l=45, r=35, t=70, b=55),
        legend_title_text="",
    )
    return fig


def make_empty_figure(message):
    """Return a clean placeholder figure when filters produce no data."""
    fig = px.scatter(title=message)
    fig.update_layout(
        template=PLOTLY_TEMPLATE,
        title_x=0.5,
        xaxis=dict(visible=False),
        yaxis=dict(visible=False),
        annotations=[
            dict(
                text=message,
                showarrow=False,
                xref="paper",
                yref="paper",
                x=0.5,
                y=0.5,
                font=dict(size=16),
            )
        ],
    )
    return fig


# -----------------------------
# Dash app initialization
# -----------------------------

app = dash.Dash(__name__)
server = app.server


# -----------------------------
# App layout
# -----------------------------

app.layout = html.Div(
    children=[
        html.H1(
            "SpaceX Falcon 9 Launch Success Dashboard",
            style={
                "textAlign": "center",
                "color": "#333333",
                "fontSize": 38,
                "marginBottom": "10px",
            },
        ),

        html.P(
            "Explore representative factors related to Falcon 9 landing success: launch site, payload mass, orbit type, and launch sequence.",
            style={
                "textAlign": "center",
                "color": "#555555",
                "fontSize": 16,
                "marginBottom": "25px",
            },
        ),

        html.Div(
            children=[
                html.Div(
                    children=[
                        html.Label(
                            "Select Launch Site",
                            style={"fontWeight": "bold"},
                        ),
                        dcc.Dropdown(
                            id="site-dropdown",
                            options=site_options,
                            value="ALL",
                            placeholder="Select a launch site",
                            searchable=True,
                            clearable=False,
                        ),
                    ],
                    style={"width": "48%", "display": "inline-block"},
                ),

                html.Div(
                    children=[
                        html.Label(
                            "Payload Range (kg)",
                            style={"fontWeight": "bold"},
                        ),
                        dcc.RangeSlider(
                            id="payload-slider",
                            min=0,
                            max=max_payload,
                            step=500,
                            marks=payload_marks,
                            value=[min_payload, max_payload],
                            tooltip={
                                "placement": "bottom",
                                "always_visible": False,
                            },
                        ),
                    ],
                    style={
                        "width": "48%",
                        "display": "inline-block",
                        "float": "right",
                    },
                ),
            ],
            style={"marginBottom": "30px"},
        ),

        html.Div(
            children=[
                html.Div(
                    dcc.Graph(id="success-pie-chart"),
                    style={"width": "49%", "display": "inline-block"},
                ),

                html.Div(
                    dcc.Graph(id="success-payload-scatter-chart"),
                    style={
                        "width": "49%",
                        "display": "inline-block",
                        "float": "right",
                    },
                ),
            ],
        ),

        html.Div(
            children=[
                html.Div(
                    dcc.Graph(id="site-success-bar-chart"),
                    style={"width": "49%", "display": "inline-block"},
                ),

                html.Div(
                    dcc.Graph(id="orbit-success-bar-chart"),
                    style={
                        "width": "49%",
                        "display": "inline-block",
                        "float": "right",
                    },
                ),
            ],
        ),

        html.Div(
            children=[
                html.Div(
                    dcc.Graph(id="flight-trend-chart"),
                    style={"width": "100%", "display": "inline-block"},
                ),
            ],
        ),

        html.Div(
            children=[
                html.H3("Key Insights", style={"color": "#333333"}),
                html.Ul(
                    [
                        html.Li("Launch success varies across launch sites, suggesting site-level operational differences."),
                        html.Li("Payload mass is an important factor to explore, but it does not fully explain launch success by itself."),
                        html.Li("Mission profile variables such as orbit type and payload mass appear to influence landing outcomes."),
                        html.Li("Launch sequence helps show whether success improved as SpaceX gained operational experience."),
                    ],
                    style={"lineHeight": "1.8", "color": "#555555"},
                ),
            ],
            style={
                "backgroundColor": "#F7F7F7",
                "padding": "18px",
                "borderRadius": "8px",
                "marginTop": "25px",
            },
        ),
    ],
    style={
        "maxWidth": "1200px",
        "margin": "0 auto",
        "padding": "20px",
        "fontFamily": "Arial, sans-serif",
    },
)


@app.callback(
    Output("success-pie-chart", "figure"),
    Input("site-dropdown", "value"),
    Input("payload-slider", "value"),
)
def update_pie_chart(selected_site, payload_range):
    filtered_df = filter_data(selected_site, payload_range)

    if filtered_df.empty:
        return make_empty_figure("No launch data available for the selected filters.")

    if selected_site == "ALL":
        success_counts = (
            filtered_df[filtered_df["Class"] == 1]["LaunchSite"]
            .value_counts()
            .reset_index()
        )
        success_counts.columns = ["Launch Site", "Count"]

        fig = px.pie(
            success_counts,
            names="Launch Site",
            values="Count",
            title="Successful Landing Count by Launch Site",
            color_discrete_sequence=px.colors.qualitative.Set2,
        )
        fig.update_traces(textinfo="label+value")

    else:
        outcome_counts = (
            filtered_df["OutcomeLabel"]
            .value_counts()
            .reset_index()
        )
        outcome_counts.columns = ["Outcome", "Count"]

        fig = px.pie(
            outcome_counts,
            names="Outcome",
            values="Count",
            title=f"Success vs Failure for {selected_site}",
            color="Outcome",
            color_discrete_map=OUTCOME_COLOR_MAP,
        )
        fig.update_traces(textinfo="label+value")

    return format_figure(fig)


@app.callback(
    Output("success-payload-scatter-chart", "figure"),
    Input("site-dropdown", "value"),
    Input("payload-slider", "value"),
)
def update_scatter_chart(selected_site, payload_range):
    filtered_df = filter_data(selected_site, payload_range)

    if filtered_df.empty:
        return make_empty_figure("No launch data available for the selected filters.")

    chart_title = (
        "Payload Mass vs Landing Outcome for All Sites"
        if selected_site == "ALL"
        else f"Payload Mass vs Landing Outcome for {selected_site}"
    )

    fig = px.scatter(
        filtered_df,
        x="PayloadMass",
        y="Class",
        color="OutcomeLabel",
        symbol="LaunchSite" if selected_site == "ALL" else None,
        hover_data=[
            "LaunchSite",
            "Date",
            "PayloadMass",
            "Orbit",
            "OutcomeLabel",
        ],
        color_discrete_map=OUTCOME_COLOR_MAP,
        title=chart_title,
        labels={
            "PayloadMass": "Payload Mass (kg)",
            "Class": "Landing Outcome",
            "OutcomeLabel": "Outcome",
        },
    )

    fig.update_yaxes(
        tickmode="array",
        tickvals=[0, 1],
        ticktext=["Failure", "Success"],
        range=[-0.2, 1.2],
    )

    fig.update_traces(marker=dict(size=10, opacity=0.75))

    return format_figure(fig)


@app.callback(
    Output("site-success-bar-chart", "figure"),
    Input("payload-slider", "value"),
)
def update_site_success_bar(payload_range):
    filtered_df = filter_data("ALL", payload_range)

    if filtered_df.empty:
        return make_empty_figure("No launch data available for the selected payload range.")

    site_success = (
        filtered_df
        .groupby("LaunchSite", as_index=False)
        .agg(SuccessRate=("Class", "mean"), LaunchCount=("Class", "count"))
        .sort_values("SuccessRate", ascending=False)
    )

    fig = px.bar(
        site_success,
        x="LaunchSite",
        y="SuccessRate",
        text=site_success["SuccessRate"].round(2),
        hover_data=["LaunchCount"],
        title="Success Rate by Launch Site",
        labels={
            "LaunchSite": "Launch Site",
            "SuccessRate": "Success Rate",
        },
        color_discrete_sequence=[PRIMARY_BLUE],
    )

    fig.update_yaxes(range=[0, 1])
    fig.update_traces(textposition="outside")

    return format_figure(fig)


@app.callback(
    Output("orbit-success-bar-chart", "figure"),
    Input("site-dropdown", "value"),
    Input("payload-slider", "value"),
)
def update_orbit_success_chart(selected_site, payload_range):
    filtered_df = filter_data(selected_site, payload_range)

    if filtered_df.empty:
        return make_empty_figure("No launch data available for the selected filters.")

    orbit_success = (
        filtered_df
        .groupby("Orbit", as_index=False)
        .agg(SuccessRate=("Class", "mean"), LaunchCount=("Class", "count"))
        .sort_values("SuccessRate", ascending=False)
    )

    fig = px.bar(
        orbit_success,
        x="Orbit",
        y="SuccessRate",
        text=orbit_success["SuccessRate"].round(2),
        hover_data=["LaunchCount"],
        title="Success Rate by Orbit Type",
        labels={
            "Orbit": "Orbit Type",
            "SuccessRate": "Success Rate",
        },
        color_discrete_sequence=[WARNING_ORANGE],
    )

    fig.update_yaxes(range=[0, 1])
    fig.update_traces(textposition="outside")

    return format_figure(fig)


@app.callback(
    Output("flight-trend-chart", "figure"),
    Input("site-dropdown", "value"),
    Input("payload-slider", "value"),
)
def update_flight_trend_chart(selected_site, payload_range):
    filtered_df = filter_data(selected_site, payload_range)

    if filtered_df.empty:
        return make_empty_figure("No launch data available for the selected filters.")

    if "FlightNumber" not in filtered_df.columns:
        return make_empty_figure("FlightNumber is not available in the dataset.")

    trend_df = filtered_df.sort_values("FlightNumber").copy()

    fig = px.scatter(
        trend_df,
        x="FlightNumber",
        y="Class",
        color="OutcomeLabel",
        hover_data=[
            "LaunchSite",
            "Date",
            "PayloadMass",
            "Orbit",
            "OutcomeLabel",
        ],
        color_discrete_map=OUTCOME_COLOR_MAP,
        title="Landing Outcome by Flight Number",
        labels={
            "FlightNumber": "Flight Number",
            "Class": "Landing Outcome",
            "OutcomeLabel": "Outcome",
        },
    )

    fig.update_yaxes(
        tickmode="array",
        tickvals=[0, 1],
        ticktext=["Failure", "Success"],
        range=[-0.2, 1.2],
    )

    fig.update_traces(marker=dict(size=10, opacity=0.75))

    return format_figure(fig)


if __name__ == "__main__":
    app.run(debug=True)
