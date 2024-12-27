from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
import csv
import json
from requests.cookies import RequestsCookieJar, create_cookie
from linkedin_api.cookie_repository import CookieRepository
from linkedin_api import Linkedin
from urllib.parse import urlparse, parse_qs

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
        print(f'{len(profiles)} profiles found')
        sleep(6)
        profile_links = []

        for profile in profiles:
            try:
                print(profile)
                # Get profile URL
                profile_url = self.driver.execute_script("return arguments[0].querySelector('a').href", profile)
                print(profile_url)
                profile_links.append(profile_url)
            except Exception as e:
                print(f"Error processing profile: {e}")
                continue
        
        return profile_links

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
        
    def getCookies(self , path):
        cookies = json.load(open(path))  
        cookie_jar = RequestsCookieJar()
        for cookie_data in cookies:
         cookie = create_cookie(
            domain=cookie_data["domain"],
            name=cookie_data["name"],
            value=cookie_data["value"],
            path=cookie_data["path"],
            secure=cookie_data["secure"],
            expires=cookie_data.get("expirationDate", None),
            rest={
             "HttpOnly": cookie_data.get("httpOnly", False),
             "SameSite": cookie_data.get("sameSite", "unspecified"),
             "HostOnly": cookie_data.get("hostOnly", False),
            }
         )
         cookie_jar.set_cookie(cookie)
        return cookie_jar
    
    def get_linkedin_username(self ,url: str) -> str:
        parsed_url = urlparse(url)
        path_segments = parsed_url.path.strip('/').split('/')
        
        if 'in' in path_segments:
            index = path_segments.index('in')
            if index + 1 < len(path_segments):
                return path_segments[index + 1].split('?')[0]
        
        query_params = parse_qs(parsed_url.query)
        mini_profile_urn = query_params.get('miniProfileUrn', [None])[0]
        
        if mini_profile_urn:
            return mini_profile_urn.split(':')[-1]
        
        return "Username not found"

    def run(self, keyword , cookiePath):
        url = self.construct_linkedin_search_url(keyword)
        cookies =  self.getCookies(cookiePath)
        api = Linkedin(username = '', password = '', cookies=cookies)
        self.driver.get(url)
        sleep(5) 
        self.scroll_to_load_profiles()
        profiles_Links = self.scrape_profiles()
        max = self.limit
        start = 0
        
        print(f'----------PROFILE FOUND ({len(profiles_Links)})')
        
        profiles_data =[]
        
        self.teardown()
        # Now visit each profile and get additional details
        for profile in profiles_Links:
            try:
                if start >= max:
                    break
                start += 1
                print(f"Scraping profile {start} of {max}")
                username = self.get_linkedin_username(profile)
                if username is None:
                    continue
                currentProfile = api.get_profile(username)
                contact_info = api.get_profile_contact_info(username)
                print(contact_info)
                print(f'linedin_url=https://www.linkedin.com/in/{username}')
                print(f'username={username}')
                print(f'name={currentProfile["firstName"]} {currentProfile["lastName"]}')
                print(f'title={currentProfile["headline"]}')
                print(f'location={currentProfile["locationName"]}')
                print(f'skills={contact_info["email_address"]}')
                
                currentProfile["contact_info"] = contact_info
                
                print('----------------------------------------------------------')

                profiles_data.append(currentProfile)
                sleep(3)

                with open('profile_log.txt', 'a', encoding='utf-8') as log_file:
                    log_file.write(json.dumps(contact_info, ensure_ascii=False, indent=4) + '\n')
            except Exception as e:
                print(f"Error scraping profile {profile}: {str(e)}")
                continue
        
        self.save_to_json(profiles_data, f'./users/{keyword}_{self.location}_linkedin_profiles.json')
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
