# 🏏 Cricket Analytics Dashboard - Live Match Intelligence System

## 📖 Project Overview
A dynamic cricket analytics platform that bridges live match data with powerful SQL analytics. This application fetches real-time cricket match information, stores it in a structured database, and provides users with interactive analytics capabilities. Users can track live match progression, analyze historical player performance, execute custom SQL queries, and manage cricket statistics through an intuitive web interface.

---

## 🎯 Core Objectives
This project was built to solve the challenge of accessing, organizing, and analyzing cricket data through a single platform:
- 📡 **Real-time Data Ingestion**: Fetch live match scores and player statistics from external APIs
- 💾 **Data Persistence**: Store cricket metrics in a structured SQLite database for long-term analysis
- 🔎 **Analytics Engine**: Execute complex SQL queries to extract meaningful patterns from cricket data
- 🖥️ **User-Friendly Interface**: Display insights through an interactive web dashboard
- ✏️ **Data Management**: Provide full control to add, modify, or remove player and match records  

---

## � Real-World Applications

### 📺 Sports Commentary & Broadcasting
Commentators can access live match statistics, player form, and historical performance data during broadcasts for enhanced commentary and expert analysis.

### 🎮 Fantasy Cricket Applications
Fantasy platforms use this system to track real-time player performance, calculate points dynamically, and provide users with data-driven player selection recommendations.

### 📊 Cricket Statistics Research
Analysts and researchers can query the database to identify performance trends, venue-based patterns, and player matchups for strategic insights.

### 🎓 Educational & Learning Resource
This project serves as a hands-on learning platform for students to practice SQL queries, understand database design, and build full-stack web applications.

### 🎯 Tournament Management
Event organizers can use this system to track tournament progression, maintain leaderboards, and provide real-time updates to stakeholders.  

---

## 🏗️ Technical Architecture

### 🌐 Data Acquisition Layer
The application uses HTTP requests to connect to the Cricbuzz Cricket API, retrieving match information, player statistics, and venue details. Data is fetched on-demand and cached efficiently to minimize API calls.

### 💾 Data Storage Layer
All cricket data is stored in SQLite, a lightweight but powerful relational database. The schema includes dedicated tables for players, matches, and venues. Database connections are managed centrally to ensure consistency and prevent connection leaks.

### 📊 Analytics Layer
A comprehensive set of 25+ SQL queries enables users to perform analysis ranging from simple player lookups to complex aggregate operations like player averages by venue or team performance trends.

### 🖥️ Presentation Layer
Streamlit provides a responsive, multi-page web interface that handles user input, displays data visualizations, and manages state efficiently without requiring front-end expertise.

### 🔧 Data Management Layer
The CRUD operations interface allows authorized users to maintain data integrity by adding new records, updating existing statistics, and removing outdated information.  

---

## 📚 Analytics Capabilities
The platform includes 25+ pre-built SQL queries organized by complexity level:

**Foundational Queries**: Basic player searches, country filters, and simple aggregations like total runs or wicket counts.

**Intermediate Queries**: Multi-table joins to combine player and match data, finding matches within date ranges, calculating batting or bowling averages by country.

**Advanced Queries**: Sophisticated analyses including player form calculations over rolling windows, head-to-head matchups, venue performance correlations, and predictive metrics based on historical data.

Examples include:
- Identify top 10 run scorers across all formats
- Find matches played in the last 30 days with specific outcome filters
- Rank venues by capacity and match frequency
- Calculate toss win impact on match outcomes
- Track player momentum through recent performance trends  

---

## 📌 Application Features

### 1️⃣ Dashboard Home
Welcoming landing page that explains the project purpose, displays the technology stack, and guides users through available features via intuitive sidebar navigation.

### 2️⃣ Live Match Monitor
Fetches current match information from the Cricbuzz API in real-time. Displays scorecards with detailed batsman and bowler statistics, current partnership information, venue details, and match status updates. Includes automatic refresh capabilities.

### 3️⃣ Player Performance Leaderboards
Displays ranked lists of players across different categories: career run totals, strike rates, batting averages, wicket counts, and bowling economy rates. Supports filtering by country or role.

### 4️⃣ Analytics Query Engine
Provides two interfaces for data analysis: a curated set of 25 pre-optimized SQL queries with one-click execution, and a custom SQL editor for users to write and test their own analytical queries against the database.

### 5️⃣ Data Administration Panel
Allows authorized users to manage the cricket database through a graphical interface: insert new player records with multiple attributes, update existing statistics, delete outdated information, and maintain data quality.  

---

## 🛠️ Tech Stack  
- **Programming**: Python  
- **Framework**: Streamlit  
- **Database**: SQL (SQLite/MySQL/PostgreSQL)  
- **Libraries**: pandas, requests  
- **Data Source**: Cricbuzz API  

---

## 📦 Installation & Setup  

1. Clone the repository:  
   ```bash
   git clone https://github.com/yourusername/cricbuzz-livestats.git
   cd cricbuzz-livestats
   ```

2. Create & activate a virtual environment:  
   ```bash
   python -m venv venv
   source venv/bin/activate   # On Mac/Linux  
   venv\Scripts\activate      # On Windows  
   ```

3. Install dependencies:  
   ```bash
   pip install -r requirements.txt
   ```

4. Set up database & environment:  
   - Configure `utils/db_connection.py`  
   - Add `.env` file with API keys and DB credentials  

5. Run the app:  
   ```bash
   streamlit run app.py
   ```

---

## 📊 Expected Results  
- Real-time cricket dashboard  
- SQL-based analytics with 25+ queries  
- Player & team performance tracking  
- CRUD-enabled database operations  

---

## 📑 Deliverables  
- Source code (Python + Streamlit)  
- SQL schema & queries  
- Requirements.txt  
- Documentation (this README + project doc)  
- Working cricket analytics dashboard  

---

## 🏷️ Technical Tags  
`Python` `Streamlit` `SQL` `Database` `REST API` `pandas` `requests` `Sports Analytics` `Web Development`  
