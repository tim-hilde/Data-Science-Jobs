# coding=utf-8
import pandas as pd
from selenium import webdriver
from selenium.webdriver.firefox.options import Options as FirefoxOptions
from bs4 import BeautifulSoup
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException

# Konfigurieren des Firefox-Browsers
options = FirefoxOptions()
options.add_argument("--headless")


# Funktion zum Hinzufügen von Informationen zu einem Job-Link
def add_info(url):
    global first
    driver.get(url)
    wait = WebDriverWait(driver, 20)

    # Überprüfen, ob die URL von gehalt.de ist
    if "gehalt.de" in url:
        try:
            wait.until(lambda driver: driver.current_url != url)
        except TimeoutException:
            print("Fehlerhafter Link: {}".format(url))
    link = driver.current_url
    if "stepstone.de" not in link:
        return (
            link,
            "Nicht stepstone",
            "Nicht stepstone",
            "Nicht stepstone",
            "Nicht stepstone",
            "Nicht stepstone",
            "Nicht stepstone",
        )

    # Beim ersten Durchlauf, Cookie Banner schließen
    if first:
        # Sicherstellen, dass es einen Cookie-Banner gibt
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
    # Überprüfen, dass alle Elemente des Texts verfügbar sind
    if len(driver.find_elements(By.CLASS_NAME, "listing-content-provider-hw0nf9")) > 0:
        driver.find_element(By.CLASS_NAME, "listing-content-provider-hw0nf9").click()

    response = driver.page_source
    soup_object = BeautifulSoup(response, features="lxml")
    # Wenn Stellenanzeige nicht mehr verfügbar ist
    if len(soup_object.find_all(attrs={"data-genesis-element": "ALERT_CONTENT"})) > 0:
        return (
            link,
            "Stellenanzeige nicht mehr verfügbar",
            "Stellenanzeige nicht mehr verfügbar",
            "Stellenanzeige nicht mehr verfügbar",
            "Stellenanzeige nicht mehr verfügbar",
            "Stellenanzeige nicht mehr verfügbar",
            "Stellenanzeige nicht mehr verfügbar",
        )
    # Teilzeit und Remote
    if len(soup_object.find_all(class_="at-listing__list-icons_work-type")) > 0:
        work_type = soup_object.find(class_="at-listing__list-icons_work-type").find(
            attrs={"data-genesis-element": "TEXT"}
        )
        teilzeit_remote = work_type.text
    else:
        teilzeit_remote = "-"

    # Informationstexte auslesen
    base = soup_object.find_all("div", class_="sc-EHOje jWEhHL")

    texts = ["", "", "", "", ""]

    for i in range(len(base)):
        area = base[i].find_all(["p", "li"])
        for element in area:
            texts[i] += element.text

    return link, teilzeit_remote, texts[0], texts[1], texts[2], texts[3], texts[4]


jobs = pd.read_pickle("../data/jobs.pkl")

jobs_new = jobs[jobs["Teilzeit_Remote"].isna()]
index_new = jobs_new.index
print(f"Adding info for {jobs_new.shape[0]} jobs.")
with webdriver.Firefox(options=options) as driver:
    first = True
    for i in index_new:
        jobs.loc[
            i,
            [
                "Link",
                "Teilzeit_Remote",
                "Introduction",
                "Description",
                "Profile",
                "We_offer",
                "Contact",
            ],
        ] = add_info(jobs_new.loc[i, "Link"])
        jobs.to_pickle("../data/jobs.pkl")

    jobs_error = jobs[(jobs["Teilzeit_Remote"] == "-") & (jobs["Introduction"] == "")]
    round = 0
    while len(jobs_error) > 0 and round < 3:
        print(f"Reducing {len(jobs_error)} error jobs")
        index_err = jobs_error.index
        for i in index_err:
            jobs.loc[
                i,
                [
                    "Link",
                    "Teilzeit_Remote",
                    "Introduction",
                    "Description",
                    "Profile",
                    "We_offer",
                    "Contact",
                ],
            ] = add_info(jobs_error.loc[i, "Link"])
        jobs_error = jobs[
            (jobs["Teilzeit_Remote"] == "-") & (jobs["Introduction"] == "")
        ]
        jobs.to_pickle("../data/jobs.pkl")
        round += 1
