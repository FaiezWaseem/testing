from selenium import webdriver
from time import sleep
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import csv
from selenium.common.exceptions import NoSuchElementException

class LinkedInJobScraper:
    def __init__(self, li_at_cookie, location="Germany"):
        self.li_at_cookie = li_at_cookie
        self.location = location
        self.driver = self.setup_linkedin_jobs()

    class TypeFilters:
        FULL_TIME = "F"
        INTERNSHIP = "I"

    class OnSiteOrRemoteFilters:
        REMOTE = "R"
        ON_SITE = "O"
        HYBRID = "H"

    class ExperienceLevelFilters:
        MID_SENIOR = "MS"
        INTERNSHIP = "I"
        ENTRY_LEVEL = "EL"
        ASSOCIATE = "A"

    class SalaryBaseFilters:
        SALARY_100K = "100K"
        SALARY_150K = "150K"
        SALARY_200K = "200K"
        SALARY_250K = "250K"
        SALARY_300K = "300K"
        SALARY_350K = "350K"
        SALARY_400K = "400K"
        SALARY_450K = "450K"
        SALARY_500K = "500K"

    def setup_linkedin_jobs(self):
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

    def construct_linkedin_job_url(self, type, on_site_or_remote, experience, base_salary):
        base_url = "https://www.linkedin.com/jobs/search/"
        type_filter = ",".join(type)
        on_site_or_remote_filter = ",".join(on_site_or_remote)
        experience_filter = ",".join(experience)
        salary_filter = base_salary

        url = f"{base_url}?f_TP={type_filter}&f_WT={on_site_or_remote_filter}&f_E={experience_filter}&f_SB={salary_filter}&location={self.location}"
        return url

    def scroll_to_load_jobs(self):
        container = self.driver.execute_script("return document.querySelectorAll('.job-card-container')[0].parentNode.parentNode.parentNode")
        last_height = self.driver.execute_script("return arguments[0].scrollHeight", container)
        
        while True:
            self.driver.execute_script("arguments[0].scrollTop = arguments[0].scrollHeight", container)
            sleep(3)
            new_height = self.driver.execute_script("return arguments[0].scrollHeight", container)
            
            if new_height == last_height:
                break
            
            last_height = new_height

    def scrape_jobs(self):
        jobs = self.driver.find_elements(By.CLASS_NAME, 'job-card-container')
        jobs_data = []
        
        for job in jobs:
            try:
                job_id = job.get_attribute('data-job-id')
                link = job.find_element(By.TAG_NAME, 'a').get_attribute('href')
                apply_link = link
                
                title_element = job.find_element(By.TAG_NAME, 'a').find_element(By.TAG_NAME, 'strong')
                title = title_element.text if title_element else "Title not found"
                
                try:
                    company = job.find_element(By.CLASS_NAME, 'artdeco-entity-lockup__subtitle').text
                except NoSuchElementException:
                    company = "Company not found"
                
                try:
                    company_link = job.find_element(By.CLASS_NAME, 'artdeco-entity-lockup__subtitle').find_element(By.TAG_NAME, 'a').get_attribute('href')
                except NoSuchElementException:
                    company_link = "Company link not found"
                
                try:
                    company_img_link = job.find_element(By.TAG_NAME, 'img').get_attribute('src')
                except NoSuchElementException:
                    company_img_link = "Image link not found"
                
                try:
                    place = job.find_element(By.CLASS_NAME, 'job-card-container__metadata-wrapper').text
                except NoSuchElementException:
                    place = "Location not found"
                
                job_type = "Type not found"
                if "(" in place and ")" in place:
                    job_type = place[place.find("(") + 1:place.find(")")]
                
                try:
                    description = job.find_element(By.CLASS_NAME, 'job-card-container__description').text
                except NoSuchElementException:
                    description = "Description not found"
                
                try:
                    description_html = job.find_element(By.CLASS_NAME, 'job-card-container__description').get_attribute('innerHTML')
                except NoSuchElementException:
                    description_html = "Description HTML not found"
                
                try:
                    date = job.find_element(By.CLASS_NAME, 'job-card-container__listed-time').text
                except NoSuchElementException:
                    date = "Date not found"
                
                try:
                    insights = job.find_element(By.CLASS_NAME, 'job-card-container__insights').text
                except NoSuchElementException:
                    insights = "Insights not found"
                
                jobs_data.append({
                    'job_id': job_id,
                    'link': link,
                    'apply_link': apply_link,
                    'title': title,
                    'company': company,
                    'company_link': company_link,
                    'company_img_link': company_img_link,
                    'place': place,
                    'job_type': job_type,
                    'description': description,
                    'description_html': description_html,
                    'date': date,
                    'insights': insights
                })
            except Exception as e:
                print(f"Error processing job: {e}")
        
        return jobs_data

    def save_to_csv(self, data, filename):
        
        
        headers = [
            'job_id', 'link', 'apply_link', 'title', 'company', 'company_link',
            'company_img_link', 'place', 'job_type', 'description',
            'description_html', 'date', 'insights', 'job_description',
            'company_linkedin_url', 'company_about', 'post_date'
        ]
        
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.DictWriter(file, fieldnames=headers)
            writer.writeheader()
            writer.writerows(data)

    def teardown(self):
        self.driver.quit()

    def run(self, type_filters, on_site_or_remote_filters, experience_filters, base_salary_filter):
        url = self.construct_linkedin_job_url(type_filters, on_site_or_remote_filters, experience_filters, base_salary_filter)
        print(url)
        self.driver.get(url)
        sleep(5) 
        self.scroll_to_load_jobs()
        jobs_data = self.scrape_jobs()
        
        # Now visit each job and get additional details
        for job in jobs_data:
            self.driver.get(job['link'])
            sleep(5)
            
            try:
                # Scrape company LinkedIn URL
                elements = self.driver.execute_script("return document.querySelectorAll('[data-view-name=\"job-details-about-company-name-link\"]')")
                if elements and len(elements) > 0:
                    company_link = elements[0].get_attribute('href')
                else:
                    company_link = "Company LinkedIn URL not found"
            except NoSuchElementException:
                company_link = "Company LinkedIn URL not found"
            
            try:
                # Scrape company about section
                company_about = self.driver.find_element(By.CSS_SELECTOR, 'section.about-us').text
            except NoSuchElementException:
                company_about = "Company about section not found"
            
            try:
                # Scrape job description
                elements = self.driver.execute_script("return document.querySelectorAll('.jobs-description-content__text--stretch')")
                if elements and len(elements) > 0:
                    job_description = elements[0].text
                else:
                    job_description = "Job description not found"
            except NoSuchElementException:
                job_description = "Job description not found"
            
            try:
                # Scrape post date
                post_date = self.driver.find_element(By.CSS_SELECTOR, 'time.job-post-date').text
            except NoSuchElementException:
                post_date = "Post date not found"
            
            
            print(company_link)
            print(company_about)
            print(job_description)
            print(post_date)
            
            # Update job data with new details
            job.update({
                'company_link': company_link,
                'company_about': company_about,
                'description': job_description,
                'post_date': post_date
            })
            
            print(job)
        
        self.save_to_csv(jobs_data, 'linkedin_jobs.csv')
        self.teardown()

if __name__ == "__main__":
    scraper = LinkedInJobScraper(
        li_at_cookie="",
        location="USA"
        )
    scraper.run(
        type_filters=[LinkedInJobScraper.TypeFilters.FULL_TIME, LinkedInJobScraper.TypeFilters.INTERNSHIP],
        on_site_or_remote_filters=[LinkedInJobScraper.OnSiteOrRemoteFilters.REMOTE, LinkedInJobScraper.OnSiteOrRemoteFilters.ON_SITE, LinkedInJobScraper.OnSiteOrRemoteFilters.HYBRID],
        experience_filters=[LinkedInJobScraper.ExperienceLevelFilters.MID_SENIOR, LinkedInJobScraper.ExperienceLevelFilters.INTERNSHIP, LinkedInJobScraper.ExperienceLevelFilters.ENTRY_LEVEL, LinkedInJobScraper.ExperienceLevelFilters.ASSOCIATE],
        base_salary_filter=LinkedInJobScraper.SalaryBaseFilters.SALARY_100K,    
    )


