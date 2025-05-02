import sqlite3, os,json
from dotenv import load_dotenv
load_dotenv()
connection =sqlite3.connect(os.getenv('DB_NAME'), check_same_thread= False)
cursor = connection.cursor()


currentlist = []
with open('journal_entries.json', 'r') as file:
    q = json.load(file)
for item in q: 
    currentlist.append((item["user"], item["entry"], item["Date"]))
#cursor.execute("CREATE TABLE journals (id INTEGER PRIMARY KEY AUTOINCREMENT, user TEXT, entry TEXT, date TEXT)")
#cursor.executemany('INSERT INTO journals(user, entry, date) VALUES (?, ?, ?)', currentlist)
connection.commit()


def appendtodb(user, entry, date):
    tupy = (user, entry, date)
    cursor.execute(
        'INSERT INTO journals(user, entry, date) VALUES (?,?,?)', tupy
    )
    connection.commit()
def get_all_entries():
    cursor.execute("SELECT user, entry, date FROM journals ORDER BY id DESC")
    return [{"user": row[0], "entry": row[1], "timestamp": row[2]} for row in cursor.fetchall()]


connection.commit()
for row in cursor.execute("select * from journals"):
    print(row)



