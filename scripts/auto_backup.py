import subprocess
import datetime
import os

# Configuration
DB_NAME = "CinemaDB"
BACKUP_DIR = "../backups"
TIMESTAMP = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
FILENAME = f"{DB_NAME}_backup_{TIMESTAMP}.sql"
FILE_PATH = os.path.join(BACKUP_DIR, FILENAME)

def run_backup():
    # 1. Execute mysqldump
    dump_cmd = f"mysqldump -u root -p@0338048344 {DB_NAME} > {FILE_PATH}"
    subprocess.run(dump_cmd, shell=True)
    
    # 2. Git commands for version control push
    try:
        # subprocess.run(["git", "add", FILE_PATH], check=True)
        # subprocess.run(["git", "commit", "-m", f"Automated Backup {TIMESTAMP}"], check=True)
        # subprocess.run(["git", "push", "origin", "main"], check=True)
        print(f"Backup successful: {FILENAME}")
    except Exception as e:
        print(f"Error during Git push: {e}")

if __name__ == "__main__":
    run_backup()