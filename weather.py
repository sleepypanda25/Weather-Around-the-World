from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.common.by import By
import pandas as pd
import csv
import sqlalchemy as sa

driver = webdriver.Chrome(service=ChromeService(ChromeDriverManager().install()))

try:
    # --- Web Scraping ---
    driver.get("https://www.timeanddate.com/weather/")

    table = driver.find_element(By.CSS_SELECTOR, 'table.zebra.fw.tb-theme')
    rows = table.find_elements(By.CSS_SELECTOR, 'tr')

    data = []

    # Traverse rows of table
    for row in rows:
        # Collect all cities, date/time, and temperatures in that row
        cities = [city.text for city in row.find_elements(By.CSS_SELECTOR, 'a')]
        dates_times = [date_time.text for date_time in row.find_elements(By.CSS_SELECTOR, 'td[id^="p"]')]
        temperatures = [temperature.text for temperature in row.find_elements(By.CSS_SELECTOR, 'td.rbi')]

        # Separate data for each city
        for i in range(len(cities)):
            city = cities[i]
            date_time = dates_times[i]
            temperature = temperatures[i]

            entry = {"City": city, "Date/Time": date_time, "Temperature": temperature}

            data.append(entry)

    print(data)

    # Write raw data into weather.csv file
    with open('weather.csv', 'w') as file:
        writer = csv.writer(file)

        for entry in data:
            writer.writerow([entry['City'], entry['Date/Time'], entry['Temperature']])

    # --- Data Cleaning & Transformation ---
    df = pd.DataFrame(data)
    print("Before", df.head())

    # Confirmed no null entries
    # Date/Time entries will remain strings since only the date of the week is in
    # in the entry value, not the date
    print(df.info())

    # Sort entries by alphabetical order of cities
    df.sort_values(by='City', ascending=True, inplace=True)
    df.reset_index(inplace=True, drop=True)

    # Check for duplicates (not really necessary since data is directly from website
    # and I can guarantee entries are unique, but done as an extra precaution)
    print("\nDuplicates: ", df.duplicated().sum())

    print("After: ", df.head())

    # Make Sqlite database
    engine = sa.create_engine('sqlite:///weather.db')

    df.to_sql('weather', engine, if_exists='append', index=False)
except Exception as e:
    print(e)
finally:
    driver.quit()