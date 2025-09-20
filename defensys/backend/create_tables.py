from api.database import engine, Base
from api.models import Project, Scan, Vulnerability
import time

# It might take a few seconds for the database container to be ready to accept connections.
# We'll add a small delay and a retry loop.
max_retries = 5
retry_delay = 5
for attempt in range(max_retries):
    try:
        print(f"Attempting to connect to the database (Attempt {attempt + 1}/{max_retries})...")
        # The connection is implicitly tested when create_all is called.
        Base.metadata.create_all(bind=engine)
        print("Tables created successfully!")
        break # Exit the loop if successful
    except Exception as e:
        print(f"Database connection failed: {e}")
        if attempt < max_retries - 1:
            print(f"Retrying in {retry_delay} seconds...")
            time.sleep(retry_delay)
        else:
            print("Could not connect to the database after several retries. Please check if the database container is running and accessible.")
            exit(1)
