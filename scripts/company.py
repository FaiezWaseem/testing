import json
from requests.cookies import RequestsCookieJar, create_cookie
from linkedin_api import Linkedin

class LinkedInCompanyDetails:
    def __init__(self, url, cookiesPath):
        self.url = url
        self.cookies = self.getCookies(cookiesPath)

        
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
    
    def getCompanyJSON(self):
        api = Linkedin(username = '', password = '', cookies=self.cookies)
        company_json = api.get_company(self.url)
        
        # Save the JSON data to a file
        with open(f'./companies/{self.url}.json', 'w') as json_file:
            json.dump(company_json, json_file, indent=4)
        
        return company_json
        
    