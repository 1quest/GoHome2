def mssql_connect(server, database, driver):
    cnxn = pyodbc.connect('DRIVER='+driver
                          + ';SERVER='+server
                          + ';DATABASE='+database
                          + ';Trusted_Connection=yes')


cursor = cnxn.cursor()
return cnxn, cursor
