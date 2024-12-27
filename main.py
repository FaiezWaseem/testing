import os
from time import sleep


from jobScrapper import LinkedInJobScraper
from candidateScrapper import LinkedInProfileScraper
from company import LinkedInCompanyDetails


from config import LI_AT




print("---- WELCOME TO LINKEDIN SCRAPPER ------")
print("1. Scrape LinkedIn Jobs")
print("2. Scrape LinkedIn Profiles")
print("3. Scrape LinkedIn Companies")
print("4. Exit")
print("Please Select an option above : ")

option = input()
cookie = LI_AT

# Switch Case To Handle Options
match option:
    case "1":
        print("Starting LinkedIn Jobs Scraper...")
        location  = input("Enter the location: ")
        limit = input("Enter the limit: ")
        limit = int(limit)
        print('Scrapper is Working...')
        scraper = LinkedInJobScraper(
            li_at_cookie=cookie,
            location=location,
            limit=limit
        )
        data = scraper.run(
        type_filters=[LinkedInJobScraper.TypeFilters.FULL_TIME, LinkedInJobScraper.TypeFilters.INTERNSHIP],
        on_site_or_remote_filters=[LinkedInJobScraper.OnSiteOrRemoteFilters.REMOTE, LinkedInJobScraper.OnSiteOrRemoteFilters.ON_SITE, LinkedInJobScraper.OnSiteOrRemoteFilters.HYBRID],
        experience_filters=[LinkedInJobScraper.ExperienceLevelFilters.MID_SENIOR, LinkedInJobScraper.ExperienceLevelFilters.INTERNSHIP, LinkedInJobScraper.ExperienceLevelFilters.ENTRY_LEVEL, LinkedInJobScraper.ExperienceLevelFilters.ASSOCIATE],
        base_salary_filter=LinkedInJobScraper.SalaryBaseFilters.SALARY_350K,    
        )
        print(data)
        print(f'{len(data)} Jobs Scrapped')
        print('-----Closing-----')
        exit() 
        # Add jobs scraping logic here
    case "2":
        print("Starting LinkedIn Profiles Scraper...")
        
        
        
        location  = input("Enter the location: ")
        keyword = input("Enter the keyword: ex (Python+Developer) :")
        limit = int(input("Enter the limit: "))
        print('Scrapper is Working...')
        scraper = LinkedInProfileScraper(
            li_at_cookie=cookie,
            location=location,
            limit=limit
        )
        data = scraper.run(
        keyword=keyword,
        cookiePath='./cookies.json'
        )
        print(data)
        print(f'{len(data)} Developer Profile Scrapped')
        print('-----Closing-----')
        exit() 
        
        
        # Add profiles scraping logic here
    case "3":
        print("Starting LinkedIn Companies Scraper...")
        company_name = input("Enter the company name: ")
        print('Scrapper is Working...')
        scraper = LinkedInCompanyDetails(
            url=company_name,
            cookiesPath='./cookies.json'
        )
        data = scraper.getCompanyJSON()
        print(data)
        # Add companies scraping logic here
    case "4":
        print("Exiting...")
        exit()
    case _:
        print("Invalid option selected. Please try again.")





