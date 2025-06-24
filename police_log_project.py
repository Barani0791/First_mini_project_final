import streamlit as st
import pandas as pd
import plotly.express as px
from sqlalchemy import create_engine

# --- PostgreSQL Connection ---
file_path_excel = "traffic_stops.xlsx"
df = pd.read_excel(file_path_excel)

username = 'postgres1'
password = 'vNwAM5lasst2zi7gb0eVxEqjLpA8RbQJ'
host = 'dpg-d1b580je5dus73e88dpg-a.singapore-postgres.render.com'
port = '5432'
database = 'barani_db1'

engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')

# --- Upload to SQL ---
table_name = 'traffic_stops'
df.to_sql(table_name, engine, if_exists='replace', index=False)

# --- Load Data from SQL ---
df = pd.read_sql(f"SELECT * FROM {table_name}", engine)
df['stop_date'] = pd.to_datetime(df['stop_date'], errors='coerce')
df['stop_hour'] = pd.to_datetime(df['stop_time'], errors='coerce').dt.hour

# --- App Title ---
st.markdown("<h1 style='text-align: center; color: navy;'>🚓 SecureCheck Analytics Dashboard</h1>", unsafe_allow_html=True)
st.markdown("---")

# --- KPIs ---
col1, col2, col3 = st.columns(3)
col1.metric("Total Stops", len(df))
col2.metric("Arrests", int(df['is_arrested'].sum()))
col3.metric("Searches", int(df['search_conducted'].sum()))

# --- Navigation and Chart Option ---
page = st.sidebar.radio("📂 Select Page", ["Dashboard", "Custom Report"])
chart_type = st.sidebar.selectbox("📊 Choose Chart Type", ["Bar Chart", "Pie Chart", "Line Chart"])

# --- Custom Report ---
if page == "Custom Report":
    option = st.selectbox(
        "How would you like to access the data? : Through - ",
        ("Vehicle Number", "Gender", "Country"),
        index=None,
        placeholder="Select a valid option...",
    )

    if option == "Vehicle Number":
        st.write("You selected:", option)
        vehicle_no = st.text_input("Please Enter the Vehicle Number: ")
        if vehicle_no:
            vehicle_df = pd.read_sql(f"SELECT * FROM traffic_stops WHERE vehicle_number = '{vehicle_no}'", engine)

            if not vehicle_df.empty:
                st.markdown("### 📝 Vehicle Report Summary")

                for _, row in vehicle_df.iterrows():
                    try:
                        age = int(row['driver_age']) if not pd.isna(row['driver_age']) else "unknown"
                        gender = "male" if row['driver_gender'] == 'M' else "female" if row['driver_gender'] == 'F' else "unspecified"
                        violation = row['violation'] if pd.notna(row['violation']) else "a traffic violation"
                        time = row['stop_time'] if pd.notna(row['stop_time']) else "an unknown time"
                        search_conducted = row['search_conducted']
                        search_type = row['search_type'] if pd.notna(row['search_type']) else "no specific search"
                        outcome = row['stop_outcome'].lower() if pd.notna(row['stop_outcome']) else "no outcome"
                        duration = row['stop_duration'] if pd.notna(row['stop_duration']) else "an unknown duration"
                        drug_related = "drug-related." if row.get('drugs_related_stop', False) else "not drug-related."
                        country_name = row['country_name'] if pd.notna(row['country_name']) else "Unknown country"
                        stop_date = pd.to_datetime(row['stop_date']).strftime("%d %B %Y") if pd.notna(row['stop_date']) else "an unknown date"
                        emoji = "🚨" if row.get('is_arrested', False) else "🚗"

                        summary = (
                            f"{emoji} Vehicle no: {vehicle_no} was driven by a {age}-year-old {gender} driver who was stopped for {violation} violation "
                            f"on {stop_date} at {time}. "
                            f"{'No search was conducted,' if not search_conducted else f'A {search_type} was conducted,'} "
                            f"this occurred in {country_name}, and the outcome was a {outcome}. "
                            f"The stop lasted {duration} and was {drug_related}"
                        )
                        st.markdown(f"**{summary}**")
                    except Exception as e:
                        st.error(f"Error while creating summary: {e}")
            else:
                st.warning("No records found for the entered vehicle number.")

    elif option == "Gender":
        gender = st.selectbox("Choose the gender of the driver: ", ("Male", "Female", "Other"), index=None)
        gender_code = 'M' if gender == "Male" else 'F' if gender == "Female" else None

        if gender_code:
            gender_df = pd.read_sql(f"SELECT * FROM traffic_stops WHERE driver_gender = '{gender_code}'", engine)
            st.markdown(f"### 📊 Summary Report for {gender} Drivers")

            min_date = pd.to_datetime(gender_df['stop_date']).min()
            max_date = pd.to_datetime(gender_df['stop_date']).max()
            date_range = st.date_input("Filter by Stop Date", [min_date, max_date], min_value=min_date, max_value=max_date)
            if len(date_range) == 2:
                start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
                gender_df = gender_df[(pd.to_datetime(gender_df['stop_date']) >= start) & (pd.to_datetime(gender_df['stop_date']) <= end)]

            total = len(gender_df)
            st.write(f"👥 **Total {gender} Drivers:** {total}")

            with st.expander("🌍 Drivers by Country"):
                country_counts = gender_df['country_name'].value_counts().reset_index()
                country_counts.columns = ['Country', 'Count']
                st.dataframe(country_counts)
                if chart_type == "Bar Chart":
                    fig = px.bar(country_counts, x='Country', y='Count')
                elif chart_type == "Pie Chart":
                    fig = px.pie(country_counts, names='Country', values='Count')
                else:
                    fig = px.line(country_counts, x='Country', y='Count')
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("🚨 Stop Outcomes"):
                outcome_counts = gender_df['stop_outcome'].value_counts().reset_index()
                outcome_counts.columns = ['Outcome', 'Count']
                st.dataframe(outcome_counts)
                if chart_type == "Bar Chart":
                    fig = px.bar(outcome_counts, x='Outcome', y='Count')
                elif chart_type == "Pie Chart":
                    fig = px.pie(outcome_counts, names='Outcome', values='Count')
                else:
                    fig = px.line(outcome_counts, x='Outcome', y='Count')
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("🔍 Search Conducted"):
                searched = gender_df['search_conducted'].sum()
                not_searched = len(gender_df) - searched
                fig = px.pie(names=['Searched', 'Not Searched'], values=[searched, not_searched])
                st.plotly_chart(fig, use_container_width=True)

            with st.expander("💊 Drug-Related Stops"):
                drugs = gender_df['drugs_related_stop'].sum()
                fig = px.pie(names=['Drug-Related', 'Non-Drug-Related'], values=[drugs, total - drugs])
                st.plotly_chart(fig, use_container_width=True)
        else:
            st.warning("Please select a valid gender.")

    elif option == "Country":
        country = st.text_input("Please Enter the Country name: ").lower()
        if country:
            country_df = pd.read_sql(f"SELECT * FROM traffic_stops WHERE lower(country_name) = '{country}'", engine)
            if not country_df.empty:
                st.markdown(f"### 📊 Summary Report for Drivers from {country.title()}")

                min_date = pd.to_datetime(country_df['stop_date']).min()
                max_date = pd.to_datetime(country_df['stop_date']).max()
                date_range = st.date_input("Filter by Stop Date", [min_date, max_date], min_value=min_date, max_value=max_date)
                if len(date_range) == 2:
                    start, end = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
                    country_df = country_df[(pd.to_datetime(country_df['stop_date']) >= start) & (pd.to_datetime(country_df['stop_date']) <= end)]

                total = len(country_df)
                st.write(f"👥 **Total Drivers from {country.title()}:** {total}")

                with st.expander("👤 Gender Distribution"):
                    gender_counts = country_df['driver_gender'].value_counts().reset_index()
                    gender_counts.columns = ['Gender', 'Count']
                    st.dataframe(gender_counts)
                    if chart_type == "Bar Chart":
                        fig = px.bar(gender_counts, x='Gender', y='Count')
                    elif chart_type == "Pie Chart":
                        fig = px.pie(gender_counts, names='Gender', values='Count')
                    else:
                        fig = px.line(gender_counts, x='Gender', y='Count')
                    st.plotly_chart(fig, use_container_width=True)

                with st.expander("🚨 Stop Outcomes"):
                    outcome_counts = country_df['stop_outcome'].value_counts().reset_index()
                    outcome_counts.columns = ['Outcome', 'Count']
                    st.dataframe(outcome_counts)
                    if chart_type == "Bar Chart":
                        fig = px.bar(outcome_counts, x='Outcome', y='Count')
                    elif chart_type == "Pie Chart":
                        fig = px.pie(outcome_counts, names='Outcome', values='Count')
                    else:
                        fig = px.line(outcome_counts, x='Outcome', y='Count')
                    st.plotly_chart(fig, use_container_width=True)

                with st.expander("🔍 Search Conducted"):
                    searched = country_df['search_conducted'].sum()
                    not_searched = len(country_df) - searched
                    fig = px.pie(names=['Searched', 'Not Searched'], values=[searched, not_searched])
                    st.plotly_chart(fig, use_container_width=True)

                with st.expander("💊 Drug-Related Stops"):
                    drugs = country_df['drugs_related_stop'].sum()
                    fig = px.pie(names=['Drug-Related', 'Non-Drug-Related'], values=[drugs, total - drugs])
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.warning("No records found for the entered country.")

# --- Dashboard ---
if page == "Dashboard":
    st.markdown("## 📊 Dashboard Insights")

    # Sidebar Filters
    st.sidebar.header("🔍 Dashboard Filters")
    country_filter = st.sidebar.selectbox("Select Country", options=["All"] + sorted(df['country_name'].dropna().unique()))
    gender_filter = st.sidebar.selectbox("Select Gender", options=["All", "Male", "Female"])
    violation_filter = st.sidebar.selectbox("Select Violation", options=["All"] + sorted(df['violation'].dropna().unique()))
    min_age = int(df['driver_age'].min())
    max_age = int(df['driver_age'].max())
    age_range = st.sidebar.slider("Driver Age Range", min_value=min_age, max_value=max_age, value=(min_age, max_age))
    search_filter = st.sidebar.selectbox("Search Conducted", ["All", "True", "False"])
    arrest_filter = st.sidebar.selectbox("Arrested", ["All", "True", "False"])
    drug_filter = st.sidebar.selectbox("Drug-Related Stop", ["All", "True", "False"])
    min_date = df['stop_date'].min()
    max_date = df['stop_date'].max()
    date_range = st.sidebar.date_input("Date Range", [min_date, max_date])
    stop_durations = df['stop_duration'].dropna().unique().tolist()
    duration_filter = st.sidebar.multiselect("Stop Duration", options=stop_durations, default=stop_durations)

    # Apply Filters
    filtered_df = df.copy()
    if country_filter != "All":
        filtered_df = filtered_df[filtered_df['country_name'] == country_filter]
    if gender_filter != "All":
        filtered_df = filtered_df[filtered_df['driver_gender'] == gender_filter]
    if violation_filter != "All":
        filtered_df = filtered_df[filtered_df['violation'] == violation_filter]
    filtered_df = filtered_df[(filtered_df['driver_age'] >= age_range[0]) & (filtered_df['driver_age'] <= age_range[1])]
    if search_filter != "All":
        filtered_df = filtered_df[filtered_df['search_conducted'] == (search_filter == "True")]
    if arrest_filter != "All":
        filtered_df = filtered_df[filtered_df['is_arrested'] == (arrest_filter == "True")]
    if drug_filter != "All":
        filtered_df = filtered_df[filtered_df['drugs_related_stop'] == (drug_filter == "True")]
    if len(date_range) == 2:
        start_date, end_date = pd.to_datetime(date_range[0]), pd.to_datetime(date_range[1])
        filtered_df = filtered_df[(filtered_df['stop_date'] >= start_date) & (filtered_df['stop_date'] <= end_date)]
    if duration_filter:
        filtered_df = filtered_df[filtered_df['stop_duration'].isin(duration_filter)]

    # Tabs
    tab1, tab2, tab3 = st.tabs(["📊 Core Charts", "📈 Deep Insights", "🌍 Country Comparison"])

    def render_chart(df, chart_type, x=None, y=None, color=None, names=None, values=None, title=""):
        if chart_type == "Bar Chart":
            return px.bar(df, x=x, y=y, color=color, title=title)
        elif chart_type == "Pie Chart":
            return px.pie(df, names=names or x, values=values or y, title=title)
        elif chart_type == "Line Chart":
            return px.line(df, x=x, y=y, color=color, title=title)
        else:
            return px.bar(df, x=x, y=y, color=color)

    with tab1:
        st.subheader("Violation Distribution by Age")
        age_violation = filtered_df.groupby("driver_age")["violation"].count().reset_index(name="count")
        fig1 = render_chart(age_violation, chart_type, x="driver_age", y="count", title="Violations by Age")
        st.plotly_chart(fig1, use_container_width=True)

        st.subheader("Arrest Rate by Country")
        arrest_country = filtered_df.groupby("country_name")["is_arrested"].mean().reset_index()
        fig2 = render_chart(arrest_country, chart_type, x="country_name", y="is_arrested", title="Arrest Rate by Country")
        st.plotly_chart(fig2, use_container_width=True)

        st.subheader("Traffic Stops by Hour")
        stops_hour = filtered_df['stop_hour'].value_counts().sort_index().reset_index()
        stops_hour.columns = ['Hour', 'Count']
        fig3 = render_chart(stops_hour, chart_type, x="Hour", y="Count", title="Stops by Hour")
        st.plotly_chart(fig3, use_container_width=True)

    with tab2:
        st.subheader("Arrest Rate by Violation")
        arrest_violation = filtered_df.groupby("violation")["is_arrested"].mean().reset_index()
        fig4 = render_chart(arrest_violation, chart_type, x="violation", y="is_arrested", title="Arrest Rate by Violation")
        st.plotly_chart(fig4, use_container_width=True)

        st.subheader("Drug-Related Stops")
        drug_counts = filtered_df['drugs_related_stop'].value_counts().reset_index()
        drug_counts.columns = ['Drug Related', 'Count']
        fig5 = render_chart(drug_counts, chart_type, x="Drug Related", y="Count", title="Drug-Related Stops")
        st.plotly_chart(fig5, use_container_width=True)

        st.subheader("Stop Duration by Violation")
        duration_counts = filtered_df.groupby(["violation", "stop_duration"]).size().reset_index(name="count")
        fig6 = render_chart(duration_counts, chart_type, x="violation", y="count", color="stop_duration", title="Stop Duration by Violation")
        st.plotly_chart(fig6, use_container_width=True)

    with tab3:
        st.subheader("Violations by Gender")
        vg = filtered_df.groupby(["driver_gender", "violation"]).size().reset_index(name="count")
        fig7 = render_chart(vg, chart_type, x="violation", y="count", color="driver_gender", title="Violations by Gender")
        st.plotly_chart(fig7, use_container_width=True)

        st.subheader("Violation Frequency by Country")
        vc = filtered_df.groupby(["country_name", "violation"]).size().reset_index(name="count")
        fig8 = render_chart(vc, chart_type, x="country_name", y="count", color="violation", title="Violation Frequency by Country")
        st.plotly_chart(fig8, use_container_width=True)

        st.subheader("Search Conducted by Race")
        sr = filtered_df.groupby("driver_race")["search_conducted"].mean().reset_index()
        fig9 = render_chart(sr, chart_type, x="driver_race", y="search_conducted", title="Search by Race")
        st.plotly_chart(fig9, use_container_width=True)

    st.markdown("---")
    st.markdown("<p style='text-align: center; color: gray;'>Made for Law Enforcement Analytics | 2025</p>", unsafe_allow_html=True)