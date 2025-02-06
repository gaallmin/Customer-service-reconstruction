import pymysql
from sqlalchemy import create_engine

# Database connection
DATABASE_URL = "mysql+pymysql://ankh:ankh03013@localhost:3306/ankh_app_db?local_infile=1"
engine = create_engine(DATABASE_URL)

# Define your CSV file path
csv_file_path = "A://UNI//website//Customer-service-reconstruction//test_dataset.csv"

try:
        conn = engine.raw_connection()
        cursor = conn.cursor()
        query = f"""
        LOAD DATA LOCAL INFILE '{csv_file_path}'
        INTO TABLE user_feedback
        FIELDS TERMINATED BY ',' 
        ENCLOSED BY '"' 
        LINES TERMINATED BY '\n'
        IGNORE 1 LINES
        (id, reservation_opinion, health_issues, ankh_help);
        """
        cursor.execute(query)
        conn.commit()
        cursor.close()

        print("CSV data imported successfully.")
except Exception as e:
    print(f"Error: {e}")