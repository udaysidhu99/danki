import mysql.connector
import pandas as pd

# Database connection
conn = mysql.connector.connect(
    host="localhost",
    user="d043b228",
    password="dXWtG3ABtQhtvXti2oCt",
    database="d043b228"
)

# Query the registrants table
query = "SELECT * FROM aw6ne_eb_registrants"
df = pd.read_sql(query, conn)

# Close connection
conn.close()

# Show and/or export data
print(df.head())
df.to_csv("registrants.csv", index=False)