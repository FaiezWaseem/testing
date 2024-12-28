import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class GoogleLinkedinProfileScraper:
    def __init__(self, keyword, country, max_pages=5):
        self.keyword = keyword
        self.country = country
        self.max_pages = max_pages
        self.profile_links = []
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
        
        # Create the Google search query
        self.google_search_url = f'https://www.google.com/search?q=site%3Alinkedin.com%2Fin%20%22{self.keyword}%22%20AND%20%22{self.country}%22%20%28%22email%22%20OR%20%22%2A%40gmail.com%22%20OR%20%22%2A%40yahoo.com%22%20OR%20%22%2A%40hotmail.com%22%29%20%28%22phone%22%20OR%20%22contact%22%20OR%20%22mobile%22%20OR%20%22tel%3A%22%29'
    
    def start(self):
        # Visit Google Search with the query
        self.driver.get(self.google_search_url)
        time.sleep(3)  # Wait for the page to load

        # Scrape the first page
        self.scrape_profiles()

        # Scrape subsequent pages
        current_page = 1
        while current_page < self.max_pages:
            print(f"Scraping page {current_page}...")
            
            # Scrape profiles on the current page
            self.scrape_profiles()

            # Go to the next page
            if not self.go_to_next_page():
                print("No more pages to scrape.")
                break

            current_page += 1

        self.driver.quit()
        # Save profiles to a JSON file
        self.save_profiles()
        
        return self.profile_links


    def scrape_profiles(self):
        # Extract all profile links from the search results on the current page
        results = self.driver.find_elements(By.CSS_SELECTOR, 'div.g')
        for result in results:
            try:
                link = result.find_element(By.TAG_NAME, 'a')
                href = link.get_attribute('href')
                if 'linkedin.com/in/' in href:  # Ensure it is a LinkedIn profile URL
                    self.profile_links.append(href)
            except Exception as e:
                print(f"Error while extracting link: {e}")
    
    def go_to_next_page(self):
        try:
            # Wait until the "Next" button is clickable and click it using the correct XPath
            next_button = WebDriverWait(self.driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, '//a[@id="pnnext"]'))
            )
            next_button.click()
            time.sleep(3)  # Wait for the page to load
            return True
        except Exception as e:
            print(f"Error navigating to next page: {e}")
            return False
    
    def save_profiles(self):
        # Save the profile links to a JSON file
        with open(f'linkedin_profiles_{self.keyword}_{self.country}.json', 'w') as file:
            json.dump(self.profile_links, file, indent=4)
        print(f"Found {len(self.profile_links)} profiles and saved to linkedin_profiles_{self.keyword}_{self.country}.json")

# Example Usage:
if __name__ == "__main__":
    keyword = input("Enter the job title/keyword: ")
    country = input("Enter the country: ")
    max_page = int(input("Enter the number of pages to scrape: "))

    # Scrape Google search results for LinkedIn profiles
    scraper = GoogleLinkedinProfileScraper(keyword, country , max_pages=max_page)
    profile_links = scraper.start()
    with open(f'./users/{keyword}_{country}_linkedin_profiles_links__from_google.json', 'w') as file:
        json.dump(profile_links, file, indent=4)

