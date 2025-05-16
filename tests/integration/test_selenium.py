import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException

class TestWebApp(unittest.TestCase):
    def setUp(self):
        from selenium.webdriver.chrome.service import Service
        from webdriver_manager.chrome import ChromeDriverManager
        from selenium.webdriver.chrome.options import Options
        
        chrome_options = Options()
        chrome_options.add_argument('--no-sandbox')
        chrome_options.add_argument('--disable-dev-shm-usage')
        chrome_options.add_argument('--window-size=1920,1080')
        chrome_options.add_argument('--start-maximized')
        chrome_options.add_experimental_option('detach', True)
        
        service = Service(ChromeDriverManager().install())
        self.driver = webdriver.Chrome(service=service, options=chrome_options)
        self.driver.implicitly_wait(20)  # 增加等待时间
        self.base_url = "http://127.0.0.1:5000"
        
        # 确保 Flask 服务器正在运行
        try:
            self.driver.get(self.base_url)
        except Exception as e:
            print("请确保 Flask 服务器正在运行于端口 5000")
            raise e

    def tearDown(self):
        self.driver.quit()

    def test_login_page(self):
        """测试登录页面加载"""
        self.driver.get(f"{self.base_url}/login_system/login.html")
        try:
            # 使用更灵活的元素定位策略
            username_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='text'], input[name='username']"))
            )
            password_field = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "input[type='password'], input[name='password']"))
            )
            login_button = WebDriverWait(self.driver, 20).until(
                EC.presence_of_element_located((By.CSS_SELECTOR, "button[type='submit'], #login-button, .login-button"))
            )
            
            # 截图以便调试
            self.driver.save_screenshot('login_page_test.png')
            
            self.assertTrue(username_field.is_displayed())
            self.assertTrue(password_field.is_displayed())
            self.assertTrue(login_button.is_displayed())
        except TimeoutException as e:
            self.driver.save_screenshot('login_page_error.png')
            self.fail(f"登录页面元素未找到: {str(e)}")

    def test_successful_login(self):
        """测试成功登录"""
        self.driver.get(f"{self.base_url}/login_system/login.html")
        try:
            username = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password = self.driver.find_element(By.NAME, "password")
            
            username.send_keys("testuser")
            password.send_keys("password123")
            
            login_button = self.driver.find_element(By.ID, "login-button")
            login_button.click()
            
            # 等待重定向到主页
            WebDriverWait(self.driver, 10).until(
                EC.url_to_be(f"{self.base_url}/main.html")
            )
        except TimeoutException:
            self.fail("登录失败或重定向超时")

    def test_failed_login(self):
        """测试登录失败"""
        self.driver.get(f"{self.base_url}/login_system/login.html")
        try:
            username = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.NAME, "username"))
            )
            password = self.driver.find_element(By.NAME, "password")
            
            username.send_keys("wrong")
            password.send_keys("wrong")
            
            login_button = self.driver.find_element(By.ID, "login-button")
            login_button.click()
            
            # 检查错误消息
            error_message = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "error-message"))
            )
            self.assertTrue(error_message.is_displayed())
        except TimeoutException:
            self.fail("错误消息未显示")

    def test_workout_recording(self):
        """测试运动记录功能"""
        # 先登录
        self.test_successful_login()
        
        try:
            # 导航到运动记录页面
            self.driver.get(f"{self.base_url}/workout_page/log.html")
            
            # 等待并填写表单
            activity = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.ID, "activity"))
            )
            duration = self.driver.find_element(By.ID, "duration")
            
            activity.send_keys("Running")
            duration.send_keys("30")
            
            submit = self.driver.find_element(By.ID, "submit-workout")
            submit.click()
            
            # 验证成功消息
            success = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "success-message"))
            )
            self.assertTrue(success.is_displayed())
        except TimeoutException:
            self.fail("运动记录表单元素未找到")

    def test_view_statistics(self):
        """测试查看统计信息"""
        # 先登录
        self.test_successful_login()
        
        try:
            # 导航到统计页面
            self.driver.get(f"{self.base_url}/record.html")
            
            # 等待统计卡片加载
            stats = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "metrics-cards"))
            )
            self.assertTrue(stats.is_displayed())
            
            # 检查图表是否存在
            charts = self.driver.find_elements(By.CLASS_NAME, "chart-item")
            self.assertTrue(len(charts) > 0)
        except TimeoutException:
            self.fail("统计信息未加载")

if __name__ == "__main__":
    unittest.main()