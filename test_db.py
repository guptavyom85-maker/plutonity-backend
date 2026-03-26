# test_db.py
from supabase import create_client
from dotenv import load_dotenv
import os

# This reads your .env file and loads the variables
load_dotenv()

# Create the Supabase client using your keys
supabase = create_client(
    os.getenv("SUPABASE_URL"),
    os.getenv("SUPABASE_SERVICE_KEY")
)

# Try to read from leaderboard table
# It'll be empty but if it doesn't crash, connection works
result = supabase.table("leaderboard").select("*").execute()
print("Connection successful!")
print(f"Leaderboard rows: {len(result.data)}")