import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(
    page_title="Customer Retention & Churn Dashboard",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --------------------------------------------------
# CSS
# --------------------------------------------------
st.markdown("""
<style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    .stApp {
        background-color: #f5f6fa;
    }

    section[data-testid="stSidebar"] {
        background: #eef2ff;
        border-right: 1px solid #dbe4ff;
    }

    .block-container {
        padding-top: 0.8rem;
        padding-bottom: 1rem;
        max-width: 100%;
    }

    .dashboard-title {
        font-size: 40px;
        font-weight: 700;
        color: #2d2a5a;
        margin-bottom: 0.2rem;
    }

    .dashboard-subtitle {
        font-size: 14px;
        color: #6b7280;
        margin-bottom: 1rem;
    }

    .kpi-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 14px 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border: 1px solid #ececf3;
        min-height: 110px;
    }

    .kpi-title {
        font-size: 13px;
        color: #7c7f8a;
        margin-bottom: 8px;
        font-weight: 600;
    }

    .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #4f46e5;
        line-height: 1.1;
    }

    .kpi-sub {
        font-size: 12px;
        color: #8b8fa3;
        margin-top: 8px;
    }

    .tile-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 10px 12px 4px 12px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border: 1px solid #ececf3;
        margin-bottom: 14px;
    }

    .mini-card {
        background: #ffffff;
        border-radius: 18px;
        padding: 12px 14px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.06);
        border: 1px solid #ececf3;
        min-height: 118px;
        margin-bottom: 10px;
    }

    .mini-title {
        font-size: 12px;
        color: #7c7f8a;
        font-weight: 600;
    }

    .mini-value {
        font-size: 22px;
        color: #4f46e5;
        font-weight: 700;
        margin-top: 8px;
    }

    .small-note {
        color: #8b8fa3;
        font-size: 11px;
    }
</style>
""", unsafe_allow_html=True)

# --------------------------------------------------
# LOAD DATA
# --------------------------------------------------
@st.cache_data
def load_data():
    df = pd.read_csv("data/customer_churn.csv")
    df.columns = df.columns.str.strip()

    if "TotalCharges" in df.columns:
        df["TotalCharges"] = pd.to_numeric(df["TotalCharges"], errors="coerce")

    if "MonthlyCharges" in df.columns:
        df["MonthlyCharges"] = pd.to_numeric(df["MonthlyCharges"], errors="coerce")

    if "tenure" in df.columns:
        df["tenure"] = pd.to_numeric(df["tenure"], errors="coerce")

    df = df.dropna()

    if "Churn" in df.columns:
        df["Churn"] = df["Churn"].astype(str).str.strip()

    return df

df = load_data()

# --------------------------------------------------
# SIDEBAR FILTERS WITH CHECKBOXES
# --------------------------------------------------
st.sidebar.markdown("## Filters")

def checkbox_filter(title, options, key_prefix):
    st.sidebar.markdown(f"### {title}")
    selected = []
    for option in options:
        if st.sidebar.checkbox(option, value=True, key=f"{key_prefix}_{option}"):
            selected.append(option)
    return selected

contract_filter = checkbox_filter("Contract", sorted(df["Contract"].unique()), "contract")
gender_filter = checkbox_filter("Gender", sorted(df["gender"].unique()), "gender")
internet_filter = checkbox_filter("Internet Service", sorted(df["InternetService"].unique()), "internet")
payment_filter = checkbox_filter("Payment Method", sorted(df["PaymentMethod"].unique()), "payment")

tenure_min = int(df["tenure"].min())
tenure_max = int(df["tenure"].max())

tenure_range = st.sidebar.slider(
    "Select Tenure Range",
    min_value=tenure_min,
    max_value=tenure_max,
    value=(tenure_min, tenure_max)
)

monthly_min = float(df["MonthlyCharges"].min())
monthly_max = float(df["MonthlyCharges"].max())

monthly_range = st.sidebar.slider(
    "Select Monthly Charges Range",
    min_value=float(round(monthly_min, 2)),
    max_value=float(round(monthly_max, 2)),
    value=(float(round(monthly_min, 2)), float(round(monthly_max, 2)))
)

filtered_df = df[
    (df["Contract"].isin(contract_filter)) &
    (df["gender"].isin(gender_filter)) &
    (df["InternetService"].isin(internet_filter)) &
    (df["PaymentMethod"].isin(payment_filter)) &
    (df["tenure"] >= tenure_range[0]) &
    (df["tenure"] <= tenure_range[1]) &
    (df["MonthlyCharges"] >= monthly_range[0]) &
    (df["MonthlyCharges"] <= monthly_range[1])
]

# --------------------------------------------------
# SAFE FALLBACK
# --------------------------------------------------
if filtered_df.empty:
    st.markdown("<div class='dashboard-title'>Customer Retention & Churn Dashboard</div>", unsafe_allow_html=True)
    st.warning("No data available for the selected filters. Please select at least one option in each filter.")
    st.stop()

# --------------------------------------------------
# KPI CALCULATIONS
# --------------------------------------------------
total_customers = len(filtered_df)
churned_customers = len(filtered_df[filtered_df["Churn"] == "Yes"])
retained_customers = len(filtered_df[filtered_df["Churn"] == "No"])
churn_rate = (churned_customers / total_customers * 100) if total_customers != 0 else 0
avg_monthly_charge = filtered_df["MonthlyCharges"].mean()
avg_tenure = filtered_df["tenure"].mean()

highest_churn_contract = (
    filtered_df.groupby("Contract")["Churn"]
    .apply(lambda x: (x == "Yes").mean() * 100)
    .sort_values(ascending=False)
    .index[0]
)

highest_churn_internet = (
    filtered_df.groupby("InternetService")["Churn"]
    .apply(lambda x: (x == "Yes").mean() * 100)
    .sort_values(ascending=False)
    .index[0]
)

# --------------------------------------------------
# HEADER
# --------------------------------------------------
st.markdown("<div class='dashboard-title'>Customer Retention & Churn Dashboard</div>", unsafe_allow_html=True)
st.markdown("<div class='dashboard-subtitle'>Interactive churn analytics dashboard with cleaner filters and aligned layout</div>", unsafe_allow_html=True)

# --------------------------------------------------
# TOP KPI ROW
# --------------------------------------------------
k1, k2, k3, k4, k5 = st.columns([1.2, 1.2, 1.0, 1.0, 1.1])

with k1:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Total Customers</div>
        <div class="kpi-value">{total_customers:,}</div>
        <div class="kpi-sub">Filtered customer records</div>
    </div>
    """, unsafe_allow_html=True)

with k2:
    st.markdown(f"""
    <div class="kpi-card">
        <div class="kpi-title">Churned Customers</div>
        <div class="kpi-value">{churned_customers:,}</div>
        <div class="kpi-sub">Customers who left</div>
    </div>
    """, unsafe_allow_html=True)

with k3:
    st.markdown(f"""
    <div class="mini-card">
        <div class="mini-title">Retention</div>
        <div class="mini-value">{retained_customers:,}</div>
        <div class="small-note">Customers retained</div>
    </div>
    """, unsafe_allow_html=True)

with k4:
    st.markdown(f"""
    <div class="mini-card">
        <div class="mini-title">Churn Rate</div>
        <div class="mini-value">{churn_rate:.1f}%</div>
        <div class="small-note">Churn percentage</div>
    </div>
    """, unsafe_allow_html=True)

with k5:
    st.markdown(f"""
    <div class="mini-card">
        <div class="mini-title">Avg Monthly Charges</div>
        <div class="mini-value">{avg_monthly_charge:.0f}</div>
        <div class="small-note">Average monthly bill</div>
    </div>
    """, unsafe_allow_html=True)

# --------------------------------------------------
# SECOND ROW
# --------------------------------------------------
left1, left2, info_col, right1 = st.columns([1.2, 1.3, 0.95, 1.35])

with left1:
    churn_dist = filtered_df["Churn"].value_counts().reset_index()
    churn_dist.columns = ["Churn", "Count"]

    fig1 = px.pie(
        churn_dist,
        names="Churn",
        values="Count",
        hole=0.70,
        title="Churn Distribution",
        color="Churn",
        color_discrete_map={"Yes": "#4f46e5", "No": "#c7d2fe"}
    )
    fig1.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="white")
    st.markdown("<div class='tile-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig1, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with left2:
    contract_churn = filtered_df.groupby(["Contract", "Churn"]).size().reset_index(name="Count")
    fig2 = px.bar(
        contract_churn,
        x="Contract",
        y="Count",
        color="Churn",
        barmode="group",
        title="Churn by Contract Type",
        color_discrete_map={"Yes": "#4f46e5", "No": "#a5b4fc"}
    )
    fig2.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="white", plot_bgcolor="white")
    st.markdown("<div class='tile-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig2, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with info_col:
    st.markdown(f"""
    <div class="mini-card">
        <div class="mini-title">Highest Churn Contract</div>
        <div class="mini-value" style="font-size:18px;">{highest_churn_contract}</div>
        <div class="small-note">Most risky contract type</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="mini-card">
        <div class="mini-title">Avg Tenure</div>
        <div class="mini-value">{avg_tenure:.1f}</div>
        <div class="small-note">Average months stayed</div>
    </div>
    """, unsafe_allow_html=True)

    st.markdown(f"""
    <div class="mini-card">
        <div class="mini-title">Highest Churn Internet</div>
        <div class="mini-value" style="font-size:18px;">{highest_churn_internet}</div>
        <div class="small-note">Highest risk internet service</div>
    </div>
    """, unsafe_allow_html=True)

with right1:
    fig3 = px.histogram(
        filtered_df,
        x="MonthlyCharges",
        color="Churn",
        nbins=25,
        barmode="overlay",
        title="Monthly Charges Distribution",
        color_discrete_map={"Yes": "#4f46e5", "No": "#c7d2fe"}
    )
    fig3.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="white", plot_bgcolor="white")
    st.markdown("<div class='tile-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig3, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# THIRD ROW
# --------------------------------------------------
c1, c2, c3 = st.columns([1.25, 1.25, 1.4])

with c1:
    gender_churn = filtered_df.groupby(["gender", "Churn"]).size().reset_index(name="Count")
    fig4 = px.bar(
        gender_churn,
        x="gender",
        y="Count",
        color="Churn",
        barmode="group",
        title="Churn by Gender",
        color_discrete_map={"Yes": "#4f46e5", "No": "#a5b4fc"}
    )
    fig4.update_layout(height=285, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="white", plot_bgcolor="white")
    st.markdown("<div class='tile-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig4, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with c2:
    fig5 = px.box(
        filtered_df,
        x="Churn",
        y="tenure",
        color="Churn",
        title="Tenure by Churn",
        color_discrete_map={"Yes": "#4f46e5", "No": "#c7d2fe"}
    )
    fig5.update_layout(height=285, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="white", plot_bgcolor="white")
    st.markdown("<div class='tile-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig5, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with c3:
    payment_churn = filtered_df.groupby(["PaymentMethod", "Churn"]).size().reset_index(name="Count")
    fig6 = px.bar(
        payment_churn,
        x="PaymentMethod",
        y="Count",
        color="Churn",
        barmode="group",
        title="Payment Method vs Churn",
        color_discrete_map={"Yes": "#4f46e5", "No": "#a5b4fc"}
    )
    fig6.update_layout(height=285, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="white", plot_bgcolor="white")
    st.markdown("<div class='tile-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig6, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

# --------------------------------------------------
# FOURTH ROW
# --------------------------------------------------
d1, d2, d3 = st.columns([1.35, 1.1, 1.35])

with d1:
    temp_df = filtered_df.copy()
    temp_df["TenureGroup"] = pd.cut(
        temp_df["tenure"],
        bins=[0, 12, 24, 48, 72],
        labels=["0-12", "13-24", "25-48", "49-72"]
    )

    tenure_group_churn = temp_df.groupby(["TenureGroup", "Churn"]).size().reset_index(name="Count")

    fig7 = px.line(
        tenure_group_churn,
        x="TenureGroup",
        y="Count",
        color="Churn",
        markers=True,
        title="Customer Count Across Tenure Groups",
        color_discrete_map={"Yes": "#4f46e5", "No": "#a5b4fc"}
    )
    fig7.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="white", plot_bgcolor="white")
    st.markdown("<div class='tile-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig7, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with d2:
    internet_churn = filtered_df.groupby("InternetService")["Churn"].apply(
        lambda x: (x == "Yes").mean() * 100
    ).reset_index(name="ChurnRate")

    fig8 = px.pie(
        internet_churn,
        names="InternetService",
        values="ChurnRate",
        hole=0.68,
        title="Internet Service Risk Share",
        color_discrete_sequence=["#4f46e5", "#818cf8", "#c7d2fe"]
    )
    fig8.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="white")
    st.markdown("<div class='tile-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig8, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)

with d3:
    fig9 = px.histogram(
        filtered_df,
        x="tenure",
        color="Churn",
        nbins=25,
        barmode="overlay",
        title="Tenure Distribution",
        color_discrete_map={"Yes": "#4f46e5", "No": "#c7d2fe"}
    )
    fig9.update_layout(height=300, margin=dict(l=10, r=10, t=40, b=10), paper_bgcolor="white", plot_bgcolor="white")
    st.markdown("<div class='tile-card'>", unsafe_allow_html=True)
    st.plotly_chart(fig9, use_container_width=True, config={"displayModeBar": False})
    st.markdown("</div>", unsafe_allow_html=True)