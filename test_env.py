from dotenv import load_dotenv
import os
import psycopg2
load_dotenv()
print("HOST:", os.getenv("POSTGRES_HOST"))
print("USER:", os.getenv("POSTGRES_USER"))
print("PASS:", os.getenv("POSTGRES_PASSWORD"))
print("DB:  ", os.getenv("POSTGRES_DB"))
try:
    conn = psycopg2.connect("host=127.0.0.1 port=5432 dbname=georisk user=admin password=admin123 connect_timeout=10")
    print("SUCCESS — connected to Postgres")
    cur = conn.cursor()
    cur.execute("SELECT version();")
    print(cur.fetchone())
    conn.close()
except Exception as e:
    print("FAILED:", e)