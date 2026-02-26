"""
Docker entrypoint:
  1. Waits for PostgreSQL to accept connections
  2. Runs migrations
  3. Starts Django dev server
"""
import os
import sys
import time
import subprocess


def wait_for_db():
    import psycopg2

    config = dict(
        host=os.environ.get('DB_HOST', 'db'),
        dbname=os.environ.get('DB_NAME', 'studybridge'),
        user=os.environ.get('DB_USER', 'studybridge_user'),
        password=os.environ.get('DB_PASSWORD', '7001070036'),
        port=os.environ.get('DB_PORT', '5432'),
    )

    print('Waiting for PostgreSQL...', flush=True)
    for attempt in range(60):
        try:
            conn = psycopg2.connect(**config)
            conn.close()
            print('PostgreSQL is ready!', flush=True)
            return
        except psycopg2.OperationalError:
            print(f'  Not ready yet (attempt {attempt + 1}/60), retrying...', flush=True)
            time.sleep(1)

    print('ERROR: Could not connect to PostgreSQL after 60 seconds. Exiting.', flush=True)
    sys.exit(1)


def main():
    wait_for_db()

    print('Running migrations...', flush=True)
    subprocess.run([sys.executable, 'manage.py', 'migrate', '--noinput'], check=True)

    print('Starting Django server on 0.0.0.0:8000 ...', flush=True)
    # os.execv replaces the current process — cleaner than subprocess for the final command
    os.execv(sys.executable, [sys.executable, 'manage.py', 'runserver', '0.0.0.0:8000'])


if __name__ == '__main__':
    main()
