import sqlite3, os,json
connection =sqlite3.connect("journals.db", check_same_thread= False)
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


connection.commit()
for row in cursor.execute("select * from journals"):
    print(row)



