![image](https://github.com/user-attachments/assets/1cdcdcba-7198-4a01-8997-862167c6ec88)

![image](https://github.com/user-attachments/assets/acc7574a-e3bb-485a-a160-da52dc494aca)

---

# Deribit Options Dashboard

This project connects to the Deribit API to collect real-time options data. It stores the data in a SQLite database and displays it on a web dashboard using Flask.

## Features

- Connects to Deribit REST and WebSocket APIs
- Collects option price, delta, and volatility
- Stores data in a local SQLite database
- Shows a live dashboard with charts and a data table

## Requirements

- Python 3.8 or higher
- Deribit API credentials

## Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/Shivam1456/DeribitOptionsTracker.git
   cd deribit-api-integration


2. Create and activate a virtual environment:

   ```bash
   python -m venv venv
   source venv/bin/activate  # For Linux/Mac
   venv\Scripts\activate     # For Windows
   ```

3. Install the required packages:

   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file based on `.env.example` and fill in your API details.

## Run the App

Start the application:

```bash
python main.py
```

Then open your browser and go to:

```
http://localhost:5000
```

## Notes

* Data is stored in a local file `deribit_data.db`
* Charts are generated using Plotly
* The dashboard shows the latest data and updates over time



