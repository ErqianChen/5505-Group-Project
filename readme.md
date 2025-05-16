# CITS5505-Group10-Project
# Fitness Tracker Web App

A full-stack fitness tracking web application built with Flask, supporting user authentication, workout logging, social features, and data visualization.

---

## Environment & Dependencies

- **Python**: 3.10+
- **Flask**: 2.3.x
- **Flask-WTF**: 1.1.x
- **Flask-SQLAlchemy**: 3.0.x
- **WTForms**: 3.0.x
- **Jinja2**: 3.1.x
- **Selenium**: 4.x (for testing)
- **SQLite**: (default database)
- **Other**: See `requirements.txt` for the full list.

---

## How to Run

1. **Clone the repository:**
   ```
   git clone https://github.com/ErqianChen/CITS5505-Group10-Project.git
   cd CITS5505-Group10-Project
   ```

2. **Create and activate a virtual environment:**
   ```
   python3 -m venv venv
   source venv/bin/activate
   ```

3. **Install dependencies:**
   ```
   pip install -r requirements.txt
   ```

4. **(Optional) Initialize the database:**
   ```
   python init_db.py
   ```
   The database will be available as app.db.


5. **Run the application:**
   ```
   python app.py
   ```
   The app will be available at `http://127.0.0.1:5000/`.

6. **(Optional) Run tests:**
   ```
   pytest
   ```

---

## Team Contributions

- **Erqian Chen**
  - Main page base framework
  - Account section implementation: user info logging, browsing history etc
  - Account section backend-frontend integration
  - Assisted with login system backend
  - Path routing and model integration

- **Harry Zhu**
  - Database schema design and mock data insertion
  - Login system implementation (Jinja-based frontend)
  - Record section implementation: data analysis, visualization, leaderboard
  - Record and Social section backend-frontend integration
  - Assisted with Path routing and model integration
  - Blueprints setup

- **Jiasen Niu**
  - Social section implementation: posts, likes, comments, bookmarks
  - Test suite development (unit & Selenium tests)
  - Code review and quality assurance

- **Jiaxin Shi**
  - Workout section implementation
  - Workout section backend-frontend integration
  - Implemented workout record entry and fitness tutorial recommendation
  - Code review and quality assurance


---

## Features

- User authentication and secure session management
- Workout logging and personalized recommendations
- Social feed and leaderboard
- Responsive, Jinja2-based frontend
- Data visualization for workout records
- Comprehensive test suite (unit & Selenium)

---

For more details, see the project documentation and code comments.