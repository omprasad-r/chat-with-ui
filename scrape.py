# import requests
# import re
# from bs4 import BeautifulSoup
# from selenium import webdriver
# import time
 

# options = webdriver.ChromeOptions()
# options.add_argument('--ignore-certificate-errors')
# options.add_argument('--incognito')
# options.add_argument('--headless')
# driver = webdriver.Chrome(options=options)

# #URL = "https://www.keurig.com/smart+coffee+makers/c/smart101?cm_sp=smart+coffee+makers-_-Top-Nav-_-smart101"

# def scrape_url(url):
#   driver.get(URL)

#   ##more_buttons = driver.find_elements_by_class_name("moreLink")

#   ##for x in range(len(more_buttons)):
#   ##  if more_buttons[x].is_displayed():
#   ##      driver.execute_script("arguments[0].click();", more_buttons[x])
#   ##      time.sleep(1)

#   time.sleep(3)
#   page_source = driver.page_source
#   headers = requests.utils.default_headers()
#   elem = BeautifulSoup(page_source, "html.parser")
#   text = ''

#   for e in elem.descendants:
#     if isinstance(e, str):
#       name = e.strip()
#       pattern = re.compile("\{")
#       match = re.search(pattern, name)
#       if match:
#           n = 1
#       else:
#           text += e.strip()
#     elif e.name in ['br',  'p', 'h1', 'h2', 'h3', 'h4','tr', 'th']:
#       text += '\n'
#     elif e.name == 'li':
#       text += '\n '

#   print(text)