<<<<<<< Updated upstream
# CITS5505-Group10-Project
# TrainTogether

A full-stack fitness tracking web application built with Flask, designed to help users stay motivated and empowers users to log, track, and visualize their workout activities, while also socilize with each other.

It allows users to:
- Watch categorized **workout tutorial** videos (cardio & strength)
- **Log workout data** details such as sport category, duration, and intensity
- View personal progress through **dynamic visualizations**
- Engage with other users in the platform through **social** functions

---
Team Members   

|  UWA Id   | Name  | GitHub |
|  :----:  | :----:  | :----:  |
| 23941282  | Jiasen Niu |[JiasenNiu-Max](https://github.com/JiasenNiu-Max) |
| 23895698  | Jiaxin Shi |[shijarrr](https://github.com/shijarrr) |
| 24009963  | Harry Zhu |[Harryzmh02](https://github.com/Harryzmh02)|
| 23421379  | Erqian Chen |[ErqianChen](https://github.com/ErqianChen)|

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
   del app.db
   python init_db.py
   ```
   The database will be available as app.db.


5. **Run the application:**
   ```
   python app.py
   ```
   The app will be available at `http://127.0.0.1:5000/`.

6. **Run the tests:**

### Unit Tests

All Python unit tests are named `test_*.py` and are located in the project root or in the `tests/` directory.  
To run all unit tests, simply execute:

```bash
pytest
```

Or to run a specific test file:

```bash
pytest tests/test_example.py
```

### Selenium Tests

Selenium tests are used for automated end-to-end browser testing. Before running, make sure:

- Selenium and all dependencies are installed (`pip install -r requirements.txt`)
- The appropriate WebDriver (e.g., ChromeDriver) is installed and available in your PATH

To run all Selenium tests:

```bash
pytest tests/selenium/
```

Or to run a specific Selenium test file:

```bash
pytest tests/selenium/test_login.py
```

**Note:**
- It is recommended to start the Flask application server (`python app.py`) before running Selenium tests.
- Selenium tests will open a browser window automatically. Please do not interact with the browser during the test.

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
  - Blueprints & CSRF token setup

- **Jiasen Niu** 

  - Social section implementation: posts, likes, comments, bookmarks
  - Test suite development (unit & Selenium tests)
  - initial data migration and admin user seeding script
  - Function debugging
  - Code review and css style refine

- **Jiaxin Shi** 

  - Workout section subpages implementation
  - Backend-frontend integration, database linkage with logic design
  - Implemented workout data record entry and fitness tutorial recommendation
  - Function debugging
  - Code review and css style refine




---

## Features

- **Valid, well-structured HTML**: All pages use valid HTML, a wide range of semantic elements, and are organized with Jinja2 templates for maintainability and clarity.
- **Responsive, maintainable CSS**: Custom selectors and classes ensure a modern, visually appealing, and fully responsive design across devices.
- **Modern JavaScript**: Includes client-side validation, DOM manipulation, and AJAX, following best practices for code quality and user experience.
- **Intuitive navigation & strong design**: The website offers a clear navigation flow, strong visual identity, and a user-centered experience with clear value.
- **Comprehensive functionality**: All features from the project brief are fully implemented, including user authentication, workout logging, social feed, leaderboard, and personalized recommendations.
- **Well-organized Flask backend**: Modular codebase using Blueprints, with clear routing, robust data manipulation, and dynamic page generation.
- **Robust data models**: Carefully designed database schema, secure authentication, and maintainable models, with evidence of database migrations.
- **Thorough testing**: Includes unit tests and Selenium tests, covering both backend logic and live server interactions.
- **Strong security**: Passwords are securely hashed and salted, CSRF tokens protect all forms, and sensitive configuration uses environment variables.


---

For more details, see the project documentation and code comments.
=======
# CITS5505-Group10-Project
# TrainTogether

A full-stack fitness tracking web application built with Flask, designed to help users stay motivated and empowers users to log, track, and visualize their workout activities, while also socilize with each other.

It allows users to:
- Watch categorized **workout tutorial** videos (cardio & strength)
- **Log workout data** details such as sport category, duration, and intensity
- View personal progress through **dynamic visualizations**
- Engage with other users in the platform through **social** functions

---
Team Members   

|  UWA Id   | Name  | GitHub |
|  :----:  | :----:  | :----:  |
| 23941282  | Jiasen Niu |[JiasenNiu-Max](https://github.com/JiasenNiu-Max) |
| 23895698  | Jiaxin Shi |[shijarrr](https://github.com/shijarrr) |
| 24009963  | Harry Zhu |[Harryzmh02](https://github.com/Harryzmh02)|
| 23421379  | Erqian Chen |[ErqianChen](https://github.com/ErqianChen)|

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

6. **Run the tests:**

### Unit Tests

All Python unit tests are named `test_*.py` and are located in the project root or in the `tests/` directory.  
To run all unit tests, simply execute:

```bash
pytest
```

Or to run a specific test file:

```bash
pytest tests/test_example.py
```

### Selenium Tests

Selenium tests are used for automated end-to-end browser testing. Before running, make sure:

- Selenium and all dependencies are installed (`pip install -r requirements.txt`)
- The appropriate WebDriver (e.g., ChromeDriver) is installed and available in your PATH

To run all Selenium tests:

```bash
pytest tests/selenium/
```

Or to run a specific Selenium test file:

```bash
pytest tests/selenium/test_login.py
```

**Note:**
- It is recommended to start the Flask application server (`python app.py`) before running Selenium tests.
- Selenium tests will open a browser window automatically. Please do not interact with the browser during the test.

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
  - Blueprints & CSRF token setup

- **Jiasen Niu** 

  - Social section implementation: posts, likes, comments, bookmarks
  - Test suite development (unit & Selenium tests)
  - initial data migration and admin user seeding script
  - Function debugging
  - Code review and css style refine

- **Jiaxin Shi** 

  - Workout section subpages implementation
  - Backend-frontend integration, database linkage with logic design
  - Implemented workout data record entry and fitness tutorial recommendation
  - Function debugging
  - Code review and css style refine




---

## Features

- **Valid, well-structured HTML**: All pages use valid HTML, a wide range of semantic elements, and are organized with Jinja2 templates for maintainability and clarity.
- **Responsive, maintainable CSS**: Custom selectors and classes ensure a modern, visually appealing, and fully responsive design across devices.
- **Modern JavaScript**: Includes client-side validation, DOM manipulation, and AJAX, following best practices for code quality and user experience.
- **Intuitive navigation & strong design**: The website offers a clear navigation flow, strong visual identity, and a user-centered experience with clear value.
- **Comprehensive functionality**: All features from the project brief are fully implemented, including user authentication, workout logging, social feed, leaderboard, and personalized recommendations.
- **Well-organized Flask backend**: Modular codebase using Blueprints, with clear routing, robust data manipulation, and dynamic page generation.
- **Robust data models**: Carefully designed database schema, secure authentication, and maintainable models, with evidence of database migrations.
- **Thorough testing**: Includes unit tests and Selenium tests, covering both backend logic and live server interactions.
- **Strong security**: Passwords are securely hashed and salted, CSRF tokens protect all forms, and sensitive configuration uses environment variables.


---

For more details, see the project documentation and code comments.
>>>>>>> Stashed changes
