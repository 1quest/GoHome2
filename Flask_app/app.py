from flask import Flask, render_template, redirect, url_for
import requests
from bs4 import BeautifulSoup
import re

url_booli_uppsala_kommun = 'https://www.booli.se/sok/till-salu?areaIds=1116&objectType=Villa&maxListPrice=7000000&minRooms=3.5'
url_booli_home = 'https://www.booli.se'

app = Flask(__name__)

# Helper function to safely extract text
def safe_extract(li_elements, index, suffix=''):
    try:
        return li_elements[index].find('p').get_text(strip=True).replace(suffix, '').replace(u'\xa0', u'').replace('rum', '').strip()
    except IndexError:
        return None

class RealEstateListing:
    def __init__(self, booli_price, boarea, rum, biarea, tomtstorlek, byggar, utgangspris, bostadstyp, omrade, stad, price_text, url):
        self.booli_price = booli_price
        self.boarea = boarea
        self.rum = rum
        self.biarea = biarea
        self.tomtstorlek = tomtstorlek
        self.byggar = byggar
        self.utgangspris = utgangspris
        self.bostadstyp = bostadstyp
        self.omrade = omrade
        self.stad = stad
        self.price_text = price_text
        self.url = url

    def __repr__(self):
        return (f"RealEstateListing(booli_price={self.booli_price}, boarea={self.boarea}, rum={self.rum}, "
                f"biarea={self.biarea}, tomtstorlek={self.tomtstorlek}, byggar={self.byggar}, "
                f"utgangspris={self.utgangspris}, bostadstyp={self.bostadstyp}, omrade={self.omrade}, "
                f"stad={self.stad}, price_text={self.price_text}, url={self.url})")

    def storeInDB(self, connection):
        pass  # Implement your database storage logic here

def Booli_findNumberOfPagesData(url):
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'lxml')
    data = soup.find_all('p', class_='m-2')
    # Regular expression to match the last number inside <!-- -->
    pattern = r'<!-- -->(\d+)<\/p>]'

    # Find all matches
    matches = re.findall(pattern, str(data))

    if matches:
        # Extract the last match and get the number
        last_number = matches[-1]
    else:
        print("No matches found")
        last_number = 0
    return int(last_number)

def Booli_ScrapeLinks(url, pages):
    hrefs = []
    for i in range(1, pages + 1):
        url_loop = f"{url}&page={i}"
        try:
            # Send a GET request to the URL
            response = requests.get(url_loop)
            response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

            # Parse the response content with BeautifulSoup
            soup = BeautifulSoup(response.text, 'lxml')

            # Select all links with the specific class and href containing '/annons/'
            links = soup.select("a.expanded-link.no-underline.hover\\:underline[href*='/']")

            # Extract the href values from the link elements and append to the list
            hrefs.extend([link['href'] for link in links])

        except requests.RequestException as e:
            print(f"An error occurred on page {i}: {e}")
            continue  # Continue to the next page even if there's an error on the current page

    return hrefs

def Booli_ScrapeObjects(links):
    listings = []
    for j, row in enumerate(links):
        # Compile the listing-url
        url_loop = url_booli_home + links[j]
        # Send a GET request to the URL
        response = requests.get(url_loop)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)
        soup = BeautifulSoup(response.text, 'lxml')
        print("URL: " + url_loop)

        # Find the span element with class 'heading-2'
        price_span = soup.find('span', class_='heading-2')

        if price_span:
            # Extract the text content and remove the 'kr' part
            price_text = price_span.get_text(strip=True).replace(u'\xa0', u'').replace('kr', '')
        try:
            int(price_text)
        except:
            price_text = '-999999'

        # Find the p element with the specific class containing the desired price
        booli_price = soup.find('p', class_='heading-5 whitespace-nowrap first-letter:uppercase tabular-nums lining-nums')

        if booli_price:
            # Extract the text content and remove the ' kr' part
            booli_price = booli_price.get_text(strip=True).split(' ')[0].replace(u'\xa0', u'').replace('kr', '')
        else:
            booli_price = '-999999'

        # Find the ul element with the housing details
        details_soup = soup.find('ul', class_='flex flex-wrap gap-y-4 gap-x-8 sm:gap-x-12 flex flex-wrap mt-6')

        # Find all <li> elements within the <ul>
        li_elements = details_soup.select('ul.flex > li')

        # Extract the desired values safely
        boarea = safe_extract(li_elements, 0, 'm²')
        rum = safe_extract(li_elements, 1)
        biarea = safe_extract(li_elements, 2, 'm²')
        tomtstorlek = safe_extract(li_elements, 3, 'm²')
        byggar = safe_extract(li_elements, 4)

        # Find the p element with the specific class containing the desired price
        utgangspris = soup.find('span', class_='text-sm text-content-secondary mt-2')

        # Regex pattern to extract text between > and <, excluding the brackets
        pattern = r'>([^<]+)<'

        # Find all matches
        bostadstyp, omrade, stad = re.findall(pattern, str(utgangspris))[0].split(' · ')

        listing = RealEstateListing(booli_price, boarea, rum, biarea, tomtstorlek, byggar, price_text, bostadstyp, omrade, stad, price_text, url_loop)
        listings.append(listing)

    return listings

# Define the ETL_db method
def etl_db():
    # ETL logic
    print("ETL process started")
    pages = Booli_findNumberOfPagesData(url_booli_uppsala_kommun)
    links = Booli_ScrapeLinks(url_booli_uppsala_kommun, pages)
    listings = Booli_ScrapeObjects(links)
    for listing in listings:
        print(listing)
    print("ETL process finished")

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/run_etl')
def run_etl():
    etl_db()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(debug=True)