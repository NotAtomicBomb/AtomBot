import config
import pymysql.cursors


async def connect():
    try:
        connection = pymysql.connect(
            user=config.DB_USERNAME,
            password=config.DB_PASSWORD,
            host=config.DB_IP,
            port=3306,
            database=config.DB_NAME
        )
        connection.autocommit(True)
        cursor = connection.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS private_channels (user_id CHAR(50) PRIMARY KEY,channel_id CHAR(50))")

        return cursor
    except pymysql.Error as error:
        print(f"Error connecting to database: {error}")
        if "Unknown database" in str(error):
            connection = pymysql.connect(
                user=config.DB_USERNAME,
                password=config.DB_PASSWORD,
                host=config.DB_IP,
                port=3306
            )
            connection.autocommit(True)
            cursor = connection.cursor()
            cursor.execute("CREATE DATABASE config.DB_NAME")
            cursor.execute(f"USE {config.DB_NAME}")
            cursor.execute("CREATE TABLE private_channels (user_id CHAR(50) PRIMARY KEY,channel_id CHAR(50))")
            print("Database created.")
            return cursor


async def get_all_records():
    cursor = await connect()

    try:
        cursor.execute("SELECT user_id,channel_id FROM private_channels")
        result = cursor.fetchall()
        return result
    finally:
        cursor.close()


async def remove_channel_record(channel_id):
    cursor = await connect()
    cursor.execute(f"DELETE FROM private_channels WHERE channel_id={channel_id}")
    cursor.close()


async def add_user_channel(user_id, channel_id):
    cursor = await connect()
    try:
        cursor.execute(f"INSERT INTO private_channels (user_id,channel_id) VALUES ({str(user_id)}, {str(channel_id)})")
    except pymysql.Error as error:
        print(error)
    cursor.close()
