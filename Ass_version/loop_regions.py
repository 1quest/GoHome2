def loopThroughRegions(data_url, m2_max, m2_min, maxListPrice, minListPrice):
    object_info = []
    region = []
    length = [0]
    for index, row in data_url.iterrows():
        #Base URL
        url = "https://www.booli.se/{}/{}/?maxListPrice={}"
        " & maxLivingArea = {} & minListPrice = {} & minLivingArea = {} & "
        "objectType = L % C3 % A4genhet & page = 1 & upcomingSale = ".format(row["Region"],
                                                                             row[
            "RegionID"],
            maxListPrice,
            m2_max,
            minListPrice,
            m2_min)
        object_info = Booli_ScrapeObjects(
                                            url, object_info)
        numberOfPages, numberOfObjects = Booli_findNumberOfPagesData(
                                                                       url)
        for page in range(2, numberOfPages):
            url = "https: // www.booli.se/{}/{} /?"
            "maxListPrice = {}"
            "& maxLivingArea = {}"
            "& minListPrice = {}"
            "& minLivingArea = {}"
            "& objectType = L % C3 % A4genhet"
            "& page = {}"
            "& upcomingSale =".format(row["Region"],
                                      row["RegionID"],
                                      maxListPrice,
                                      m2_max,
                                      minListPrice,
                                      m2_min,
                                      page)
            object_info = Booli_ScrapeObjects(
                                                url, object_info)
            length.append(
                              len(object_info))
            #Creating a simple vector containing duplicates of regions up to number of object stored for each region
            for i in range(0, length[len(length)-1] - length[len(length) - 2]):
                region.append(
                              row["Region"])
                return object_info, region
