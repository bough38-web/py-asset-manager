import pandas as pd
import sqlite3

def export_to_csv():
    # Connect to the SQLite database
    conn = sqlite3.connect('assets.db')
    
    # Read the data into a DataFrame
    try:
        df = pd.read_sql_query("SELECT * FROM assets", conn)
        
        # Save to CSV
        df.to_csv('local_data.csv', index=False)
        print(f"Successfully exported {len(df)} records to local_data.csv")
    except Exception as e:
        print(f"Error exporting data: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    export_to_csv()
