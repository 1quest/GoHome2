from bs4 import BeautifulSoup
from requests import get
from datetime import datetime
import csv
import json
from config import ScraperConfig
from requests_html import HTMLSession

API_KEY = ScraperConfig.GOOGLE_MAPS_API_KEY

# Hemnet search result page will only show 50 pages.
# Attempting to access page 51 or higher will return an error
MAX_NUM_OF_PAGES = 50
County = "Uppsala"


class SlutPriserScraper:
    # Search URL for Stockholm, Nacka, Sundbyberg and Sollentuna counties
    base_url_sthlm = "https://www.hemnet.se/salda/bostader?location_ids%5B%5D=18031&location_ids%5B%5D=17853&location_ids%5B%5D=18028&location_ids%5B%5D=18027&location_ids%5B%5D=18042&item_types%5B%5D=bostadsratt"
    base_url_uppsala = "https://www.hemnet.se/bostader?housing_form_groups%5B%5D=apartments&location_ids%5B%5D=17800"

    def __init__(self, start_page=1, num_of_pages=1, use_google_maps_api=False):
        self.listings = []
        print(API_KEY)
        # Normalized location names used to "clean up" location data
        self.norm_locations = [
            "Bromma",
            "Södermalm",
            "Kungsholmen",
            "Gamla Stan",
            "Midsommarkransen",
            "Råsunda",
            "Telefonplan",
            "Vällingby",
            "Hässelby",
            "Skarpnäck",
            "Sickla",
            "Vasastan",
            "Hagastaden",
            "Östermalm"
        ]

        num_of_pages = min(num_of_pages, MAX_NUM_OF_PAGES)

        for page in range(start_page, num_of_pages+start_page):
            url = self.base_url_uppsala
            if page > 1:
                url += "&page=%d" % page
            # More DOokie
            # driver = webdriver.Firefox()
            sessions = HTMLSession()
            response = sessions.get(url)
            print("Fetching from URL", url)
            # response = get(url)
            # End of DOokiE
            soup = BeautifulSoup(response.text, 'html.parser')

            for property_row in soup.findAll('li', attrs={'class': 'normal-results__hit js-normal-list-item'}):
                listing = {}
                try:
                    location_div = property_row.find(
                        'span', attrs={'class': 'listing-card__location-name'})

                    street_address = property_row.find(
                        'h2', attrs={'class': 'listing-card__street-address qa-listing-title'}).text  # .findAll(
                    # 'span', attrs={'class': 'sold-property-listing__heading qa-selling-price-title'})[0].text

                    # re.sub(r"[\n\t\s]*", "", location_div.div.text.replace('Lägenhet', '').strip()))
                    location = location_div.text.strip().replace(', Uppsala kommun', '')
                    region = location.split(',')[-1].replace('\n', '').replace('\t', '').replace(
                        'Bostadsrättslägenhet', '').replace('\xa0', '').strip().replace('Bostadsrätt', '')
                    # Location normalization
                    normalized = False

                    listing['link'] = property_row.a['href']

                    for norm_loc in self.norm_locations:
                        if norm_loc in location:
                            location = norm_loc
                            normalized = True
                            break

                    if not normalized:
                        location = location.split(',')[0].replace('\n', '').replace('\t', '').replace('Bostadsrättslägenhet', '').replace('\xa0', '').strip(
                        ).replace('Bostadsrätt', '').replace('Andelibostadsförening', '').replace(' ', '').split('/')[0].split('-')[0].split('\\')[0].replace('Lägenhet', '')
                    listing['region'] = region
                    listing['location'] = location

                    # Not really used in the ML model,
                    # but adding this data anyways as extra information
                    listing['street_address'] = street_address

                    if use_google_maps_api:
                        dist_to_central_st = SlutPriserScraper._calculate_distance_to_central_station(
                            street_address)
                        listing['dist_to_central_st'] = dist_to_central_st

                    if not region or not location:
                        print(
                            "Skipping property as region or location parameter not found")
                        continue
                    size_div = property_row.findAll(
                        'div', attrs={'class': 'listing-card__attribute listing-card__attribute--primary'})

                    listing['num_of_rooms'] = size_div[2].text.split(
                        ' rum')[0].replace('\n', '').replace(' ', '').replace(',', '.').split('–')[0]
                    size = size_div[1].text.replace('\n', '').split('m²')[0].split('+')[0].replace(
                        ',', '.').replace(' ', '').split('–')[0]
                    listing['size'] = float(size)

                    if not size_div[2].text or not size_div[1].text:
                        print("Skipping property as num_of_rooms parameter not found")
                        continue
                    fee = property_row.find(
                        'div', attrs={'class': 'listing-card__attribute listing-card__attribute--secondary listing-card__attribute--fee'})
                    if hasattr(fee, 'text'):
                        fee = fee.text
                        fee = fee.replace('\n', '').replace('\t', '').replace(
                            ' ', '').replace('kr/mån', '').replace('\xa0', '')
                    else:
                        fee = '-'
                    listing['fee'] = fee

                    if not fee:
                        print("Skipping property as fee parameter not found")
                        continue

                    final_price_div = size_div[0].text
                    final_price = final_price_div.replace('\n', '').replace('\t', '').replace(
                        ' ', '').split('kr')[0].split('Slutpris')[-1].replace('\xa0', '').replace('fr.', '')
                    listing['price'] = final_price

                    if not final_price:
                        print("Skipping property as final_price parameter not found")
                        continue

                except ValueError as ve:
                    print(ve)
                    exit()
                except Exception as e:
                    print("Exception occurred", e)
                    print("Continuing with next listing...")
                    continue
                # print("APPENDING A LISTING")
                self.listings.append(dict(listing))

    @staticmethod
    def _calculate_distance_to_central_station(street_address):
        origin = street_address.split(',')[0].replace(' ', '+')
        print(origin)

        URL = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s+Stockholm&destinations=T-Centralen+Stockholm&mode=transit&key=%s" % (
            origin, API_KEY)
        print(URL)
        response = get(URL)
        json_data = json.loads(response.text)

        if json_data['status'] == 'REQUEST_DENIED':
            raise ValueError(
                "Request to google maps API was denied. API key provided was not valid")

        return json_data['rows'][0]['elements'][0]['duration']['value']

    # Will not export to CSV, but only output the data

    def show(self):
        for listing in self.listings:
            for key, val in listing.items():
                print(f"{key}: {val}")

            print('\n')

    # Export the results to a CSV file in csv directory
    def to_csv(self):
        now = datetime.now()
        dt_string = now. strftime("%Y%m%d")
        csv_filepath = "./csv/Hemnet_future-" + County + dt_string + ".csv"
        print("Number of listings: "+str(len(self.listings)))
        keys = self.listings[0].keys()

        with open(csv_filepath, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.listings)


if __name__ == "__main__":
    SlutPriserScraper(start_page=1, num_of_pages=50,
                      use_google_maps_api=False).to_csv()
