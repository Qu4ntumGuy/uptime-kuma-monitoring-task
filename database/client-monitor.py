import mysql.connector

# Replace these with your actual database connection details
db_config = {
    'host': '3.149.245.49',
    'user': 'admin',
    'password': 'root@123',
    'database': 'kuma',
}

# Create a connection to the MySQL server
connection = mysql.connector.connect(**db_config)

try:
    # Create a cursor to interact with the database
    cursor = connection.cursor()

    # Execute a query to select all data from the credentials table
    query = "SELECT * FROM websites"
    cursor.execute(query)

    # Fetch all rows
    rows = cursor.fetchall()

    # Print the data
    for row in rows:
        client_ip = [row[1]]
        name = [row[2]]
        url = [row[3]]
        # print(f"ID: {row[0]}, Host IP: {row[1]}, Username: {row[2]}, Password: {row[3]}, Client IP: {row[4]}")

    print(f"Client IP: {client_ip}, Name: {name}, URL: {url}")

finally:
    # Close the cursor and connection
    cursor.close()
    connection.close()
