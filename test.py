import time
import json
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

class LinkedInScraper:
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

        # Save profiles to a JSON file
        self.save_profiles()

        # Close the WebDriver
        self.driver.quit()

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

# Separate class for scraping LinkedIn profile details
class LinkedInProfileScraper:
    def __init__(self, profile_url):
        self.profile_url = profile_url
        self.driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))

    def scrape_profile_data(self , keyword , country):
        # Visit the LinkedIn profile URL
        self.driver.get(self.profile_url)
        time.sleep(6)  # Wait for the page to load
        
        # Extract the required information
        profile_data = {
            "name": self.get_name(),
            "location": self.get_location(),
            "education": self.get_education(),
            "experience": self.get_experience(),
            "link" : self.profile_url,
            "keyword" : keyword,
            "country": country
        }
        print(profile_data)

        # Close the WebDriver
        self.driver.quit()

        return profile_data

    def get_name(self):
        try:
            name_element = self.driver.find_element(By.CSS_SELECTOR, 'h1.top-card-layout__title')
            return name_element.text.strip()
        except Exception as e:
            print(f"Error extracting name: {e}")
            return None

    def get_location(self):
        try:
            location_element = self.driver.find_element(By.CSS_SELECTOR, 'div.not-first-middot')
            return location_element.text.strip()
        except Exception as e:
            print(f"Error extracting location: {e}")
            return None

    def get_education(self):
        education = []
        try:
            education_section = self.driver.find_element(By.XPATH, '//section[@data-section="educationsDetails"]')
            education_items = education_section.find_elements(By.XPATH, './/li')
            for item in education_items:
                print(f"Experience Item Content: {item.text.strip()}")
                school = item.find_element(By.XPATH, './/h3').text.strip()
                degree = item.find_element(By.XPATH, './/h4').text.strip()
                education.append({"school": school, "degree": degree})
        except Exception as e:
            print(f"Error extracting education: {e}")
        return education

    def get_experience(self):
        experience = []
        try:
            experience_section = self.driver.find_element(By.XPATH, '//section[contains(@data-section, "experience")]')
            experience_items = experience_section.find_elements(By.XPATH, './/li')
            for item in experience_items:
                try:
                    print(f"Experience Item Content: {item.text.strip()}")
                    job_title = item.find_element(By.CLASS_NAME, 'experience-item__title').text.strip()
                    company = item.find_elements(By.CLASS_NAME, 'experience-item__meta-item')[1].text.strip()
                    experience.append({"job_title": job_title, "company": company})
                except Exception as e_inner:
                    print(f"Error extracting item details: {e_inner}")
        except Exception as e_outer:
            print(f"Error extracting experience section: {e_outer}")
            print(f"Page Source:\n{self.driver.page_source}")
        return experience
# Example Usage:
if __name__ == "__main__":
    keyword = input("Enter the job title/keyword: ")
    country = input("Enter the country: ")

    # Scrape Google search results for LinkedIn profiles
    scraper = LinkedInScraper(keyword, country , max_pages=1)
    scraper.start()

    # Scrape data for each LinkedIn profile (assuming you have the links in a file)
    with open(f'./users/linkedin_profiles_{keyword}_{country}.json', 'r') as file:
        profile_links = json.load(file)
    
    # Initialize the LinkedInProfileScraper and get details for each profile
    profile_details = []
    for link in profile_links:
        print(f"Scraping profile: {link}")
        profile_scraper = LinkedInProfileScraper(link)
        data = profile_scraper.scrape_profile_data(keyword, country)
        profile_details.append(data)

    # Save the detailed profile data to a JSON file
    with open(f'linkedin_profile_data_{keyword}_{country}.json', 'w') as file:
        json.dump(profile_details, file, indent=4)

    print(f"Scraped data for {len(profile_details)} profiles.")
