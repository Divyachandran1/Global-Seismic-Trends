import streamlit as st
import pandas as pd
import pymysql
import plotly.express as px

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Global Seismic Trends",
    layout="wide"
)

st.title("🌍 Global Seismic Trends Analysis")
st.markdown(
    "This dashboard analyzes global earthquake patterns based on magnitude, depth, and geographic distribution."
)

# ---------------- DATABASE LOAD ----------------
@st.cache_data
def load_data():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="Divyasenthil123",
        database="earthquake_db"
    )

    query = """
    SELECT 
        place,
        country,
        mag,
        depth_km AS depth,
        latitude,
        longitude,
        time
    FROM earthquakes_5_years
    WHERE mag IS NOT NULL
    """

    df = pd.read_sql(query, conn)
    conn.close()
    return df

df = load_data()

# ---------------- SIDEBAR FILTERS ----------------
st.sidebar.header("🔍 Filters")

# Country filter
countries = sorted(df["country"].dropna().unique().tolist())
selected_countries = st.sidebar.multiselect(
    "Select Country",
    options=countries,
    default=countries
)

# Magnitude filter
mag_min, mag_max = st.sidebar.slider(
    "Magnitude Range",
    float(df.mag.min()),
    float(df.mag.max()),
    (3.0, float(df.mag.max()))
)

# Apply filters
filtered_df = df[
    (df["country"].isin(selected_countries)) &
    (df["mag"].between(mag_min, mag_max))
]

# ---------------- KPI METRICS ----------------
col1, col2, col3 = st.columns(3)

col1.metric("🌐 Total Earthquakes", len(filtered_df))
col2.metric("📈 Max Magnitude", round(filtered_df.mag.max(), 2))
col3.metric("🌊 Avg Depth (km)", round(filtered_df.depth.mean(), 2))

# ---------------- MAGNITUDE DISTRIBUTION ----------------
st.subheader("📊 Earthquake Magnitude Distribution")

fig1 = px.histogram(
    filtered_df,
    x="mag",
    nbins=30,
    title="Distribution of Earthquake Magnitudes",
    color_discrete_sequence=["crimson"]
)
st.plotly_chart(fig1, use_container_width=True)

# ---------------- DEPTH vs MAGNITUDE ----------------
st.subheader("🌋 Depth vs Magnitude Relationship")

fig2 = px.scatter(
    filtered_df,
    x="depth",
    y="mag",
    opacity=0.6,
    color="mag",
    color_continuous_scale="Turbo",
    labels={"depth": "Depth (km)", "mag": "Magnitude"}
)
st.plotly_chart(fig2, use_container_width=True)

# ---------------- TOP COUNTRIES ----------------
st.subheader("📍 Top Earthquake-Prone Countries")

top_countries = (
    filtered_df["country"]
    .value_counts()
    .head(10)
    .reset_index()
)
top_countries.columns = ["Country", "Earthquake Count"]

fig3 = px.bar(
    top_countries,
    x="Earthquake Count",
    y="Country",
    orientation="h",
    color="Earthquake Count",
    color_continuous_scale="Reds"
)
st.plotly_chart(fig3, use_container_width=True)

# ---------------- GLOBAL MAP ----------------
st.subheader("🗺️ Global Seismic Activity Map")

fig4 = px.scatter_geo(
    filtered_df,
    lat="latitude",
    lon="longitude",
    size="mag",
    color="mag",
    projection="natural earth",
    color_continuous_scale="Plasma",
    title="Global Earthquake Locations by Magnitude"
)
st.plotly_chart(fig4, use_container_width=True)

# ---------------- RAW DATA TABLE ----------------
st.subheader("📄 Raw Earthquake Data")

st.dataframe(
    filtered_df.sort_values("time", ascending=False),
    use_container_width=True
)

# ---------------- INSIGHTS ----------------
st.subheader("🧠 Key Insights")

st.markdown("""
- 🌐 Earthquakes cluster along **tectonic plate boundaries**.
- 🔥 Strong earthquakes commonly occur at **moderate depths**.
- 🌊 Shallow earthquakes pose **higher surface risk**.
- ⚠️ The **Pacific Ring of Fire** dominates global seismic activity.
""")

st.success("✅ Global Seismic Trends analysis completed successfully")
