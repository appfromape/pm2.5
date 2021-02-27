# you have to pip install requests and beautifulsoup4 to get it work.
import sqlite3, ast, hashlib, os, requests
from bs4 import BeautifulSoup


# create and connect database to store pm2.5 data.
conn = sqlite3.connect("DataBasePM25.sqlite")
cursor = conn.cursor()


# create a data table, name is "TablePM25" inside has 3 items : "no", "SiteName", "PM25".
sqlstr = '''
CREATE TABLE IF NOT EXISTS TablePM25 ("no" INTEGER PRIMARY KEY AUTOINCREMENT 
NOT NULL UNIQUE ,"SiteName" TEXT NOT NULL ,"PM25" INTEGER)
'''
cursor.execute(sqlstr)


# this url work for now, in the future have to pay $ to connect the api.
url = "http://opendata2.epa.gov.tw/AQI.json"

# read the pm2.5 website's html source code and check web id already update or not.
html = requests.get(url).text.encode("utf-8")
new_md5 = hashlib.md5(html).hexdigest()

old_md5 = ""

if os.path.exists("old_md5.txt"):

    with open("old_md5.txt", "r") as file:
        old_md5 = file.read()

with open("old_md5.txt", "w") as file:
    file.write(new_md5)

# use ast.literal_eval() transform website data to json data.
# use execute() to delete data from TablePM25 in sqlite database.
if new_md5 != old_md5:
    
    print("Data already updated...")
    
    sp = BeautifulSoup(html, "html.parser")
    jsondata = ast.literal_eval(sp.text)
    conn.execute("delete from TablePM25")
    conn.commit()
    
    n = 1
    for site in jsondata:
        
        SiteName = site["SiteName"]
        
        PM25 = int(site["PM2.5"])
        print("地點:{}   PM2.5: {}".format(SiteName, PM25))
        
        sqlstr = "insert into TablePM25 values({},'{}',{})" .format(n, SiteName, PM25)
        cursor.execute(sqlstr)
        n += 1
        conn.commit()
    
else:
    print('website not update, data form the old databse...') 
    cursor = conn.execute("select * from TablePM25")
    rows = cursor.fetchall()
    
    for row in rows:
        print("地點:{}   PM2.5: {}".format(row[1],row[2]))    

conn.close()
