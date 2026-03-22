# 🏏 Cricbuzz LiveStats - Cricket Analytics Dashboard

A comprehensive cricket analytics dashboard that integrates live data from the Cricbuzz API with a SQL database to create an interactive web application.

## 📋 Features

- ⚡ **Real-time Match Updates** - Live scorecards from Cricbuzz API
- 📊 **Detailed Player Statistics** - Comprehensive player performance metrics
- 🔍 **SQL-driven Analytics** - 25+ advanced SQL queries for cricket insights
- 🛠️ **Full CRUD Operations** - Complete data management for players and matches
- 📱 **Interactive Dashboard** - Multi-page Streamlit web application

## 💼 Business Use Cases

1. **📺 Sports Media & Broadcasting** - Real-time match updates and player analysis
2. **🎮 Fantasy Cricket Platforms** - Player form tracking and team selection insights
3. **📈 Cricket Analytics Firms** - Advanced statistical modeling and trend analysis
4. **🎓 Educational Institutions** - SQL practice with real-world cricket datasets
5. **🎲 Sports Betting & Prediction** - Historical analysis for odds calculation

## 🏗️ Project Structure

```
cricbuzz_livestats/
├── app.py                      # Main Streamlit application
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── pages/
│   ├── home.py                # Home page with project info
│   ├── live_matches.py        # Live match updates from API
│   ├── top_stats.py           # Player statistics display
│   ├── sql_queries.py         # SQL analytics interface
│   ├── crud_operations.py     # Data management operations
│   └── __pycache__/           # Python cache
└── utils/
    ├── db_connection.py       # Database connection handler
    └── sql_queries_bank.py    # 25 predefined SQL queries
```

## � Data Flow

```
Cricbuzz API
    ↓
fetch_live_data.py (fetches & stores)
    ↓
PostgreSQL Database (live data)
    ↓
Dashboard Pages (query & display)
```

**Your database contains ONLY LIVE data from the API** - no sample data, only real cricket matches and teams!

## �🚀 Installation & Setup

### Prerequisites
- Python 3.8+
- PostgreSQL Database
- API Key from RapidAPI (Cricbuzz Cricket API)

### Step 1: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 2: Configure Database

**Option A: Using PostgreSQL**

1. Create a database:
```sql
CREATE DATABASE cricbuzz_livestats;
```

2. Update credentials in `utils/db_connection.py`:
```python
host="your_host"
database="cricbuzz_livestats"
user="your_username"
password="your_password"
port="5432"
```

**Option B: Using SQLite (Testing)**

Modify `utils/db_connection.py` to use SQLite for development.

### Step 3: Initialize Database Schema

Run the database initialization script to create tables (NO sample data):
```bash
python utils/init_database.py
```

This creates an empty database with proper schema. Next step will populate it with live data.

### Step 3B: Populate Database with Live API Data

Run the live data fetcher to populate the database with real Cricbuzz data:
```bash
python utils/fetch_live_data.py
```

This fetches:
- 🔴 Live matches currently happening
- ⏱️ Upcoming scheduled matches
- 🏟️ Teams and venues
- 📊 Match details

**Run this periodically** to keep your database fresh with latest cricket data!

### Step 4: Configure API Key

Update the API key in `pages/live_matches.py`:
```python
API_KEY = "your_rapidapi_key"
```

Or use environment variables in `.env`:
```
RAPIDAPI_KEY=your_key_here
RAPIDAPI_HOST=cricbuzz-cricket.p.rapidapi.com
```

### Step 5: Run the Application
```bash
streamlit run app.py
```

The application will open at `http://localhost:8501`

## 📄 Page Descriptions

### 1. **Home Page** 🏠
- Project introduction and features
- Business use cases overview
- Navigation guide
- Documentation links

### 2. **Live Matches** 📺
- Real-time match updates from Cricbuzz API
- Detailed scorecards with:
  - Team information
  - Current score and batting status
  - Bowler and batsman details
  - Match status and venue info

### 3. **Top Stats** 📊
- Top batsmen (runs, average, strike rate)
- Top bowlers (wickets, economy, average)
- Performance across different formats (Test, ODI, T20I)
- Visualizations of player performance trends

### 4. **SQL Analytics** 🧮
- 25 predefined SQL queries organized by difficulty:
  - **Beginner (8 queries)**: Basic SELECT, WHERE, GROUP BY operations
  - **Intermediate (8 queries)**: JOINs, subqueries, aggregate functions
  - **Advanced (9 queries)**: Window functions, CTEs, complex analytics
- Custom query interface for testing
- Results displayed in interactive tables

### 5. **CRUD Operations** 🛠️
- **Create**: Add new players/matches
- **Read**: View existing records with filtering
- **Update**: Modify player statistics and details
- **Delete**: Remove records safely
- Form-based user interface

## 🧮 SQL Queries (25 Total)

### Beginner Level (Questions 1-8)
1. Find all Indian players with roles and styles
2. Show recent matches with team and venue info
3. Top 10 ODI run scorers
4. Cricket venues with capacity > 25,000
5. Wins count by team
6. Player distribution by role
7. Highest individual score by format
8. Cricket series from 2024

### Intermediate Level (Questions 9-16)
9. All-rounders with 1000+ runs and 50+ wickets
10. Last 20 completed matches details
11. Player performance across formats
12. Team performance (home vs away)
13. Batting partnerships scoring 100+ runs
14. Bowling performance at different venues
15. Players in close match situations
16. Batting performance trends by year

### Advanced Level (Questions 17-25)
17. Toss advantage analysis in winning matches
18. Most economical bowlers in limited-overs
19. Consistency analysis of batsmen
20. Player performance ranking by format
21. Comprehensive performance scoring system
22. Head-to-head team match predictions
23. Recent player form and momentum analysis
24. Best batting partnerships analysis
25. Time-series career evolution tracking

## 🛢️ Database Schema

### Tables Included:
- `players` - Player information and statistics
- `matches` - Match details and results
- `innings` - Batting/bowling performance per innings
- `series` - Cricket series information
- `teams` - Team details and records
- `venues` - Stadium information
- `partnerships` - Batting pair statistics

## ⚙️ Technical Stack

- **Frontend**: Streamlit
- **Backend**: Python
- **Database**: PostgreSQL (or SQLite for testing)
- **API**: Cricbuzz Cricket REST API (RapidAPI)
- **Data Processing**: Pandas, NumPy
- **Visualization**: Plotly

## 📊 Performance Optimization Tips

1. **Indexing**: Create indexes on frequently queried columns:
   ```sql
   CREATE INDEX idx_player_country ON players(country);
   CREATE INDEX idx_match_date ON matches(match_date);
   ```

2. **Query Optimization**: Use efficient JOINs and avoid N+1 queries

3. **Caching**: Implement Streamlit's `@st.cache_data` for API calls

4. **Connection Pooling**: Use connection pooling for database queries

## 🔒 Security Recommendations

1. **Credentials**: Store database credentials and API keys in `.env` file
2. **SQL Injection**: Use parameterized queries (already implemented)
3. **API Keys**: Never commit API keys to version control
4. **Database**: Use strong passwords and restrict access by IP
5. **Error Messages**: Don't expose sensitive info in error messages

## 🐛 Troubleshooting

### Database Connection Error
- Verify PostgreSQL is running
- Check credentials in `db_connection.py`
- Ensure database exists

### API Connection Error
- Verify API key is correct
- Check internet connection
- Verify RapidAPI subscription is active

### Missing Tables
- Run `python utils/init_database.py`
- Check database connection

## 📚 Learning Resources

- [Streamlit Documentation](https://docs.streamlit.io)
- [PostgreSQL Documentation](https://www.postgresql.org/docs/)
- [Python Requests Library](https://requests.readthedocs.io/)
- [Pandas Documentation](https://pandas.pydata.org/docs/)

## 📝 Coding Standards

- Follow PEP 8 Python style guidelines
- Add docstrings to all functions
- Implement proper error handling
- Use type hints where applicable
- Keep functions focused and modular

## 🤝 Contributing

Feel free to extend this project with:
- Additional API endpoints
- More SQL queries
- Enhanced visualizations
- Prediction models
- Performance optimizations

## 📄 License

This project is open source and available for educational purposes.

## 👨‍💻 Author

Cricket Analytics Dashboard - Open Source Project

## 📧 Support

For issues and questions, refer to the documentation or create an issue in the repository.

---

**Last Updated**: March 2026  
**Version**: 1.0.0
