import sqlite3

con = sqlite3.connect("jarvis.db")
cursor = con.cursor()
"""
query = "CREATE TABLE IF NOT EXISTS sys_command(id integer primary key, name VARCHAR(100), path VARCHAR(1000))"
cursor.execute(query)

query = "CREATE TABLE IF NOT EXISTS web_command(id integer primary key, name VARCHAR(100), url VARCHAR(1000))"
cursor.execute(query)

query = "INSERT INTO web_command VALUES (null,'youtube', 'https://www.youtube.com/')"
cursor.execute(query)
con.commit()

query = "CREATE TABLE IF NOT EXISTS contacts(id integer primary key, name VARCHAR(200), mobile_no VARCHAR(255), email VARCHAR(255) NULL, address VARCHAR(255) NULL)"
cursor.execute(query)

# Import contacts from CSV
import csv
desired_columns_indices = [0, 18]  # Adjust indices based on CSV columns (name, mobile_no)
try:
    with open('contactss.csv', 'r', encoding='utf-8') as csvfile:
        csvreader = csv.reader(csvfile)
        next(csvreader)  # Skip header if present
        for row in csvreader:
            if len(row) > max(desired_columns_indices):
                selected_data = [row[i] for i in desired_columns_indices]
                cursor.execute('''INSERT INTO contacts (id, name, mobile_no) VALUES (null, ?, ?)''', tuple(selected_data))
    con.commit()
except Exception as e:
    print(f"Error importing contacts: {e}")
"""
def get_sys_commands():
    cursor.execute("SELECT name, path FROM sys_command")
    return {row[0].lower(): row[1] for row in cursor.fetchall()}

def get_web_commands():
    cursor.execute("SELECT name, url FROM web_command")
    return {row[0].lower(): row[1] for row in cursor.fetchall()}

def find_contact(query):
    query = query.strip().lower()
    cursor.execute("SELECT mobile_no FROM contacts WHERE LOWER(name) LIKE ? OR LOWER(name) LIKE ?", ('%' + query + '%', query + '%'))
    results = cursor.fetchall()
    if results:
        mobile_number_str = str(results[0][0])
        if not mobile_number_str.startswith('+91'):
            mobile_number_str = '+91' + mobile_number_str
        return mobile_number_str, query
    else:
        return 0, 0
