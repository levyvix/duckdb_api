import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

from log_analyzer import LogAnalyzer

st.set_page_config(page_title="Log Analytics Dashboard", page_icon="📊", layout="wide")


# Initialize the log analyzer
@st.cache_data(ttl=300)  # Cache for 5 minutes
def load_log_data():
    analyzer = LogAnalyzer()
    return analyzer.load_logs(), analyzer


# Main dashboard
st.title("📊 Log Analytics Dashboard")
st.write("Real-time analysis of application logs")

# Load data
df, analyzer = load_log_data()

if df.empty:
    st.error("No log data found. Please check the logs directory.")
else:
    # Create two columns for the top metrics
    col1, col2, col3 = st.columns(3)

    # Success/Error Rate
    with col1:
        rates = analyzer.get_success_error_rate()
        total = rates["success"] + rates["error"]
        success_rate = (rates["success"] / total * 100) if total > 0 else 0

        fig = go.Figure(
            go.Indicator(
                mode="gauge+number",
                value=success_rate,
                title={"text": "Success Rate"},
                domain={"x": [0, 1], "y": [0, 1]},
                gauge={
                    "axis": {"range": [0, 100]},
                    "bar": {"color": "green"},
                    "steps": [
                        {"range": [0, 50], "color": "red"},
                        {"range": [50, 80], "color": "yellow"},
                        {"range": [80, 100], "color": "lightgreen"},
                    ],
                },
            )
        )
        st.plotly_chart(fig, use_container_width=True)

    # Log Level Distribution
    with col2:
        level_dist = analyzer.get_level_distribution()
        fig = px.pie(level_dist, values="frequency", names="level", title="Log Level Distribution")
        fig.update_traces(textinfo="value+percent")
        st.plotly_chart(fig, use_container_width=True)

    # Total Logs Over Time
    with col3:
        module_activity = analyzer.get_module_activity()
        daily_logs = module_activity.resample("h", on="timestamp").size()
        fig = px.line(daily_logs, title="Logs per Hour")
        st.plotly_chart(fig, use_container_width=True)

    # Process Durations
    st.subheader("Process Durations")
    durations = analyzer.get_process_durations()
    fig = px.bar(
        durations.head(10),
        x="module",
        y="duration",
        color="function",
        title="Top 10 Longest Operations",
        labels={"duration": "Duration (seconds)"},
    )
    st.plotly_chart(fig, use_container_width=True)

    # API Response Times
    st.subheader("API Performance")
    response_times = analyzer.get_response_times()
    if not response_times.empty:
        response_times["duration"] = response_times["elapsed"].apply(lambda x: x["seconds"])
        response_times["endpoint"] = response_times["extra"].apply(
            lambda x: x["extra"]["url"] if isinstance(x, dict) and "extra" in x else "unknown"
        )

        fig = px.box(
            response_times,
            x="endpoint",
            y="duration",
            title="API Response Time Distribution",
            labels={"duration": "Response Time (seconds)"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # Data Processing Statistics
    st.subheader("Data Processing Statistics")
    stats = analyzer.get_data_processing_stats()
    if not stats.empty:
        col1, col2 = st.columns(2)

        with col1:
            # Remove duplicate tables and keep the last entry
            unique_stats = stats.sort_values("table").groupby("table").last().reset_index()
            fig = px.bar(
                unique_stats,
                x="table",
                y="rows",
                title="Rows Processed by Table",
                labels={"rows": "Number of Rows"},
            )
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Remove duplicate tables and keep the last entry
            unique_stats = stats.sort_values("table").groupby("table").last().reset_index()
            fig = px.bar(
                unique_stats,
                x="table",
                y="columns",
                title="Columns by Table",
                labels={"columns": "Number of Columns"},
            )
            st.plotly_chart(fig, use_container_width=True)

    # Raw Logs Table
    with st.expander("View Raw Logs"):
        st.dataframe(analyzer.get_module_activity())
