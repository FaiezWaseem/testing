from requests.cookies import RequestsCookieJar, create_cookie
from linkedin_api.cookie_repository import CookieRepository
from linkedin_api import Linkedin

# Use cookies from the browser to create a cookie jar
import json

profiles = [
    "https://de.linkedin.com/in/fatih-arzu-mobile-and-java-full-stackdeveloper/en",
    "https://de.linkedin.com/in/memonsarang88",
    "https://www.linkedin.com/in/tejasvi-h-y-504b01112",
    "https://www.linkedin.com/in/aadil-farooqui-6141193b/",
    "https://de.linkedin.com/in/aflatun-valibayli",
    "https://de.linkedin.com/in/john-henry-k%C3%B6nig-47605a99/en",
    "https://www.linkedin.com/in/vaishali-chaudhary-b2b91411b",
    "https://de.linkedin.com/in/olenaopenko",
    "https://de.linkedin.com/in/natalia-konshina/en",
    "https://pk.linkedin.com/in/mohsin-hameed-2224aa5b"
]

def getUsernameFromProfile(profile):
    part = profile.split("/")[-1]
    if part.startswith("en"):
        # get second last part
        name = profile.split("/")[-2]
        if len(name) == 0:
            return None
        return name
    return part

cookies = json.load(open('./cookies.json'))  # Path of exported cookie via https://www.editthiscookie.com/

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

username  = ""
password = ""
# Save cookies
new_repo = CookieRepository()
new_repo.save(cookie_jar, username)

# Authenticate using Linkedin API
api = Linkedin(username, password, cookies=cookie_jar)

for profile in profiles:
    username = getUsernameFromProfile(profile)
    if username is None:
        continue
    currentProfile = api.get_profile(username)
    sleep(2)
    print(currentProfile)
    print("-----------------------------------------")
    # Save profile to JSON file
    with open(f'./users/{username}.json', 'w') as f:
     json.dump(currentProfile, f, indent=4)




