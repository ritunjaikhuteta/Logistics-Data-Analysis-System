import streamlit as st
import pandas as pd
import plotly.express as px

# 1. Page Configuration
st.set_page_config(page_title="Logistics Analysis System", layout="wide")
st.title("🚢 Logistics & Shipping Container Data Analysis")

# 2. Load and Clean Data
@st.cache_data
def load_data():
    df = pd.read_csv('shipping_containers_1000.csv')
    df['Scheduled_Arrival'] = pd.to_datetime(df['Scheduled_Arrival'])
    df['Actual_Arrival'] = pd.to_datetime(df['Actual_Arrival'])
    df['Delay_Days'] = (df['Actual_Arrival'] - df['Scheduled_Arrival']).dt.days
    df[['Carrier', 'Origin_Port', 'Destination_Port']] = df[['Carrier', 'Origin_Port', 'Destination_Port']].fillna('Unknown')
    return df

df = load_data()

# 3. Sidebar Filters
st.sidebar.header("Control Panel")
selected_carrier = st.sidebar.multiselect("Filter by Carrier", options=df["Carrier"].unique(), default=df["Carrier"].unique())

filtered_df = df[df["Carrier"].isin(selected_carrier)]

# 4. Top Level Metrics
m1, m2, m3 = st.columns(3)
m1.metric("Total Containers", len(filtered_df))
m2.metric("Avg Delay (Days)", round(filtered_df["Delay_Days"].mean(), 2))
m3.metric("Max Delay Found", f"{int(filtered_df['Delay_Days'].max())} Days")

# --- NEW: RISK ASSESSMENT SECTION ---
st.divider()
st.subheader("🚨 High-Risk Shipment Alert")

# Filter for shipments delayed by more than 10 days
high_risk_df = filtered_df[filtered_df['Delay_Days'] > 10]

if not high_risk_df.empty:
    st.error(f"ATTENTION: {len(high_risk_df)} shipments have exceeded the 10-day delay threshold!")
    # Show only the high-risk ones in a highlighted table
    st.dataframe(high_risk_df[['ContainerID', 'Carrier', 'Destination_Port', 'Delay_Days']].sort_values(by="Delay_Days", ascending=False))
else:
    st.success("All shipments are within acceptable delay limits.")
st.divider()

# 5. Charts
col_a, col_b = st.columns(2)

with col_a:
    st.subheader("Performance by Carrier")
    fig1 = px.bar(filtered_df.groupby("Carrier")["Delay_Days"].mean().reset_index(), 
                  x="Carrier", y="Delay_Days", color="Carrier", title="Avg Delay per Carrier")
    st.plotly_chart(fig1, use_container_width=True)

with col_b:
    st.subheader("Port Congestion Analysis")
    fig2 = px.box(filtered_df, x="Destination_Port", y="Delay_Days", 
                  color="Destination_Port", title="Delay Spread per Port")
    st.plotly_chart(fig2, use_container_width=True)

# 6. Raw Data View
with st.expander("Click to view full shipment logs"):
    st.write(filtered_df)
    st.subheader("📤 Export Insights")
csv_data = high_risk_df.to_csv(index=False).encode('utf-8')
st.download_button(
    label="Download High-Risk Shipment Report",
    data=csv_data,
    file_name='high_risk_alerts.csv',
    mime='text/csv',
)