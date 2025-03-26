import numpy as np
import pyodbc
import requests
import re
from IPython.core.oinspect import object_info
from bs4 import BeautifulSoup


def Booli_ScrapeObjects(page, object_info):
    request = requests.get(page)
    soup = BeautifulSoup(request.text, 'lxml')
    links = soup.select("a[href*=/annons/]")

    for j, row in enumerate(links):
        info = row.contents[5].text.split("\n")
        while '' in info:
            info.remove('')
            info[0] = info[0].strip(" kr")
            info[1] = info[1].strip(" kr/m²")
            info[2] = info[2].strip(" kr/mån")
            object_info.append(info)
        try:
            info.insert(0, "https://www.booli.se" + links[j]["href"])
            #           FETCHING ADDRESS, # ROOMS AND M2
            request_apartment = requests.get(info[0])
            soup_apartment = BeautifulSoup(request_apartment.text, 'lxml')
            address = soup_apartment.findAll('span',
                                             class_='property__header__street-address')
            address = address[0].contents[0].strip("\n\t\t")
            info.append(address)
            size = soup_apartment.findAll('span',
                                          class_='property__base-info__title__size')
            size = size[0].contents[0].strip("\n\t").split(",")
            rooms = size[0].strip(" rum")
            m2 = size[1].strip(" m²")
            info.append(rooms)
            info.append(m2)
        except:
            info.insert(0, "Unknown")  # Link
            info.append("Unknown")  # Address
            info.append("Unknown")  # Rooms
            info.append("Unknown")  # m2
            info.append("Unknown")  # Estimate
        continue

    return object_info


def Booli_ScrapeLinks_wip(url):
    try:
        # Send a GET request to the URL
        response = requests.get(url)
        response.raise_for_status()  # Raise an HTTPError for bad responses (4xx and 5xx)

        # Parse the response content with BeautifulSoup
        soup = BeautifulSoup(response.text, 'lxml')

        # Select all links with the specific class and href containing '/annons/'
        links = soup.select("a.expanded-link.no-underline.hover\\:underline[href*='/']")

        # Extract the href values from the link elements
        hrefs = [link['href'] for link in links]

        return hrefs
    except requests.RequestException as e:
        print(f"An error occurred: {e}")
        return []


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
        # print(last_number)
        # print(data)
    else:
        print("No matches found")
        last_number = 0
    return last_number


#   Loop through regions


def loop_through_regions(data_url,
                         m2_max,
                         m2_min,
                         max_list_price,
                         min_list_price):
    object_info = []
    region = []
    length = [0]
    for index, row in data_url.iterrows():
        # Base URL
        url = "https://www.booli.se/{}/{}/?maxListPrice={}&maxLivingArea={}&minListPrice={}&minLivingArea={}&objectType=L%C3%A4genhet&page=1&upcomingSale=".format(
            row["Region"],
            row["RegionID"],
            max_list_price,
            m2_max,
            min_list_price,
            m2_min)
        object_info = Booli_ScrapeObjects(url, object_info)
        numberOfPages, numberOfObjects = Booli_findNumberOfPagesData(url)
        for page in range(2, numberOfPages):
            object_info = Booli_ScrapeObjects(url, object_info)
            length.append(len(object_info))
            # Creating a simple vector containing duplicates of regions up to number of object stored for each region
            for i in range(0, length[len(length) - 1] - length[len(length) - 2]):
                region.append(row["Region"])
    return object_info, region

# Clean data
def cleaning_data(object_info):

    for index, row in object_info.iterrows():
        if row["m2"].find("+") != -1:
            m2s = row["m2"].split("+")

        newM2 = int(m2s[0]) + int(m2s[1])
        object_info.set_value(index, "m2", newM2)
        if row["Number of rooms"].find("½") != -1:
            rooms = row["Number of rooms"].split("½")
        if rooms[0] == "":
            newRooms = 0.5
        else:
            newRooms = float(0.5) + float(rooms[0])
        object_info.set_value(index, "Number of rooms", newRooms)
        if row["Rent"].find("—") != -1:
            newRent = 0
        object_info.set_value(index, "Rent", newRent)
    else:
        newRent = "".join(row["Rent"].split())
        object_info.set_value(index, "Rent", newRent)
        return object_info

def mssql_connect(server, database, driver):

    cnxn = pyodbc.connect('DRIVER=' + driver + \
                          ';SERVER=' + server + \
                          ';DATABASE=' + database + \
                          ';Trusted_Connection=yes')

    cursor = cnxn.cursor()
    return cnxn, cursor

# MAIN ------

# # SQL INPUT PARAMETERS
# pyodbc.pooling = False
# server = 'localhost'
# database = 'Booli'
# username = 'senek'
# password = 'senek'
# driver = '{ODBC Driver 13 for SQL Server}'
# cnxn, cursor = mssql_connect(server,
#                              database,
#                              username,
#                              password,
#                              driver)
# data = result.values.tolist()
# for i, item in enumerate(data):
#     insert_query = "IF NOT EXISTS ( \
# SELECT \
# * \
# FROM \
# [Booli].[UpcomingSales] \
# WHERE \
# [Link] = '" + str(item[0]) + "' AND
# [DateInserted] = '"
# + str(date.today()) + "') \
# BEGIN \
# INSERT INTO [Booli].[UpcomingSales] \
# VALUES ('" + str(item[0]) + \
# "'," + str(item[1]) + \
# "," + str(item[2]) + \
# "," + str(item[3]) + \
# ",'" + str(item[4]) + \
# "'," + str(item[5]) + \
# "," + str(item[6]) + \
# ",'" + str(item[7]) + \
# "','" + str(date.today()) + "') \
# END"
# cursor.execute(insert_query)
# # Cleanup
# cnxn.commit()
# cursor.close()
# cnxn.close()


if __name__ == "__main__":
    url_booli_uppsala_kommun = 'https://www.booli.se/sok/till-salu?areaIds=1116&objectType=Villa&maxListPrice=7000000&minRooms=3.5'
    print(Booli_findNumberOfPagesData(url_booli_uppsala_kommun))
