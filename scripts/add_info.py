# coding=utf-8
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

options = FirefoxOptions()
options.add_argument("--headless")
driver = webdriver.Firefox(options=options)
# driver = webdriver.Firefox()

first = True
def add_info(url):
	global first
	driver.get(url)
	wait = WebDriverWait(driver, 20)
	if "gehalt.de" in url:
		wait.until(lambda driver: driver.current_url != url)
	link = driver.current_url
	if "stepstone.de" not in link:
		return(link, 
				"Nicht stepstone",
				"Nicht stepstone",
				"Nicht stepstone",
				"Nicht stepstone",
				"Nicht stepstone",
				"Nicht stepstone",)
	# print(link)
	if first:
		wait.until(lambda driver: len(driver.find_elements(By.CSS_SELECTOR, "#ccmgt_explicit_preferences.privacy-prompt-button.secondary-button.options-button")) > 0)
		driver.find_element(By.CSS_SELECTOR, "#ccmgt_explicit_preferences.privacy-prompt-button.secondary-button.options-button").click()
		driver.find_element(By.CSS_SELECTOR, ".secondary-button.ccmgt_reject_button").click()
		first = False

	if len(driver.find_elements(By.CLASS_NAME, "listing-content-provider-hw0nf9")) > 0:
		driver.find_element(By.CLASS_NAME, "listing-content-provider-hw0nf9").click()
	
	response = driver.page_source
	soup_object = BeautifulSoup(response, features="lxml")
	if len(soup_object.find_all(attrs={"data-genesis-element":"ALERT_CONTENT"})) > 0:
		return(link, 
				"Stellenanzeige nicht mehr verfügbar", 
				"Stellenanzeige nicht mehr verfügbar", 
				"Stellenanzeige nicht mehr verfügbar", 
				"Stellenanzeige nicht mehr verfügbar", 
				"Stellenanzeige nicht mehr verfügbar", 
				"Stellenanzeige nicht mehr verfügbar")
	# Teilzeit und Remote
	if len(soup_object.find_all(class_="at-listing__list-icons_work-type")) > 0:
		work_type = soup_object.find(class_="at-listing__list-icons_work-type").find(attrs={"data-genesis-element":"TEXT"})
		# # print(soup_object)
		# print(work_type)
		teilzeit_remote = work_type.text
	else:
		teilzeit_remote = "-"

	base = soup_object.find_all("div", class_="sc-EHOje jWEhHL")

	texts = ["", "", "", "", ""]

	for i in range(len(base)):
		area = base[i].find_all(["p", "li"])
		for element in area:
			texts[i] += element.text + "\n"

	return link, teilzeit_remote, texts[0], texts[1], texts[2], texts[3], texts[4]

jobs = pd.read_pickle("../data/jobs.pkl")

jobs_new = jobs[jobs["Teilzeit_Remote"].isna() == True]

index_new = jobs_new.index
for i in index_new:
	jobs.loc[i, ["Link", "Teilzeit_Remote", "Introduction", "Description", "Profile", "We_offer", "Contact"]] = add_info(jobs_new.loc[i, "Link"])

jobs_error = jobs[(jobs["Teilzeit_Remote"] == "-") & (jobs["Introduction"] == "")]

while len(jobs_error) > 0:
	index_err = jobs_error.index
	for i in index_err:
			jobs.loc[i, ["Link", "Teilzeit_Remote", "Introduction", "Description", "Profile", "We_offer", "Contact"]] = add_info(jobs_error.loc[i, "Link"])
	jobs_error = jobs[(jobs["Teilzeit_Remote"] == "-") & (jobs["Introduction"] == "")]


jobs.to_pickle("../data/jobs.pkl")
driver.quit()