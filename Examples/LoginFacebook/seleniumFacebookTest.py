from selenium import webdriver
from selenium.webdriver.common.keys import Keys

user = "gauravleekha@gmail.com"
pwd = ""

driver = webdriver.Chrome()
driver.get("http://www.facebook.com")
assert "Facebook" in driver.title
element = driver.find_element_by_id("email")
element.send_keys(user)
element = driver.find_element_by_id("pass")
element.send_keys(pwd)
element.send_keys(Keys.RETURN)