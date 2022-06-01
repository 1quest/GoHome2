def Booli_findNumberOfPagesData(url):
    request = requests.get(url)
    soup = BeautifulSoup(request.text, 'lxml')
    data = soup.findAll('div',
                        class_='search-list__pagination-summary')
    numberOfObjectsPerPage = 38
    try:
        numberOfObjects = int(
            data[0].text[-(len(data[0].text)-3 - data[0].text.rfind("av")):])
    except:
        numberOfObjects = 0
        numberOfPages = int(np.ceil(numberOfObjects/numberOfObjectsPerPage))


return numberOfPages, numberOfObjectsPerPage
#   Loop through regions
