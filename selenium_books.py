from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import csv

service = Service(executable_path="chromedriver.exe")

def scrape_books_to_scrape():
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--window-size=1920,1080")

    driver = webdriver.Chrome(options=chrome_options)

    output_file = "scraped_books.csv"

    with open(output_file, mode='w', newline='', encoding='utf-8') as file:
        writer = csv.writer(file)
        writer.writerow(['Title', 'Price', 'Rating', 'Availability', 'Category', 'Page URL'])

    try:
        base_url = "http://books.toscrape.com/catalogue/page-{}.html"
        page_number = 1
        max_pages = 5

        while page_number <= max_pages:
            current_url = base_url.format(page_number)
            print(f"Scraping page: {current_url}")

            driver.get(current_url)

            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.CLASS_NAME, "product_pod"))
            )

            books = driver.find_elements(By.CLASS_NAME, "product_pod")
            page_data = []

            for book in books:
                try:
                    title = book.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a").get_attribute("title")
                    price = book.find_element(By.CLASS_NAME, "price_color").text
                    rating_element = book.find_element(By.CLASS_NAME, "star-rating")
                    rating = rating_element.get_attribute("class").split()[1]
                    availability = book.find_element(By.CLASS_NAME, "availability").text.strip()
                    detail_url = book.find_element(By.TAG_NAME, "h3").find_element(By.TAG_NAME, "a").get_attribute("href")

                    driver.execute_script("window.open('');")
                    driver.switch_to.window(driver.window_handles[1])
                    driver.get(detail_url)

                    breadcrumbs = driver.find_elements(By.CLASS_NAME, "breadcrumb")
                    category = breadcrumbs[0].find_elements(By.TAG_NAME, "li")[2].text.strip()

                    driver.close()
                    driver.switch_to.window(driver.window_handles[0])

                    page_data.append([title, price, rating, availability, category, detail_url])

                except Exception as e:
                    print(f"Error processing a book: {e}")
                    continue

            with open(output_file, mode='a', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                writer.writerows(page_data)

            print(f"Saved {len(page_data)} books from page {page_number}")
            page_number += 1
            time.sleep(2)

    except Exception as e:
        print(f"Error during scraping: {e}")
    finally:
        driver.quit()
        print(f"Scraping completed. Results saved to {output_file}")

if __name__ == "__main__":
    scrape_books_to_scrape()
