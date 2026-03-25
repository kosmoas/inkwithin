from flask import( Flask, render_template, jsonify, request, json,
                   flash, get_flashed_messages, session, redirect, url_for)
import requests, datetime, os
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from dotenv import load_dotenv
from aihelp import generate_prompt
from journal_service import create_journal_entry
load_dotenv()
back = Flask(__name__)
back.secret_key = os.getenv('FLASH_KEY', 'devkey')
entrielist = []

DISCORD_CLIENT_ID = os.getenv("DISCORD_CLIENT_ID")
DISCORD_CLIENT_SECRET = os.getenv("DISCORD_CLIENT_SECRET")
DISCORD_REDIRECT_URI = os.getenv("DISCORD_REDIRECT_URI")
API_BASE_URL = "https://discord.com/api"
AUTH_BASE_URL = f"{API_BASE_URL}/oauth2/authorize"
TOKEN_URL = f"{API_BASE_URL}/oauth2/token"
USER_URL = f"{API_BASE_URL}/users/@me"
DISCORD_OAUTH_URL = f"https://discord.com/api/oauth2/authorize?client_id={DISCORD_CLIENT_ID}&redirect_uri={DISCORD_REDIRECT_URI}&response_type=code&scope=identify"
back.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
back.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
userbase = SQLAlchemy(back)
class User(userbase.Model):
    id = userbase.Column('id',userbase.Integer, primary_key=True)
    username = userbase.Column('username',userbase.String(80), unique=True, nullable=False)
    password = userbase.Column('password',userbase.String(200), nullable=False)
class journalent(userbase.Model):
    id = userbase.Column('id',userbase.Integer, primary_key=True)
    user_id = userbase.Column('User_id', userbase.Integer, nullable = False)
    content = userbase.Column('Content', userbase.Text, nullable = False)
    date = userbase.Column('Date', userbase.String(100), nullable = False)
    tag = userbase.Column('Tag', userbase.String(100), nullable = True)
    source = userbase.Column('Source', userbase.String(50), nullable = False, default = 'web')
    ai_mood = userbase.Column(userbase.String(100), nullable=True)
    ai_reflection = userbase.Column(userbase.Text, nullable=True)
    ai_follow_up = userbase.Column(userbase.Text, nullable=True)
with back.app_context():
    userbase.create_all()
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
    return redirect('/login')
@back.route('/api/journal', methods=['POST'])
def journal_page():
    data = request.get_json()

    username = data.get('user')
    content = data.get('entry')
    discord_id = data.get('id')
    tag = data.get('tag')

    if not username or not content or not discord_id:
        return jsonify({'error': 'Missing required fields'}), 400

    discord_id = int(discord_id)

    existing_user = User.query.filter_by(id=discord_id).first()

    if not existing_user:
        new_user = User(
            username=username,
            id=discord_id,
            password=generate_password_hash(str(discord_id))
        )
        userbase.session.add(new_user)
        userbase.session.commit()
        current_user = new_user
    else:
        current_user = existing_user

    try:
        saved_entry = create_journal_entry(
            db=userbase,
            journal_model=journalent,
            user_id=current_user.id,
            content=content,
            tag=tag,
            source="discord"
        )

        return jsonify({
            'status': 'saved',
            'entry_id': saved_entry.id,
            'mood': saved_entry.ai_mood,
            'reflection': saved_entry.ai_reflection,
            'follow_up': saved_entry.ai_follow_up,
            'source': saved_entry.source
        }), 200

    except Exception as e:
        return jsonify({'error': str(e)}), 500
@back.route('/login/discord')
def discord_login():
    return redirect(DISCORD_OAUTH_URL)
@back.route("/callback")
def discord_callback():
    code = request.args.get("code") #pulls out the auth code when a user goes to authorize
    tokens = requests.post( #sends a post request to this endpoint to exchange the code for an acess token and refresh
        "https://discord.com/api/oauth2/token",
        data={
            "client_id": DISCORD_CLIENT_ID,
            "client_secret": DISCORD_CLIENT_SECRET,
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": DISCORD_REDIRECT_URI,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"}
    )

    token_json = tokens.json() # converts the tokens into a json that I can read
    access_token = token_json["access_token"] #grabs the access token that was requested

    # Get user info like name and pfp
    user_response = requests.get( 
        "https://discord.com/api/users/@me",
        headers={"Authorization": f"Bearer {access_token}"}
    )

    user_info = user_response.json()
    discord_username = user_info["username"]
    discord_id = user_info["id"]

    # stores the current sessions userid and username to discord
    session["user_id"] = discord_id
    session["username"] = discord_username
    # Check if user exists
    existing_user = User.query.filter_by(id=discord_id).first()

    if not existing_user:
        new_user = User(
            username=discord_username,
            id=discord_id,
            password=generate_password_hash(discord_id) 
    )
        userbase.session.add(new_user)
        userbase.session.commit()
        session['user_id'] = new_user.id
    else:
        session['user_id'] = existing_user.id

    return redirect("/dashboard")

@back.route('/register', methods = ['POST', 'GET'])
def register():
     if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username = username).first():
             flash('Sorry this username already exist')
             return redirect('/register')
        hashpass = generate_password_hash(password)
        new_user = User(username = username, password = hashpass)
        userbase.session.add(new_user)
        userbase.session.commit()
        flash('You have sucessfully made a new account!')
        return redirect('/login')
     return render_template('register.html')
@back.route('/login', methods = ['POST', 'GET'])
def login():
     if request.method == 'POST':
          username = request.form['username']
          password = request.form['password']
          user = User.query.filter_by(username = username).first()
          if user and check_password_hash(user.password, password):
                session['user_id'] = user.id
                flash('Logged in!')
                return redirect('/dashboard')
          else:
               flash('Sorry incorrect credentials')
               return redirect('/login')
     return render_template('login.html')
@back.route('/logout')
def logout():
     session.pop('user_id', None)
     flash('You have been logged out 🎈')
     return redirect('/login')
@back.route('/edit/<entry_id>', methods = ['GET','POST'])
def edit(entry_id):
    entry = journalent.query.get_or_404(entry_id)
    if entry.user_id != session['user_id']:
        flash('You are not allowed to edit this')
        return redirect('/login')
    if request.method == 'POST':
        entry.content = request.form['content']
        userbase.session.commit()
        flash('You have sucessfully changed it')
        return redirect('/dashboard')
    return render_template('edit_entry.html', entry = entry)
@back.route('/delete/<entry_id>', methods = ['GET','POST'])
def delete_entry(entry_id):
    entry = journalent.query.get_or_404(entry_id)
    if entry.user_id != session['user_id']:
        flash("You are not allowed to delete this")
        return redirect('/dashboard')
    userbase.session.delete(entry)
    userbase.session.commit()
    flash('You have sucessfully deleted the entry')
    return redirect('/dashboard')
     
@back.route('/dashboard')
def dashpage():
    user_id = session.get('user_id')
    if not user_id:
         flash('Sorry please login first')
         redirect('/login')
    user = User.query.get(user_id)
    if not user:
        session.pop('user_id', None)
        flash("Your session expired or user no longer exists. Please log in again.")
        return redirect('/login')
    

    selected_tag = request.args.get('tag')
    search_query = request.args.get('query')
    query = journalent.query.filter(journalent.user_id == user_id)
    if search_query:
       query = query.filter(journalent.content.ilike(f"%{search_query}%"))
    if selected_tag:
        query = journalent.query.filter_by(user_id = user_id, tag = selected_tag.capitalize())
  
    user = User.query.get(user_id)
    entrielist = query.all()
    
    return render_template('dashboard.html', entries = entrielist, user_id = user.username)
@back.route('/new', methods=['POST', 'GET']) #looks for get and post requests
def new_page():
    if 'user_id' not in session:
        flash('You must be logged in to create a message')
        return redirect('/login')

    if request.method == 'POST':
        entry = request.form.get('journal', '').strip()
        tag = request.form.get('tag')

        if not entry:
            flash('Please write something before saving.')
            return redirect('/new')

        try:
            create_journal_entry(
                db=userbase,
                journal_model=journalent,
                user_id=session['user_id'],
                content=entry,
                tag=tag,
                source="web"
            )
            flash("✅ Your journal was saved successfully!")
            return redirect('/dashboard')
        except Exception as e:
            flash(f"Something went wrong while saving your entry: {e}")
            return redirect('/new')

    return render_template('new_entry.html')
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    back.run(debug = True, host = '0.0.0.0', port = port)
