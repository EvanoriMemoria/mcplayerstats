import psycopg2

def getDSN():
    with open('config.txt', 'r') as keyfile:
        for line in keyfile:
            if "dsn" in line:
                return line.rsplit("dsn: ", 1)[1]
            
        print("No Valid DSN")


def getTable():
    with open('config.txt', 'r') as keyfile:
        for line in keyfile:
            if "table" in line:
                return line.rsplit("table: ", 1)[1]
            
        print("No Valid Table")


def writeToDB(table, cursor, values):
    sql = "INSERT INTO %s (username, IPAddresses, totalLogins, totalLogouts, Playtime, PlaytimeHR) VALUES (%s %s %s %s %s %s)"
    cursor.execute(sql, (table, values[0], values[1], values[2], values[3], values[4], values[6] ))


def getDBValues(table, cursor, username):
    sql = "SELECT * FROM %s WHERE username = %s"
    entry = cursor.execute(sql, (table, username))


def updateValues(data):
    dsn = getDSN()
    table = getTable()
    connection = psycopg2.connect(dsn)
    cursor = connection.cursor()
    getDBValues(table, cursor, username)
    writeToDB(cursor)
    
