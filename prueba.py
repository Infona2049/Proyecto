from django.db import connection
cursor = connection.cursor()
cursor.execute("SELECT 1;")
print(cursor.fetchone())
