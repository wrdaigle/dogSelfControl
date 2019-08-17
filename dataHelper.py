import sqlite3, os, datetime

homePath = os.path.split(os.path.realpath(__file__))[0]
dbPath = os.path.join(homePath,'data','selfControlData.sqlite3')
con = None

def getConfigValue(configDesc):
    print(configDesc)
    con = sqlite3.connect(dbPath)
    cur = con.cursor()
    cur.execute('SELECT Value,Units from Configuration where Description = ?',(configDesc,))
    data = cur.fetchone()
    outDict = {'value':data[0],'units':data[1]}
    con.close
    return outDict

def setConfigValue(configDesc,value):
    con = sqlite3.connect(dbPath)
    cur = con.cursor()
    sqlStr = 'UPDATE Configuration SET Value = '+str(value)+ " where Description = '"+configDesc+"'"
    cur.execute(sqlStr)
    con.commit()
    con.close

def getAllConfigValuesAsDict():
    con = sqlite3.connect(dbPath)
    cur = con.cursor()
    cur.execute('SELECT Value, Description from Configuration')
    data = cur.fetchall()
    outDict = {}
    for item in data:
        outDict.setdefault(item[1],item[0])
    con.close
    return str(outDict)

def getAllConfigValuesAsString():
    return str(getAllConfigValuesAsDict())


def getDogList():
    con = sqlite3.connect(dbPath)
    cur = con.cursor()
    cur.execute('SELECT DogID, Name, Breed from Dog order by Name, Breed')
    data =cur.fetchall()
    dogList = []
    for row in data:
        dogList.append(row[1]+' - '+row[2]+' ('+str(row[0])+')')
    con.close()
    return dogList

def dogyAlreadyRegistered(name, breed):
    con = sqlite3.connect(dbPath)
    cur = con.cursor()
    cur.execute("SELECT * from Dog where name = '"+name+"' and breed = '"+breed+"'")
    data =cur.fetchall()
    con.close()
    if len(data)>0:
        return False
    return True

def getAffilliationList():
    con = sqlite3.connect(dbPath)
    cur = con.cursor()
    cur.execute('SELECT * from AffiliationLU')
    data =cur.fetchall()
    affiliationList = []
    for row in data:
        affiliationList.append(row[0])
    con.close()
    return affiliationList

def getDogData(dogID):
    con = sqlite3.connect(dbPath)
    cur = con.cursor()
    cur.execute('SELECT Name,Breed,Large_reward_side from Dog where dogID = '+dogID)
    data =cur.fetchall()
    dogData = data[0]
    con.close()
    return dogData

def addDogRecord(dogName,dogBreed,dogAge,affiliation):
    con = sqlite3.connect(dbPath)
    cur = con.cursor()
    cur.execute(
        """
            INSERT INTO Dog (
                    Name,
                    Registration_Date,
                    Breed,
                    Age_at_registration,
                    Affiliation,
                    Large_reward_side
            )
            VALUES (
                '"""+dogName+"""',
                DATETIME('now'),
                '"""+dogBreed+"""',
                '"""+str(dogAge)+"""',
                '"""+affiliation+"""',
                '"""+random.choice(['left','right'])+"""'
            )
        """
    )
    con.commit()
    con.close()

def logNewTrialRecord(dogId,recorders,hoursSinceLastFeeding):
    con = sqlite3.connect(dbPath)
    cur = con.cursor()
    cur.execute(
        """
            Insert into Trial
                (DogID, StartTime,Recorders, Configurations,HoursSinceLastFeeding)
                VALUES (?,?,?,?,?)
        """,
        (dogId,datetime.datetime.now(),recorders,getAllConfigValuesAsString(),hoursSinceLastFeeding)
    )
    trialId = cur.lastrowid
    con.commit()
    con.close()
    return trialId

def logEvent(trialId,eventType):
    con = sqlite3.connect(dbPath)
    cur = con.cursor()
    cur.execute(
        """
            Insert into Event
                (TrialID, Type,Time)
                VALUES (?,?,?)
        """,
        (trialId,eventType,datetime.datetime.now())
    )
    eventId = cur.lastrowid
    con.commit()
    con.close()
    return eventId
##connection=sqlite3.connect(':memory:')
##cursor=connection.cursor()
##cursor.execute('''CREATE TABLE foo (id integer primary key autoincrement ,
##                                    username varchar(50),
##                                    password varchar(50))''')
##cursor.execute('INSERT INTO foo (username,password) VALUES (?,?)',
##               ('test','test'))
##print(cursor.lastrowid)