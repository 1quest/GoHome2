from bs4 import BeautifulSoup
from requests import get
from datetime import datetime
import csv
import json
from config import ScraperConfig

API_KEY = ScraperConfig.GOOGLE_MAPS_API_KEY

# Hemnet search result page will only show 50 pages.
# Attempting to access page 51 or higher will return an error
MAX_NUM_OF_PAGES = 50


class SlutPriserScraper:
    # Search URL for Stockholm, Nacka, Sundbyberg and Sollentuna counties
    base_url = "https://www.hemnet.se/salda/bostader?location_ids%5B%5D=18031&location_ids%5B%5D=17853&location_ids%5B%5D=18028&location_ids%5B%5D=18027&location_ids%5B%5D=18042&item_types%5B%5D=bostadsratt"

    def __init__(self, start_page=1, num_of_pages=1, use_google_maps_api=False):
        self.listings = []
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
            url = self.base_url
            if page > 1:
                url += "&page=%d" % page

            print("Fetching from URL", url)
            response = get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            for property_row in soup.findAll('div', attrs={'class': 'sold-property-listing'}):
                listing = {}
                property_link = property_row.a['href']

                try:

                    location_div = property_row.find(
                        'div', attrs={'class': 'sold-property-listing__location'})
                    street_address = location_div.h2.findAll(
                        'span', attrs={'class': 'item-result-meta-attribute-is-bold item-link'})[0].text
                    location = location_div.div.text.strip()
                    region = location.split(',')[-1].replace('\n', '').replace('\t', '').replace(
                        'Bostadsrättslägenhet', '').replace('\xa0', '').strip().replace('Bostadsrätt', '').replace(' ', '')

                    ## Location normalization
                    normalized = False

                    for norm_loc in self.norm_locations:
                        if norm_loc in location:
                            location = norm_loc
                            #print("Normalized location to", norm_loc)
                            normalized = True
                            break

                    if not normalized:
                        location = location.split(',')[0].replace('\n', '').replace('\t', '').replace('Bostadsrättslägenhet', '').replace('\xa0', '').strip(
                        ).replace('Bostadsrätt', '').replace('Andelibostadsförening', '').replace(' ', '').split('/')[0].split('-')[0].split('\\')[0]

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

                    size_div = property_row.find(
                        'div', attrs={'class': 'sold-property-listing__size'})
                    size_and_rooms = size_div.div.find(
                        'div', attrs={'class': 'sold-property-listing__subheading'}).text
                    size_and_rooms = size_and_rooms.replace(
                        '\n', '').replace('\t', '').replace(' ', '')
                    if size_and_rooms[-6] == ",":
                        num_of_rooms = size_and_rooms[-7:-4].replace(',', '.')
                    else:
                        num_of_rooms = size_and_rooms[-5]
                    listing['num_of_rooms'] = num_of_rooms
                    size = size_and_rooms.split('m')[0].replace(',', '.')
                    listing['size'] = size

                    if not num_of_rooms or not size:
                        print("Skipping property as num_of_rooms parameter not found")
                        continue

                    fee = size_div.div.find(
                        'div', attrs={'class': 'sold-property-listing__fee'}).text
                    fee = fee.replace('\n', '').replace('\t', '').replace(
                        ' ', '').split('kr')[0].replace('\xa0', '')
                    listing['fee'] = fee

                    if not fee:
                        print("Skipping property as fee parameter not found")
                        continue

                    final_price_div = property_row.find(
                        'div', attrs={'class': 'sold-property-listing__price'})
                    final_price = final_price_div.div.span.text
                    final_price = final_price.replace('\n', '').replace('\t', '').replace(
                        ' ', '').split('kr')[0].split('Slutpris')[-1].replace('\xa0', '')
                    listing['final_price'] = final_price

                    if not final_price:
                        print("Skipping property as final_price parameter not found")
                        continue

                    # Fetch the initial price from property page
                    listing_webpage = get(property_link)
                    listing_soup = BeautifulSoup(
                        listing_webpage.text, 'html.parser')

                    price_stats = listing_soup.find(
                        'dl', attrs={'class': 'sold-property__price-stats'})

                    for dt, dd in zip(price_stats.findAll('dt'), price_stats.findAll('dd')):
                        if "Begärt" in dt.text:
                            initial_price = dd.text

                    initial_price = initial_price.replace('\n', '').replace(
                        '\t', '').replace(' ', '').replace('\xa0', '').replace('kr', '')

                    if not initial_price:
                        print(
                            "Skipping property as initial_price parameter not found")
                        continue

                    listing['initial_price'] = initial_price

                    attributes = listing_soup.find(
                        'dl', attrs={'class': 'sold-property__attributes'})

                    for dt, dd in zip(attributes.findAll('dt'), attributes.findAll('dd')):
                        if "Bygg" in dt.text:
                            year_built = dd.text.split('-')[0]
                        elif "Drift" in dt.text:
                            mgmt_cost = dd.text.split('kr')[0].replace(
                                ' ', '').replace('\xa0', '')

                    if not year_built or not mgmt_cost:
                        print(
                            "Skipping property as year_built or mgmt_cost parameter not found")
                        continue

                    listing['year_built'] = year_built

                except ValueError as ve:
                    print(ve)
                    exit()
                except Exception as e:
                    print("Exception occurred", e)
                    print("Continuing with next listing...")
                    continue

                self.listings.append(dict(listing))

    @staticmethod
    def _calculate_distance_to_central_station(street_address):
        origin = street_address.split(',')[0].replace(' ', '+')

        URL = "https://maps.googleapis.com/maps/api/distancematrix/json?origins=%s+Stockholm&destinations=T-Centralen+Stockholm&mode=transit&key=%s" % (
            origin, API_KEY)
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
        csv_filepath = f"csv/{dt_string}-housingprices.csv"
        keys = self.listings[0].keys()

        with open(csv_filepath, 'w') as output_file:
            dict_writer = csv.DictWriter(output_file, keys)
            dict_writer.writeheader()
            dict_writer.writerows(self.listings)


if __name__ == "__main__":
    SlutPriserScraper(start_page=1, num_of_pages=50,
                      use_google_maps_api=False).to_csv()
