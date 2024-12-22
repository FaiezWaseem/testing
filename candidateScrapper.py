from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import csv
from selenium.common.exceptions import NoSuchElementException
import json
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta

from linkedin_scraper import Person, actions
import os

class LinkedInProfileScraper:
    def __init__(self, li_at_cookie, location="Germany", limit=10):
        self.li_at_cookie = li_at_cookie
        self.location = location
        self.limit = limit
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

    def construct_linkedin_search_url(self, keyword):
        """Construct the LinkedIn search URL for people"""
        # Germany's geoUrn is 101282230
        base_url = "https://www.linkedin.com/search/results/people/"
        url = f"{base_url}?keywords={keyword}&geoUrn=%5B%22101282230%22%5D&origin=FACETED_SEARCH"
        return url

    def scroll_to_load_profiles(self):
        """Scroll to load more profiles"""
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            sleep(3)
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    def scrape_profiles(self):
        """Scrape profile data from search results"""
        profiles = self.driver.execute_script("return document?.querySelector('[role=\"list\"]')?.children")
        profiles_data = []
        
        print(f'{len(profiles)} profiles found')
        
        for profile in profiles:
            try:
                print(profile)
                # Get profile URL
                profile_url = self.driver.execute_script("return arguments[0].querySelector('a').href", profile)
                
                print(profile_url)
                
                
                person = Person(profile_url, driver=self.driver)
                
                print(person)
                
                with open('profile_log.txt', 'a', encoding='utf-8') as log_file:
                 log_file.write(json.dumps(person, ensure_ascii=False, indent=4) + '\n')
                
                # Visit profile
                # self.driver.get(profile_url)
                # sleep(5)  # Wait for page to load
                
                # # Basic Info
                # profile_image = self.driver.execute_script("""
                #     return document.querySelector('img.pv-top-card-profile-picture__image')?.src 
                #     || document.querySelector('.presence-entity__image')?.src 
                #     || 'Profile image not found';
                # """)
                
                # name = self.driver.execute_script("""
                #     return document.querySelector('h1.text-heading-xlarge')?.textContent.trim() 
                #     || 'Name not found';
                # """)
                
                # title = self.driver.execute_script("""
                #     return document.querySelector('div.text-body-medium')?.textContent.trim() 
                #     || 'Title not found';
                # """)
                
                # location = self.driver.execute_script("""
                #     return document.querySelector('.pv-text-details__left-panel .text-body-small')?.textContent.trim() 
                #     || 'Location not found';
                # """)
                
                # # About Section
                # about = self.driver.execute_script("""
                #     return document.querySelector('div.pv-shared-text-with-see-more > div > span')?.textContent.trim() 
                #     || 'About not found';
                # """)
                
                # # Skills Section - only grab visible skills
                # skills = self.driver.execute_script("""
                #     const skillElements = document.querySelectorAll('.skill-category-entity__name');
                #     return Array.from(skillElements, el => el.textContent.trim());
                # """)
                
                # profile_data = {
                #     'name': name,
                #     'profile_url': profile_url,
                #     'profile_image': profile_image,
                #     'title': title,
                #     'location': location,
                #     'about': about,
                #     'skills': skills if skills else []
                # }
                
                # profiles_data.append(profile_data)
                
                # Log the scraped profile
                print(f"Scraped profile: {name}")
                
            except Exception as e:
                print(f"Error processing profile: {e}")
                continue
        
        return profiles_data

    def save_to_csv(self, data, filename):
        headers = [
            'name', 'profile_url', 'profile_image', 'title', 'location',
            'about', 'skills'
        ]
        
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            for profile in data:
                # Convert skills list to string for CSV storage
                profile['skills'] = ', '.join(profile['skills']) if profile['skills'] else ''
                writer.writerow(profile)

    def save_to_json(self, data, filename):
        """Save profile data to a JSON file."""
        with open(filename, 'w', encoding='utf-8') as file:
            json.dump(data, file, ensure_ascii=False, indent=4)

    def teardown(self):
        self.driver.quit()

    def run(self, keyword):
        url = self.construct_linkedin_search_url(keyword)
        print(url)
        self.driver.get(url)
        sleep(5) 
        self.scroll_to_load_profiles()
        profiles_data = self.scrape_profiles()
        max = self.limit
        start = 0
        
        print(f'----------PROFILE FOUND ({len(profiles_data)})')
        
        # Now visit each profile and get additional details
        # for profile in profiles_data:
        #     if start >= max:
        #         break
        #     start += 1
        #     print(f"Scraping profile {start} of {max}")
        #     print(profile['profile_url'])
        #     self.driver.get(profile['profile_url'])
        #     sleep(5)
            
        #     try:
        #         # Scrape company LinkedIn URL
        #         elements = self.driver.execute_script("return document.querySelectorAll('[data-view-name=\"job-details-about-company-name-link\"]')")
        #         if elements and len(elements) > 0:
        #             company_link = elements[0].get_attribute('href')
        #         else:
        #             company_link = "Company LinkedIn URL not found"
        #     except NoSuchElementException:
        #         company_link = "Company LinkedIn URL not found"
            
        #     try:
        #         # Scrape company about section
        #         company_about = self.driver.execute_script(
        #             "return document.querySelectorAll('.jobs-company__company-description')[0]?.textContent || 'Description not found';"
        #         )
        #     except Exception as e:
        #         print(f"An error occurred: {e}")
        #         company_about = "Description not found"
            
        #     try:
        #         # Scrape job description
        #         elements = self.driver.execute_script("return document.querySelectorAll('.jobs-description-content__text--stretch')")
        #         if elements and len(elements) > 0:
        #             job_description = elements[0].text
        #         else:
        #             job_description = "Job description not found"
        #     except NoSuchElementException:
        #         job_description = "Job description not found"
            
        #     try:
        #         # Scrape post date
        #         post_date_str = self.driver.execute_script(
        #             "return document.querySelectorAll('.job-details-jobs-unified-top-card__primary-description-container')[0].childNodes[2].childNodes[3].textContent"
        #         )
                
        #         # Convert the post_date string to a datetime object
        #         post_date = datetime.now()  # Default to now if parsing fails
        #         try:
        #             if "hour" in post_date_str:
        #                 hours = int(post_date_str.split()[0])
        #                 post_date -= timedelta(hours=hours)
        #             elif "day" in post_date_str:
        #                 days = int(post_date_str.split()[0])
        #                 post_date -= timedelta(days=days)
        #             elif "month" in post_date_str:
        #                 months = int(post_date_str.split()[0])
        #                 post_date -= relativedelta(months=months)
        #             elif "year" in post_date_str:
        #                 years = int(post_date_str.split()[0])
        #                 post_date -= relativedelta(years=years)
        #         except Exception as e:
        #             print(f"Error parsing date: {e}")
        #     except Exception as e:
        #         print(f"An error occurred: {e}") 
        #         post_date = "Post date not found"
            
            
        #     print(company_link)
        #     print(company_about)
        #     print(job_description)
        #     print(post_date)
            
        #     # Update profile data with new details
        #     profile.update({
        #         'company_link': company_link,
        #         'company_about': company_about,
        #         'description': job_description,
        #         'post_date': post_date.isoformat() if isinstance(post_date, datetime) else post_date
        #     })
            
        #     # Write the updated profile to a log file
        #     with open('profile_log.txt', 'a', encoding='utf-8') as log_file:
        #         log_file.write(json.dumps(profile, ensure_ascii=False, indent=4) + '\n')
            
        #     print(profile)
        
        # self.save_to_json(profiles_data, 'linkedin_profiles.json')  # Save to JSON
        # self.save_to_csv(profiles_data, 'linkedin_profiles.csv')
        # self.teardown()
        return profiles_data

if __name__ == "__main__":
    cookie = os.environ.get('li_at')
    print(cookie)
    scraper = LinkedInProfileScraper(
        li_at_cookie=cookie,
        location="Germany"
        )
    scraper.run(
        keyword="Python+Developer"
    )
