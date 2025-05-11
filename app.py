from flask import Flask, render_template, request, jsonify
import pandas as pd
import sqlite3
import openai
import os
import re
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
import folium
import time
import threading

app = Flask(__name__)

# Load your Excel data into the SQLite database
def load_data_to_db():
    excel_file_path = 'final_data.xlsx'
    database_path = 'data.db'
    table_name = 'Clothes'

    try:
        df = pd.read_excel(excel_file_path)
        conn = sqlite3.connect(database_path)
        df.to_sql(table_name, conn, if_exists='replace', index=False)
        conn.close()
        print("Data successfully loaded to the database.")
    except Exception as e:
        print(f"Error loading data to database: {e}")

load_data_to_db()

# Setup OpenAI API key from environment variable
openai.api_key = 'sk-proj-Hke1plcwJpNsbomSebWhT3BlbkFJOtDprEot4uEPYyeoPibB'  # Use environment variable for security

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/sales')
def sales():
    return render_template('sales.html')

@app.route('/map')
def map():
    return render_template('map.html')

@app.route('/charts')
def charts():
    return render_template('charts.html')

@app.route('/chat', methods=['POST'])
def chat():
    user_message = request.json.get('message')
    print(f"Received user message: {user_message}")  # Debug log

    try:
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that generates accurate SQL queries from natural language requests. If the user asks for data, ensure to include all relevant columns or specify how to handle the request. Use the Clothes table."},
                {"role": "user", "content": user_message},
                {"role": "assistant", "content": "Please convert the above message into a valid SQL query to retrieve data from the Clothes table. Make sure to include all relevant columns unless specified otherwise. If a specific column is requested, ensure the query includes that column only. Adjust column names and values to match the database schema."}
            ]
        )

        # Extract and clean the SQL query
        sql_query = response['choices'][0]['message']['content']
        sql_query = re.search(r'SELECT.*?(?:;|$)', sql_query, re.DOTALL)

        if sql_query:
            sql_query = sql_query.group(0).strip()
        else:
            return jsonify({'error': 'No valid SQL query found in response.'})

        print(f"Generated SQL query: {sql_query}")  # Debug log

        # Normalize the case of column names and values in the SQL query
        normalized_query = normalize_query(sql_query)
        print(f"Normalized SQL query: {normalized_query}")  # Debug log

        try:
            conn = sqlite3.connect('data.db')
            cursor = conn.cursor()
            cursor.execute(normalized_query)
            rows = cursor.fetchall()
            columns = [description[0] for description in cursor.description]
            conn.close()

            print(f"Query results: {rows}")  # Debug log

            if rows:
                data = [dict(zip(columns, row)) for row in rows]
                bot_response = jsonify({'results': data})
            else:
                bot_response = jsonify({'results': []})

        except sqlite3.Error as e:
            bot_response = jsonify({'error': f"An error occurred while querying the database: {e}"})

    except openai.OpenAIError as e:
        bot_response = jsonify({'error': f"An error occurred with OpenAI: {e}"})

    print(f"Bot response: {bot_response.get_json()}")  # Debug log
    return bot_response

def normalize_query(query):
    """
    Normalize the SQL query to ensure it matches the case of the database schema and values.
    """
    conn = sqlite3.connect('data.db')
    cursor = conn.cursor()

    # Get table info to fetch column names
    cursor.execute("PRAGMA table_info(Clothes)")
    columns_info = cursor.fetchall()

    # Fetch unique values for each column to normalize the case of the values
    columns = [info[1] for info in columns_info]
    column_values = {col: fetch_column_values(cursor, col) for col in columns}

    conn.close()

    normalized_columns = {col.lower(): col for col in columns}

    def replace_column_names(match):
        col = match.group(0)
        return normalized_columns.get(col.lower(), col)

    def replace_column_values(match):
        val = match.group(0).strip("'\"")
        val = str(val)  # Convert value to string
        for col, values in column_values.items():
            for v in values:
                if str(v).lower() == val.lower():  # Convert v to string before comparison
                    return f"'{v}'"
        return f"'{val}'"

    # Normalize column names in the query
    query = re.sub(r'\b[a-z_]+\b', replace_column_names, query, flags=re.IGNORECASE)

    # Normalize column values in the query
    query = re.sub(r"'.*?'", replace_column_values, query)

    return query

def fetch_column_values(cursor, column_name):
    """
    Fetch unique values for a given column from the database.
    """
    cursor.execute(f"SELECT DISTINCT {column_name} FROM Clothes")
    values = [row[0] for row in cursor.fetchall()]
    return values

@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    df = get_data()

    # Ensure required columns exist
    required_columns = ['quantity_sold', 'discount', 'profit', 'launch_month', 'rating']
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        return jsonify({'error': f"Missing columns in data: {missing_columns}"})

    # Prepare data for prediction
    X = df[['quantity_sold', 'discount', 'profit', 'launch_month', 'rating']]
    y = df['sales_amount']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LinearRegression()
    model.fit(X_train, y_train)

    # Convert month name to number
    launch_month_number = month_to_number(data['launch_month'])
    if launch_month_number is None:
        return jsonify({'error': 'Invalid month name'})

    # Prepare input data for prediction
    input_data = [
        [
            float(data['quantity_sold']),
            float(data['discount']),
            float(data['profit']),
            float(launch_month_number),
            float(data['rating'])
        ]
    ]

    # Ensure input_data is in numeric format
    input_data = pd.DataFrame(input_data, columns=['quantity_sold', 'discount', 'profit', 'launch_month', 'rating'])

    # Check for any non-numeric values
    for col in input_data.columns:
        input_data[col] = pd.to_numeric(input_data[col], errors='coerce')

    prediction = model.predict(input_data)[0]

    return jsonify({'prediction': prediction})

def get_data():
    conn = sqlite3.connect('data.db')
    query = "SELECT sales_amount, quantity_sold, discount, profit, launch_month, rating FROM Clothes"
    df = pd.read_sql_query(query, conn)
    
    # Convert month names to numbers
    df['launch_month'] = df['launch_month'].map(month_to_number)
    
    conn.close()
    return df

def month_to_number(month_name):
    months = {
        'January': 1,
        'February': 2,
        'March': 3,
        'April': 4,
        'May': 5,
        'June': 6,
        'July': 7,
        'August': 8,
        'September': 9,
        'October': 10,
        'November': 11,
        'December': 12
    }
    return months.get(month_name, None)

def get_data_from_db():
    """Fetch latitude and longitude data from the database."""
    conn = sqlite3.connect('data.db')
    query = "SELECT Latitude, Longitude FROM Clothes"
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def create_map(df):
    """Create a map with markers from the DataFrame."""
    m = folium.Map(location=[df['Latitude'].mean(), df['Longitude'].mean()], zoom_start=10)
    for index, row in df.iterrows():
        folium.Marker([row['Latitude'], row['Longitude']]).add_to(m)
    return m

def update_map():
    while True:
        try:
            # Fetch the latest data from the database
            df = get_data_from_db()

            # Create the map
            m = create_map(df)

            # Save the map to an HTML file
            m.save('templates/map.html')

            # Print a message to indicate that the map has been updated
            print("Map updated.")

        except Exception as e:
            print(f"Error updating map: {e}")

        # Wait for a specified interval before updating again (e.g., 60 seconds)
        time.sleep(60)

# Start map updating in a separate thread
threading.Thread(target=update_map, daemon=True).start()

if __name__ == '__main__':
    app.run(debug=True)
