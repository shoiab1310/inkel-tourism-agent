from flask import Flask, render_template, redirect, url_for, request, session, flash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from models import db, User, ChatMessage
from agents.geocode_agent import get_coordinates
from agents.weather_agent import get_weather, get_forecast
from agents.places_agent import get_places

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite'
db.init_app(app)

login_manager = LoginManager()
login_manager.init_app(app)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash('Username already exists')
            return redirect(url_for('register'))
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        login_user(new_user)
        return redirect(url_for('chat'))
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            login_user(user)
            return redirect(url_for('chat'))
        flash('Login Failed! Check your username and password.')
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

import re

def extract_place(text):
    """
    Extract city or place from input sentence with improved pattern matching.
    Handles queries like:
    - "what's the temperature in bangalore"
    - "suggest top 5 places in delhi"
    - "weather in mumbai"
    - "places to visit in goa"
    """
    # Convert to lowercase for easier matching
    text_lower = text.lower()
    
    # Remove common question words and phrases
    text_clean = re.sub(r'\b(what\'?s?|whats|how|is|the|are|there|can|you|suggest|show|me|tell|about|give|top|best|\d+)\b', '', text_lower)
    
    # Pattern 1: Look for "in/at/to/from" followed by a location
    match = re.search(r'\b(?:in|at|to|from|for|of)\s+([a-z]+(?:\s+[a-z]+)?)', text_clean, re.IGNORECASE)
    if match:
        place = match.group(1).strip()
        if len(place) > 2:  # Avoid single letters or very short matches
            return place.title()
    
    # Pattern 2: Look for capitalized words (likely place names)
    words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', text)
    if words:
        # Return the longest capitalized phrase (likely the place name)
        return max(words, key=len)
    
    # Pattern 3: Look for any remaining words that might be places (after cleaning)
    remaining_words = text_clean.split()
    # Filter out common words and keep potential place names
    stop_words = {'weather', 'temperature', 'places', 'visit', 'go', 'trip', 'travel', 'plan', 
                  'attraction', 'tourist', 'see', 'explore', 'find', 'looking', 'want', 'need'}
    potential_places = [w for w in remaining_words if w not in stop_words and len(w) > 2]
    
    if potential_places:
        # Return the last significant word (usually the place name)
        return potential_places[-1].title()
    
    # Fallback: return cleaned text
    return text.strip().title()


def extract_number(text):
    """
    Extract numbers from text like "top 5 places" or "suggest 10 attractions"
    """
    match = re.search(r'\b(\d+)\b', text)
    if match:
        return int(match.group(1))
    return 5  # Default to 5

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('chat'))
    else:
        return redirect(url_for('login'))
    
@app.route('/clear_chat', methods=['POST'])
@login_required
def clear_chat():
    ChatMessage.query.filter_by(user_id=current_user.id).delete()
    db.session.commit()
    flash("Your chat history was cleared!", "info")
    return redirect(url_for('chat'))


@app.route('/')
@app.route('/chat', methods=['GET', 'POST'])
@login_required
def chat():
    if request.method == 'POST':
        user_input = request.form.get('chat_input', '').strip()
        
        if not user_input:
            messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp).all()
            return render_template('chat.html', username=current_user.username, messages=messages)
        
        # Extract place and intent
        place = extract_place(user_input)
        num_places = extract_number(user_input)
        response = ""
        
        # Get coordinates
        location = get_coordinates(place) if place else None

        # Handle unknown place
        if not location:
            response = f"Sorry, I couldn't find '{place}'. Please try another city or landmark."
            db.session.add(ChatMessage(user_id=current_user.id, sender='user', text=user_input))
            db.session.add(ChatMessage(user_id=current_user.id, sender='ai', text=response))
            db.session.commit()
            messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp).all()
            return render_template('chat.html', username=current_user.username, messages=messages)

        session['last_place'] = place
        lat = location["lat"]
        lon = location["lon"]

        # Determine user intent with improved keyword matching
        user_lower = user_input.lower()
        
        # Check for weather-related keywords
        weather_keywords = ['weather', 'temperature', 'temp', 'forecast', 'climate', 'hot', 'cold', 'rain', 'sunny']
        wants_weather = any(keyword in user_lower for keyword in weather_keywords)
        
        # Check for places-related keywords
        places_keywords = ['place', 'places', 'attraction', 'attractions', 'visit', 'see', 'go', 'tourist', 
                          'sightseeing', 'explore', 'destination', 'destinations', 'spot', 'spots', 'recommend', 
                          'suggest', 'suggestion', 'top', 'best']
        wants_places = any(keyword in user_lower for keyword in places_keywords)

        # Handle different intents
        if wants_weather and not wants_places:
            weather = get_weather(lat, lon)
            if weather:
                map_iframe = (
            f"<iframe src='https://www.openstreetmap.org/export/embed.html?bbox={lon - 0.03},{lat - 0.03},{lon + 0.03},{lat + 0.03}&layer=mapnik&marker={lat},{lon}' "
            f"style='width:100%; height:250px; border:1px solid #ccc; margin-bottom:12px;' loading='lazy'></iframe>"
        )
                response = (
            f"🌤️ In {place}, it's currently {weather['temperature']}°C with a {weather['rain_chance']}% chance of rain.<br>"
            f"{map_iframe}"
        )
            else:
                response = f"Sorry, I couldn't retrieve weather information for {place} right now."


        elif wants_places and not wants_weather:
            # Places only
            places = get_places(lat, lon)
            if places:
                places = places[:num_places]
                top_places_html = []
                for i, p in enumerate(places):
                    item = f"{i + 1}. {p['name']}"
                    if p.get('lat') and p.get('lon'):
                        place_map = (
                f"<iframe src='https://www.openstreetmap.org/export/embed.html?bbox={p['lon'] - 0.01},{p['lat'] - 0.01},{p['lon'] + 0.01},{p['lat'] + 0.01}"
                f"&layer=mapnik&marker={p['lat']},{p['lon']}' style='width:100%; height:160px; border:1px solid #ccc; margin-bottom:10px;' loading='lazy'></iframe>"
            )
                        item += f"<br>{place_map}"
                    top_places_html.append(item)
                places_list = "<br><br>".join(top_places_html)
                response = f"📍 Top {len(places)} places to visit in {place}:<br><br>{places_list}"
            else:
                response = f"Sorry, I couldn't find tourist attractions for {place}."


        elif wants_weather and wants_places:
            # Both weather and places
            weather = get_weather(lat, lon)
            places = get_places(lat, lon)
            
            weather_txt = ""
            if weather:
                weather_txt = f"🌤️ In {place}, it's currently {weather['temperature']}°C with a {weather['rain_chance']}% chance of rain.\n\n"
            
            places_txt = ""
            if places:
                places = places[:num_places]
                places_list = "\n".join([f"{i+1}. {p['name']}" for i, p in enumerate(places)])
                places_txt = f"📍 Top {len(places)} places to visit:\n{places_list}"
            
            response = weather_txt + places_txt
            if not response:
                response = f"Sorry, I couldn't retrieve information for {place} right now."

        else:
            # Default: Show places if no specific intent detected
            places = get_places(lat, lon)
            if places:
                places = places[:num_places]
                places_list = "\n".join([f"{i+1}. {p['name']}" for i, p in enumerate(places)])
                response = f"📍 Top {len(places)} places to visit in {place}:\n{places_list}"
            else:
                response = f"I found {place}! What would you like to know? You can ask about weather or places to visit."

        # Save to database
        db.session.add(ChatMessage(user_id=current_user.id, sender='user', text=user_input))
        db.session.add(ChatMessage(user_id=current_user.id, sender='ai', text=response))
        db.session.commit()

    messages = ChatMessage.query.filter_by(user_id=current_user.id).order_by(ChatMessage.timestamp).all()
    return render_template('chat.html', username=current_user.username, messages=messages)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)