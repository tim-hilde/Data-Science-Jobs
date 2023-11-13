# Readme
Dieses Repository enhtält sowohl gesammelte Daten von Jobangeboten im Data Science und Analysis Bereich als auch deren Auswertung

## Data Collection
Die Daten wurden mit Hilfe von Skripten generiert, die nach Jobpostings auf [gehalt.de](gehalt.de) unter den Schlagworten "junior+data+scientist", "junior+data+science", "junior+data+analyst" und "junior+data+analysis" suchen. Dafür wird die Webseite mit [Selenium](https://www.selenium.dev) geöffnet und alle Jobspostings gescraped, bis genug bekannte Einträge gesammelt wurden, sodass sichergestellt werden kann, alle neuen Einträge gespeichert wurden. Anschließend werden die Inhalte der Jobangebote gescraped. Auch das funktioniert über [Selenium](https://www.selenium.dev) und anschließend mit [BeautifulSoup](https://beautiful-soup-4.readthedocs.io/en/latest/#). Insgesamt werden so Titel, Unternehmen, Ort, die von gehalt.de prognostizierte Gehaltsbereiche, Informationen zu Teilzeit- und Remotemöglichkeit, sowie den gesamten Text der Stellenausschreibunge gespeichert.

## Analyse
Die Auswertung der Daten wurde mit [pandas](https://pandas.pydata.org) durchgeführt. Darstellungen wurden mit [Matplotlib](https://matplotlib.org) und [Seaborn](https://seaborn.pydata.org) erstellt. Eine Geo-Analyse wurde mit [Geopandas](https://geopandas.org) mit Daten vom [Regionalatlas](https://regionalatlas.statistikportal.de/#) und [opendatasoft](https://public.opendatasoft.com/explore/dataset/georef-germany-postleitzahl) durchgeführt.

Die Analyse ist [hier](https://github.com/tim-hilde/Data-Science-Jobs/blob/main/notebooks/02-Analysis.ipynb) zu finden.