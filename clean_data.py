def cleaningData(object_info):
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
