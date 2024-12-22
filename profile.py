from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from time import sleep
from selenium.webdriver.common.by import By

from linkedin_scraper import Person , Company , JobSearch , Job
class LinkedInProfileScraper:
    def __init__(self, li_at_cookie, location="Germany"):
        self.li_at_cookie = li_at_cookie
        self.location = location
        self.driver = self.setup_linkedin()

    def setup_linkedin(self):
        options = Options()
        options.add_argument('--disable-infobars')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-setuid-sandbox')
        options.add_argument('--disable-gpu')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-logging')
        options.add_argument('--disable-browser-side-navigation')
        options.add_argument('--remote-debugging-address=0.0.0.0')
        options.add_argument('--remote-debugging-port=9222')
        options.add_argument('--remote-debugging-port=0')
        options.add_argument('--disable-features=VizDisplayCompositor')
        options.add_argument('--disable-blink-features=AutomationControlled')
        options.add_argument('--start-maximized')
        options.add_argument('--disable-popup-blocking')
        options.add_argument('--disable-notifications')

        driver = webdriver.Chrome(options=options)
        driver.get("https://www.linkedin.com")
        sleep(0.7)

        driver.add_cookie({
            'name': 'li_at',
            'value': self.li_at_cookie,
            'domain': '.linkedin.com'
        })
        driver.refresh()

        return driver
    
    def scrape_profile_json(self, profile_url):
        driver = self.driver
        driver.get(profile_url)
        script_element = driver.find_element(By.CSS_SELECTOR, 'script[type="application/ld+json"]')
        json_data = script_element.get_attribute('innerHTML')
        profile_data = json.loads(json_data)
        return profile_data
    
    def scrape_profile(self, profile_url):
        person = Person(profile_url, driver=self.driver).scrape(close_on_complete=False)
        return person
        
        


#This code block is the main entry point of the application. It demonstrates how to use the `LinkedInProfileScraper` class to scrape a LinkedIn profile and save the data to a JSON file.
#The code first retrieves the `li_at` cookie from the environment, which is used to authenticate the scraper with LinkedIn. It then creates an instance of the `LinkedInProfileScraper` class and uses it to scrape the profile data for the specified URL.
#The scraped profile data is then converted to a dictionary and saved to a JSON file named `profile_data.json`. The JSON file is formatted with indentation and ensures that non-ASCII characters are properly encoded.
if __name__ == "__main__":
    cookie = os.environ.get('li_at')
    scraper = LinkedInProfileScraper(cookie)
    profile_url = "https://www.linkedin.com/in/adeel-a-khan/"
    # profile_data = scraper.scrape_profile_json(profile_url)
    # print(profile_data)
    profile_data = scraper.scrape_profile(profile_url)
    print(profile_data)
    profile_data_dict = {
        'name': profile_data.name,
        'about': profile_data.about,
        'accomplishments': profile_data.accomplishments,
        'educations': profile_data.educations,
        'experiences': profile_data.experiences,
        'contacts': profile_data.contacts,
        'interests': profile_data.interests,
        'job_title': profile_data.job_title,
    }
    
    import json
    with open('profile_data.json', 'w', encoding='utf-8') as f:
        json.dump(profile_data_dict, f, indent=4, ensure_ascii=False)