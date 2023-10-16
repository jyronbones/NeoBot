from database.db import async_db_executor, connect_to_db


async def get_total_messages(servername):
    return await async_db_executor(_get_total_messages, servername)


def _get_total_messages(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute("SELECT COUNT(*) FROM dbo.discord_logs WHERE servername = ?", (servername,))
    total = cursor.fetchone()[0]
    cursor.close()
    cnxn.close()
    return total


async def get_total_links_shared(servername):
    return await async_db_executor(_get_total_links_shared, servername)


def _get_total_links_shared(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute("SELECT COUNT(*) FROM dbo.discord_logs WHERE servername = ? AND links IS NOT NULL AND links <> ''",
                   (servername,))
    total = cursor.fetchone()[0]
    cursor.close()
    cnxn.close()
    return total


async def get_messages_over_time(servername, interval="daily"):
    return await async_db_executor(_get_messages_over_time, servername, interval)


def _get_messages_over_time(servername, interval):
    cnxn, cursor = connect_to_db()
    if interval == "daily":
        cursor.execute("SELECT FORMAT(timestamp, 'yyyy-MM-dd') as date, COUNT(*) as count FROM dbo.discord_logs WHERE "
                       "servername = ? GROUP BY FORMAT(timestamp, 'yyyy-MM-dd') ORDER BY date DESC", (servername,))
    elif interval == "weekly":
        # Note: We need to group by both DATEPART(week, timestamp) and the formatted date to ensure aggregation
        # happens correctly.
        cursor.execute("SELECT FORMAT(timestamp, 'yyyy-MM-dd', 'en-US') as date, COUNT(*) as count FROM "
                       "dbo.discord_logs WHERE servername = ? GROUP BY DATEPART(week, timestamp), FORMAT(timestamp, "
                       "'yyyy-MM-dd', 'en-US') ORDER BY date DESC",
                       (servername,))
    elif interval == "monthly":
        cursor.execute("SELECT FORMAT(timestamp, 'yyyy-MM') as date, COUNT(*) as count FROM dbo.discord_logs WHERE "
                       "servername = ? GROUP BY FORMAT(timestamp, 'yyyy-MM') ORDER BY date DESC", (servername,))
    elif interval == "yearly":
        cursor.execute("SELECT FORMAT(timestamp, 'yyyy') as date, COUNT(*) as count FROM dbo.discord_logs WHERE "
                       "servername = ? GROUP BY FORMAT(timestamp, 'yyyy') ORDER BY date DESC", (servername,))
    results = cursor.fetchall()
    cursor.close()
    cnxn.close()
    return results


async def get_busiest_hour(servername):
    return await async_db_executor(_get_busiest_hour, servername)


def _get_busiest_hour(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT TOP 1 DATEPART(HOUR, timestamp) as hour, COUNT(*) as count 
        FROM dbo.discord_logs 
        WHERE servername = ? 
        GROUP BY DATEPART(HOUR, timestamp) 
        ORDER BY count DESC 
        """,
        (servername,)
    )
    result = cursor.fetchone()
    cursor.close()
    cnxn.close()

    if result:
        hour = result[0]
        if 0 <= hour <= 23:
            return hour
    return None


async def get_busiest_day(servername):
    return await async_db_executor(_get_busiest_day, servername)


def _get_busiest_day(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT DATEPART(WEEKDAY, timestamp) as day, COUNT(*) as count 
        FROM dbo.discord_logs 
        WHERE servername = ? 
        GROUP BY DATEPART(WEEKDAY, timestamp) 
        ORDER BY count DESC 
        """,
        (servername,)
    )
    results = cursor.fetchone()
    cursor.close()
    cnxn.close()
    return results


async def get_unique_users(servername):
    return await async_db_executor(_get_unique_users, servername)


def _get_unique_users(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT COUNT(DISTINCT username) 
        FROM dbo.discord_logs 
        WHERE servername = ?
        """,
        (servername,)
    )
    total = cursor.fetchone()[0]
    cursor.close()
    cnxn.close()
    return total


async def get_avg_messages_per_user(servername):
    total_messages = await get_total_messages(servername)
    unique_users = await get_unique_users(servername)
    return total_messages / unique_users if unique_users != 0 else 0


async def get_avg_messages_per_user_async(servername):
    total_messages = await get_total_messages(servername)
    unique_users = await get_unique_users(servername)
    return total_messages / unique_users if unique_users != 0 else 0


async def get_user_growth_over_time(servername):
    return await async_db_executor(_get_user_growth_over_time, servername)


def _get_user_growth_over_time(servername):
    cnxn, cursor = connect_to_db()
    cursor.execute(
        """
        SELECT FORMAT(timestamp, 'yyyy-MM-dd') as date, COUNT(DISTINCT username) as new_users
        FROM dbo.discord_logs 
        WHERE servername = ? 
        GROUP BY FORMAT(timestamp, 'yyyy-MM-dd') 
        ORDER BY date ASC
        """,
        (servername,)
    )
    results = cursor.fetchall()
    cursor.close()
    cnxn.close()
    return results
