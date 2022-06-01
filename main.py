def Booli_ScrapeObjects(page, object_info):
 request = requests.get(page)
 soup = BeautifulSoup(request.text,'lxml')
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
   info.insert(0,"https://www.booli.se" + links[j]["href"])
  #FETCHING ADDRESS, # ROOMS AND M2
  request_apartment = requests.get(info[0])
  soup_apartment = BeautifulSoup(request_apartment.text, 'lxml')
  address = soup_apartment.findAll('span',
   class_ = 'property__header__street-address')
  address = address[0].contents[0].strip("\n\t\t")
  info.append(address)
  size = soup_apartment.findAll('span',
   class_ = 'property__base-info__title__size')
  size = size[0].contents[0].strip("\n\t").split(",")
  rooms = size[0].strip(" rum")
  m2 = size[1].strip(" m²")
  info.append(rooms)
  info.append(m2)
  except:
   info.insert(0, "Unknown")   #Link
   info.append("Unknown")      #Address
   info.append("Unknown")      #Rooms
   info.append("Unknown")      #m2
   info.append("Unknown")      #Estimate
   continue
return object_info


def Booli_findNumberOfPagesData(url):
 request = requests.get(url)
 soup = BeautifulSoup(request.text,'lxml')
 data = soup.findAll('div',
		class_ = 'search-list__pagination-summary')
 numberOfObjectsPerPage = 38
 try:
  numberOfObjects = int(data[0].text[
		-(len(data[0].text)-3 - data[0].text.rfind("av")):])except:
  numberOfObjects = 0
  numberOfPages = int(
		np.ceil(numberOfObjects/numberOfObjectsPerPage))

return numberOfPages, numberOfObjectsPerPage))

def loopThroughRegions(data_url,
			m2_max,
			m2_min,
			maxListPrice,
			minListPrice):
 object_info = []
 region = []
 length = [0]
 for index, row in data_url.iterrows():
  #Base URL
  url = "https://www.booli.se/{}/{}/?
			maxListPrice={}&
			maxLivingArea={}&
			minListPrice={}&
			minLivingArea={}&
			objectType=L%C3%A4genhet&
			page=1&
			upcomingSale=
				".format(row["Region"],
					row["RegionID"],
					maxListPrice,
					m2_max,
					minListPrice,
					m2_min)
  object_info = Booli_ScrapeObjects(url, object_info)
  numberOfPages, numberOfObjects = Booli_findNumberOfPagesData(url)
  for page in range(2, numberOfPages):
   url = "https://www.booli.se/{}/{}/?
		maxListPrice={}&
		maxLivingArea={}&
		minListPrice={}&
		minLivingArea={}&
		objectType=L%C3%A4genhet&
		page={}&
		upcomingSale=
			".format(row["Region"],
				row["RegionID"],
				maxListPrice,
				m2_max,
				minListPrice,
				m2_min,
				page)
  object_info = Booli_ScrapeObjects(url, object_info)
 length.append(len(object_info))
#Creating a simple vector containing duplicates of regions up to number of object stored for each region
 for i in range(0, length[len(length)-1] - length[len(length) - 2]):
  region.append(row["Region"])

return object_info, region

def cleaningData(object_info):
 for index, row in object_info.iterrows():if row["m2"].find("+") != -1:
   m2s = row["m2"].split("+")
   newM2 = int(m2s[0]) + int(m2s[1])
   object_info.set_value(index, "m2", newM2)if row["Number of rooms"].find("½") != -1:
    rooms = row["Number of rooms"].split("½")if rooms[0] == "":
     newRooms = 0.5
    else:
     newRooms = float(0.5) + float(rooms[0])object_info.set_value(index, "Number of rooms", newRooms)if row["Rent"].find("—") != -1:
     newRent = 0
     object_info.set_value(index, "Rent", newRent)
    else:
     newRent = "".join(row["Rent"].split())
     object_info.set_value(index, "Rent", newRent)return object_info

def mssql_connect(server, database, driver):
    cnxn = pyodbc.connect('DRIVER='+driver+ \
                          ';SERVER='+server+ \
                          ';DATABASE='+database + \
                          ';Trusted_Connection=yes')
    cursor = cnxn.cursor()
    return cnxn, cursor

#MAIN ------

#SQL INPUT PARAMETERS
pyodbc.pooling = False
server = 'localhost'
database = 'Booli'
username = 'senek'
password = 'senek'
driver= '{ODBC Driver 13 for SQL Server}'cnxn, cursor = mssql_connect(	server,
				database,
				username,
				password,
				driver)
data = result.values.tolist()
for i, item in enumerate(data):
 insert_query = "IF NOT EXISTS ( \
			SELECT \
				* \
			FROM \
				[Booli].[UpcomingSales] \
			WHERE \
				[Link] = '" + str(item[0]) + "' AND
				[DateInserted] = '" +
				str(date.today()) +"') \
			BEGIN \
			INSERT INTO [Booli].[UpcomingSales] \
			VALUES ('" + str(item[0]) + \
				"'," + str(item[1]) + \
				"," + str(item[2]) + \
				"," + str(item[3]) + \
				",'" + str(item[4]) + \
				"'," + str(item[5]) + \
				"," + str(item[6]) + \
				",'" + str(item[7]) + \
				"','" + str(date.today()) +"') \
			END"cursor.execute(insert_query)
#Cleanup
cnxn.commit()
cursor.close()
cnxn.close()
