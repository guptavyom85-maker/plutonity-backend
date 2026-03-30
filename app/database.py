from supabase import create_client, Client
from dotenv import load_dotenv
import os

load_dotenv()

url = os.getenv("SUPABASE_URL")
service_key = os.getenv("SUPABASE_SERVICE_KEY")

supabase: Client = create_client(url, service_key)

# Force service role on every request
# This is what newer supabase-py versions require
supabase.postgrest.auth(service_key)