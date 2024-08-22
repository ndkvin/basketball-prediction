from database import db

# SQL query to create the table
create_table_query = '''
    CREATE TABLE activity (
        id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(255),
        path VARCHAR(255),
        result VARCHAR(255),
        confidence FLOAT,
        created_at DATETIME
    );
'''

# Execute the query to create the table
db.execute_query(create_table_query, commit=True)

# Optionally, close the database connection if done
db.close()

