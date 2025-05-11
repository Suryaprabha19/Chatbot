
# 🧠 Smart Clothing Data Insights App
- This is an interactive Flask-based web application designed to analyze and visualize sales data from a clothing dataset. It integrates chat-based SQL querying, sales prediction with machine learning, and live map updates for location-based insights.

## 🚀 Features
- 💬 Chatbot Interface: Ask questions in natural language and get instant insights from the database.
- 📈 Sales Prediction: Predict future sales using a Linear Regression model.
- 🗺️ Live Map: Visualize geographic data with auto-updating Folium maps.
- 📊 Dashboard: View charts and sales data for better analysis.


🔧 Setup Instructions
1. Clone the Repository
```
git clone https://github.com/yourusername/chatbot.git

```

2. Install Required Packages
```
pip install flask pandas openai scikit-learn folium
```

3. Configure OpenAI API Key
Edit app.py:
```
openai.api_key = 'your-api-key-here'
```

In app.py:
```
import os
openai.api_key = os.getenv("OPENAI_API_KEY")
```

4. Run the Application
```
python app.py
```
Open in browser:
```
http://127.0.0.1:5000
```

🗺️ Map Integration
- Built with Folium
- Auto-refreshes every 60 seconds via background thread

✅ requirements.txt
```
flask
pandas
openai
scikit-learn
folium
```
