Inkel Tourism Agent AI 🌏

A smart, friendly travel agent web app built with Flask — get instant weather updates, top places to visit, and embedded maps for any destination!

Features

- ✈️ Predicts weather and recommends top tourist spots for any city
- 📍 Shows interactive maps for each location and attraction (powered by OpenStreetMap)
- 💬 Chat-based interface with user accounts
- 🔥 Modern, responsive design with Clear Chat functionality
- 🧳 Easy to use — just type your destination and let the AI guide you

Setup

1. Clone the repository:
    ```
    git clone https://github.com/YOUR-USERNAME/inkel-tourism-agent.git
    cd inkel-tourism-agent
    ```

2. Install dependencies:
    ```
    pip install -r requirements.txt
    ```

3. Run the app:
    ```
    python app.py
    ```
    Now go to [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

 Usage

- Register/Login to start chatting
- Ask about cities:  
  `I'm going to Delhi, what should I visit?`  
  `What's the temperature in Bangalore?`
- Click "View on Map" and see embedded maps for each destination and attraction

 API & Technology

- Flask & Flask-Login (Python)
- OpenStreetMap Nominatim for geocoding and maps
- Custom weather and places agents
- Bootstrap, CSS, FontAwesome for UI
