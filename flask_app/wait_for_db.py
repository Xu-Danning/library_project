import os
import time
import pymysql

host = os.getenv('DB_HOST', 'db')
port = int(os.getenv('DB_PORT', 3306))
user = os.getenv('DB_USER', 'root')
password = os.getenv('DB_PASS', '')
db = os.getenv('DB_NAME', 'library_db')

def wait_for_db(timeout=60, interval=2):
    start = time.time()
    while True:
        try:
            conn = pymysql.connect(host=host, user=user, password=password, db=db, port=port, charset='utf8mb4')
            conn.close()
            print('DB is ready')
            return
        except Exception as e:
            if time.time() - start > timeout:
                print('Timed out waiting for DB')
                raise
            print('Waiting for DB...', str(e))
            time.sleep(interval)

if __name__ == '__main__':
    wait_for_db()