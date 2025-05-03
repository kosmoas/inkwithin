from flask import( Flask, render_template, jsonify, request, json,
                   flash, get_flashed_messages, session, redirect)
import requests, datetime, entriesdb, os
from dotenv import load_dotenv
load_dotenv()
back = Flask(__name__)
back.secret_key = os.getenv('FLASH_KEY', 'devkey')
entrielist = []
def load_entries():
    try:
        with open('journal_entries.json', 'r') as journal:
            entrielist = json.load(journal)
    except (FileNotFoundError):
        entrielist = []
    return entrielist
def save_entries(newlist):
        with open('journal_entries.json', 'w') as journal:
            json.dump(newlist, journal, indent = 4)

@back.route('/')
def home():
    return render_template('journal.html')
@back.route('/api/journal', methods =['POST'])
def journal_page():
    data = request.json # now that I have the data I want to append it to both the entrylist and the file
    listt = load_entries() #loading entries from the json
    listt.append(data) #adding entries to the json
    with open('journal_entries.json', 'w') as entries: #open the file   
        json.dump(listt, entries) #load it onto the file
    return jsonify({'status': 'yes'})
@back.route('/theme') #maybe set this to like a little widget in the future
def theme_page():
    pass
@back.route('/dashboard')
def dashpage():
    entrielist = entriesdb.get_all_entries()
    return render_template('dashboard.html', entries = entrielist)
@back.route('/new', methods = ['POST','GET']) #looking out for post methods or get methos
def new_page():
    entry = ''
    if request.method == 'POST':
        entry = request.form.get('journal')
        if entry:
                entries = load_entries()
                data = {
                    'Date': datetime.datetime.now().strftime('%B %d, %Y at %I:%M %p'),
                    'user': 'Anon',
                    'entry': entry
                }
                entries.append(data)
                entriesdb.appendtodb(data['user'], data['entry'], data['Date'])
                save_entries(entries)
                flash("✅ Your journal was saved successfully!")
                return redirect("/dashboard")

    return render_template('newentry.html', entry = request.form.get('journal'))
if __name__ == '__main__':
    back.run(debug=True)