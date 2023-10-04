# coding=utf-8
import pandas as pd
import datetime
from selenium import webdriver
from bs4 import BeautifulSoup
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait

search_keywords = [
    "junior+data+scientist",
    "junior+data+science",
    "junior+data+analyst",
    "junior+data+analysis",
]
search_url = "https://www.gehalt.de/einkommen/suche/"

# Konfigurieren des Firefox-Browsers
options = FirefoxOptions()
options.add_argument("--headless")
# driver = webdriver.Firefox()
driver = webdriver.Firefox(options=options)
wait = WebDriverWait(driver, 20)
first = True


def next_page():
    global end_reached
    if duplicate_count <= 20 and end_reached is not True:
		# Überprüfen, ob es einen "Next"-Button gibt
        if (
            len(
                driver.find_elements(
                    By.CSS_SELECTOR, ".next.icon.icon--right.chevron-right"
                )
            )
            > 0
        ):
			# Scrollen, um den "Next"-Button sichtbar zu machen
            driver.execute_script(
                "arguments[0].scrollIntoView();",
                driver.find_element(
                    By.CSS_SELECTOR, ".next.icon.icon--right.chevron-right"
                ),
            )
		
		# Überprüfen, ob ein Newsletter-Modal angezeigt wird
        if (
            len(driver.find_elements(By.CSS_SELECTOR, ".jobletter.jobletterModal.show"))
            > 0
        ):
            # Schließe Newsletter-Modal
            driver.find_element(
                By.CSS_SELECTOR, ".simplemodal-close.icon.close"
            ).click()

		# Überprüfen, ob "Next"-Button unverfügbar ist
        if (
            len(
                driver.find_elements(
                    By.CSS_SELECTOR, ".next.icon.icon--right.chevron-right.disabled"
                )
            )
            == 0
        ):
            # Klicke "Next"- Button
            driver.find_element(
                By.CSS_SELECTOR, ".next.icon.icon--right.chevron-right"
            ).click()
        else:
            end_reached = True

# Lese bestehende Daten
jobs_df = pd.read_pickle("../data/jobs.pkl")
ix_jobs = jobs_df.shape[0]

statistics = pd.read_pickle("../data/statistics.pkl")
ix_stats = statistics.shape[0]

# Durchlaufen der Suchbegriffe
for keywords in search_keywords:
    new_entries = 0
    duplicates_found = 0
    duplicate_count = 0
    end_reached = False

    driver.get(search_url + keywords)
	# Überprüfen, ob es einen "Next"-Button gibt
    if (
        len(
            driver.find_elements(
                By.CSS_SELECTOR, ".next.icon.icon--right.chevron-right"
            )
        )
        > 0
    ):
        # Scrollen, um den "Next"-Button sichtbar zu machen
        driver.execute_script(
            "arguments[0].scrollIntoView();",
            driver.find_element(
                By.CSS_SELECTOR, ".next.icon.icon--right.chevron-right"
            ),
        )

	# Beim ersten Durchlauf, Cookie Banner schließen
    if first:
        # Überprüfen, ob es einen Cookie-Banner gibt
        wait.until(
            lambda driver: len(
                driver.find_elements(
                    By.CSS_SELECTOR,
                    "#ccmgt_explicit_preferences.privacy-prompt-button.secondary-button.options-button",
                )
            )
            > 0
        )
        # Klicke ersten Teil des Cookie Banners
        driver.find_element(
            By.CSS_SELECTOR,
            "#ccmgt_explicit_preferences.privacy-prompt-button.secondary-button.options-button",
        ).click()
        
        # Klicke zweiten Teil des Cookie Banners
        wait.until(
            lambda driver: len(
                driver.find_elements(
                    By.CSS_SELECTOR,
                    ".secondary-button.ccmgt_reject_button",
                )
            )
            > 0
        )
        driver.find_element(
            By.CSS_SELECTOR, ".secondary-button.ccmgt_reject_button"
        ).click()
        first = False

	# Wenn Newsletter-Modal, klicken
    if len(driver.find_elements(By.CSS_SELECTOR, ".jobletter.jobletterModal.show")) > 0:
        driver.find_element(By.CSS_SELECTOR, ".simplemodal-close.icon.close").click()

    # Solange suchen, bis genug Duplikate gefunden oder Ende erreicht ist
    while duplicate_count < 20 and end_reached is not True:
        response = driver.page_source
        soup_object = BeautifulSoup(response, features="lxml")

        joblist_container = soup_object.find_all(
            id="joblist", class_="joblist copy-default"
        )[0]
        joblist = joblist_container.find_all("li", attrs={"data-hidesalarydata": True})

        for job in joblist:
            link = job.find(class_="jobListLink")["href"]
            job_id = job.find(class_="jobListLink")["href"].split("jobId=")[1]
            titel = job.find(class_="text title textlink-default").text
            unternehmen = job.find(class_="company").text
            ort = job.find(class_="location textlink-default").text
            datum = datetime.datetime.now().strftime("%Y-%m-%d")
            if job.find(class_="salary month textlink-default") is not None:
                gehalt_min = (
                    job.find(class_="salary month textlink-default")
                    .text.split(" – ")[0]
                    .replace(".", "")
                )
                gehalt_max = (
                    job.find(class_="salary month textlink-default")
                    .text.split(" – ")[1]
                    .replace(".", "")
                )
            else:
                gehalt_min = ""
                gehalt_max = ""
            if ~jobs_df["JobID"].isin([job_id]).any():
                jobs_df.loc[
                    ix_jobs,
                    [
                        "Titel",
                        "Unternehmen",
                        "Ort",
                        "Gehalt_min",
                        "Gehalt_max",
                        "JobID",
                        "Link",
                        "Datum",
                    ],
                ] = [
                    titel,
                    unternehmen,
                    ort,
                    gehalt_min,
                    gehalt_max,
                    job_id,
                    link,
                    datum,
                ]
                ix_jobs += 1
                duplicate_count = 0
                new_entries += 1
            else:
                duplicate_count += 1
                duplicates_found += 1

        next_page()

    statistics.loc[ix_stats, ["Date", keywords]] = [
        datetime.datetime.now().strftime("%d.%m.%Y"),
        new_entries,
    ]

driver.quit()

jobs_df.to_pickle("../data/jobs.pkl")
statistics.to_pickle("../data/statistics.pkl")
