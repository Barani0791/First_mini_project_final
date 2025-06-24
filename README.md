🚓 SecureCheck Analytics Dashboard
=================================

SecureCheck is a Streamlit-based interactive dashboard designed for analyzing police traffic stop data. It reads from an Excel file, stores the data in a PostgreSQL database, and offers an intuitive interface for visual exploration and filtering.

📦 Features
----------
- Dashboard View:
  • KPIs (Total Stops, Arrests, Searches)
  • Filterable by gender, country, age, violation, drug involvement, etc.
  • Choose between Bar, Pie, or Line charts
  • Tabbed views: Core Charts, Deep Insights, Country Comparison

- Custom Report View:
  • Search by Vehicle Number, Gender, or Country
  • Natural language summaries of traffic stops
  • Charts and tables for breakdowns by category

🛠 Setup Instructions
---------------------
1. Clone or download this repository
2. Ensure Python 3.10+ is installed
3. Set up a virtual environment (recommended):
   > python -m venv .venv
   > .\.venv\Scripts\activate (on Windows)
4. Install the required packages:
   > pip install -r requirements.txt
5. Run the Streamlit app:
   > streamlit run police_log_project.py

💾 Database Configuration
--------------------------
Update the database connection settings in `police_log_project.py`:

    username = 'your_username'
    password = 'your_password'
    host = 'your_host'
    port = '5432'
    database = 'your_database'

    engine = create_engine(f'postgresql+psycopg2://{username}:{password}@{host}:{port}/{database}')

✅ Requirements
---------------
See `requirements.txt`

📄 Notes
--------
- Excel file should be named `traffic_stops.xlsx`
- PostgreSQL database is used via psycopg2 and SQLAlchemy
- Charts rendered using Plotly

📜 License
----------
MIT License © 2025

👮 Made for Law Enforcement Analytics | 2025
