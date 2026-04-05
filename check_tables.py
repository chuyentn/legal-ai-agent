import os, psycopg2
from dotenv import load_dotenv

load_dotenv()

host = os.getenv('SUPABASE_DB_HOST')
pwd = os.getenv('SUPABASE_DB_PASSWORD')
is_pooler = 'pooler' in host.lower()

conn = psycopg2.connect(
    host=host,
    port=6543 if is_pooler else 5432,
    dbname='postgres',
    user='postgres.cjkrsnqdsfucngmrsnpm' if is_pooler else 'postgres',
    password=pwd,
    sslmode='require'
)

cur = conn.cursor()

# List all tables
cur.execute("""
    SELECT table_name FROM information_schema.tables 
    WHERE table_schema = 'public'
    ORDER BY table_name
""")

tables = cur.fetchall()
print('Tables in database:')
if tables:
    for t in tables:
        print(f'  {t[0]}')
else:
    print('  (NONE - need to initialize!)')

conn.close()
