from database import connection

connection.execute(
    '''
    CREATE TABLE activity (
        id INT PRIMARY KEY AUTO_INCREMENT,
        username VARCHAR(255),
        path VARCHAR(255),
        result VARCHAR(255),
        confidence FLOAT,
        created_at DATETIME
    );
    '''
)
