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
# FETCHING ADDRESS, # ROOMS AND M2
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
