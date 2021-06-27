import os
import requests
from bs4 import BeautifulSoup

target = "https://monroewaschools.nextrequest.com/requests/20-60"

r = requests.get(target)