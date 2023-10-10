from database.db import connect_to_db
import pyodbc


def fetch_top_users(servername, limit=3):
    # Validate and sanitize inputs
    if not isinstance(servername, str) or not servername.strip():
        raise ValueError("Invalid server name provided")

    if not isinstance(limit, int) or limit <= 0:
        raise ValueError("Invalid limit provided")

    cnxn, cursor = None, None
    try:
        cnxn, cursor = connect_to_db()

        query = """
        SELECT TOP (?) username, COUNT(message) as message_count
        FROM dbo.discord_logs 
        WHERE servername=?
        GROUP BY username
        ORDER BY message_count DESC
        """

        cursor.execute(query, (limit, servername))
        rows = cursor.fetchall()

        # Convert rows to list of dictionaries for easier processing
        top_users = [{"username": row[0], "message_count": row[1]} for row in rows]
        return top_users

    except pyodbc.Error as e:
        print(f"Database error occurred: {e}")
        raise RuntimeError("Failed to fetch top users from the database.") from e

    finally:
        if cursor:
            cursor.close()
        if cnxn:
            cnxn.close()
