# MAIN ------
import pyodbc
# Connect function


def mssql_connect(server, database, driver):
    cnxn = pyodbc.connect('DRIVER='+driver
                          + ';SERVER='+server
                          + ';DATABASE='+database
                          + ';Trusted_Connection=yes')
    cursor = cnxn.cursor()
    return cnxn, cursor


# SQL INPUT PARAMETERS
pyodbc.pooling = False
server = 'localhost'
database = 'Booli'
username = 'senek'
password = 'senek'
driver = '{ODBC Driver 13 for SQL Server}'
cnxn, cursor = mssql_connect(server, database, username, password, driver)
data = result.values.tolist()
for i, item in enumerate(data):
    insert_query = "IF NOT EXISTS ( \
    SELECT \
    * \
    FROM \
    [Booli].[UpcomingSales] \
    WHERE \
    [Link] = '" + str(item[0]) + " ' AND    [DateInserted] = '"
    + str(date.today()) + "') \
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
        "','" + str(date.today()) + "') \
    END"
    cursor.execute(insert_query)
# Cleanup
cnxn.commit()
cursor.close()
cnxn.close()
