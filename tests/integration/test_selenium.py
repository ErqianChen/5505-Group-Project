import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os

class TestWebApp(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Use Chrome in headless mode
        options = webdriver.ChromeOptions()
        options.add_argument('--headless')
        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(10)
        # Assuming the app is running on localhost:5000
        cls.base_url = "http://localhost:5000"

    @classmethod
    def tearDownClass(cls):
        cls.driver.quit()

    def test_login_page(self):
        """Test login page elements and functionality"""
        self.driver.get(f"{self.base_url}/")
        
        # Check for login form elements
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.ID, "login-button")
        
        self.assertTrue(username_input.is_displayed())
        self.assertTrue(password_input.is_displayed())
        self.assertTrue(login_button.is_displayed())

    def test_successful_login(self):
        """Test successful login flow"""
        self.driver.get(f"{self.base_url}/")
        
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.ID, "login-button")
        
        username_input.send_keys("taylor_swift")
        password_input.send_keys("password")
        login_button.click()
        
        # Wait for main page to load
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "dashboard"))
        )
        
        # Verify we're on the main page
        self.assertIn("dashboard", self.driver.current_url)

    def test_failed_login(self):
        """Test login with invalid credentials"""
        self.driver.get(f"{self.base_url}/")
        
        username_input = self.driver.find_element(By.NAME, "username")
        password_input = self.driver.find_element(By.NAME, "password")
        login_button = self.driver.find_element(By.ID, "login-button")
        
        username_input.send_keys("invalid_user")
        password_input.send_keys("wrong_password")
        login_button.click()
        
        # Wait for error message
        error_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
        )
        
        self.assertTrue(error_message.is_displayed())

    def test_workout_recording(self):
        """Test recording a new workout"""
        # First login
        self.test_successful_login()
        
        # Navigate to workout recording page
        add_workout_btn = self.driver.find_element(By.ID, "add-workout-button")
        add_workout_btn.click()
        
        # Fill in workout details
        category_select = self.driver.find_element(By.NAME, "category")
        duration_input = self.driver.find_element(By.NAME, "duration")
        difficulty_input = self.driver.find_element(By.NAME, "difficulty")
        submit_button = self.driver.find_element(By.ID, "submit-workout")
        
        category_select.send_keys("Running")
        duration_input.send_keys("30")
        difficulty_input.send_keys("3")
        submit_button.click()
        
        # Verify success message
        success_message = WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
        )
        self.assertTrue(success_message.is_displayed())

    def test_view_statistics(self):
        """Test viewing workout statistics"""
        # First login
        self.test_successful_login()
        
        # Navigate to statistics page
        stats_link = self.driver.find_element(By.ID, "stats-link")
        stats_link.click()
        
        # Verify statistics elements are present
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.CLASS_NAME, "stats-container"))
        )
        
        streak_element = self.driver.find_element(By.ID, "current-streak")
        calories_element = self.driver.find_element(By.ID, "total-calories")
        hours_element = self.driver.find_element(By.ID, "total-hours")
        
        self.assertTrue(streak_element.is_displayed())
        self.assertTrue(calories_element.is_displayed())
        self.assertTrue(hours_element.is_displayed())