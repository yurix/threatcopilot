import argparse
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from io import BytesIO
import time
from selenium.webdriver.common.by import By
start_time = time.time()

options = webdriver.ChromeOptions()
options.add_argument("start-maximized")
options.add_argument("--headless")
options.add_argument("--no-sandbox")
options.add_argument("--disable-gpu")

options.add_argument("--disable-dev-shm-usage") #should be enabled for Jenkins
       
options.add_experimental_option("excludeSwitches", ["enable-automation"])
options.add_experimental_option('useAutomationExtension', False)
driver = webdriver.Chrome(service=ChromeService(executable_path='/usr/bin/chromedriver'), options=options)

def main():
    print(f'Instalando o ChromeDriver ')
    #
    driver.get('http://localhost:5005/threatmodel/br.gov.inss.atestado/dfd')
    time.sleep(3)
    width = 1920
    web_page_height = driver.execute_script('return Math.max(document.body.scrollHeight, document.body.offsetHeight, document.documentElement.clientHeight, document.documentElement.scrollHeight, document.documentElement.offsetHeight);')
    print (web_page_height)
    driver.set_window_size(width,web_page_height)
    body = driver.find_element(By.TAG_NAME,'body')
    body.screenshot('teste.png')
    #dfdpng = driver.save_screenshot('teste.png')
    driver.quit()
    elapsed = "%s seconds" % (time.time() - start_time)
    print("Done in " + elapsed)
    print(f'Encerrado.')

if __name__ == "__main__":
    main()