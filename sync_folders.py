import os
import shutil
import time
import hashlib
import argparse
from datetime import datetime

# Log message to both the log file and the console
def log_message(log_file, message):
    with open(log_file, 'a') as f:
        f.write(f"{datetime.now()} - {message}\n")
    print(f"{datetime.now()} - {message}")

# Calculate the MD5 checksum of a file
def calculate_md5(file_path):
    hash_md5 = hashlib.md5()
    with open(file_path, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

# Synchronize replica folder to match the content of the source folder
def sync_folders(source, replica, log_file):
    # Step 1: Copy/update files from source to replica
    for root, dirs, files in os.walk(source):
        # Construct relative path from the source folder
        relative_path = os.path.relpath(root, source)
        replica_root = os.path.join(replica, relative_path)

        # Ensure all directories from source exist in replica
        if not os.path.exists(replica_root):
            os.makedirs(replica_root)
            log_message(log_file, f"Created directory: {replica_root}")

        for file in files:
            source_file = os.path.join(root, file)
            replica_file = os.path.join(replica_root, file)

            if not os.path.exists(replica_file):
                # File doesn't exist in replica, copy it
                shutil.copy2(source_file, replica_file)
                log_message(log_file, f"Copied new file: {replica_file}")
            else:
                # If the file exists, check if it needs updating
                if calculate_md5(source_file) != calculate_md5(replica_file):
                    shutil.copy2(source_file, replica_file)
                    log_message(log_file, f"Updated file: {replica_file}")

    # Step 2: Remove files from replica that are not in source
    for root, dirs, files in os.walk(replica):
        # Construct relative path from the replica folder
        relative_path = os.path.relpath(root, replica)
        source_root = os.path.join(source, relative_path)

        for file in files:
            replica_file = os.path.join(root, file)
            source_file = os.path.join(source_root, file)

            if not os.path.exists(source_file):
                # File is no longer in source, remove it from replica
                os.remove(replica_file)
                log_message(log_file, f"Removed file: {replica_file}")

        # Remove directories in replica that no longer exist in source
        for dir in dirs:
            replica_dir = os.path.join(root, dir)
            source_dir = os.path.join(source_root, dir)

            if not os.path.exists(source_dir):
                shutil.rmtree(replica_dir)
                log_message(log_file, f"Removed directory: {replica_dir}")

def main():
    parser = argparse.ArgumentParser(description="One-way folder synchronization.")
    parser.add_argument("source", help="Path to source folder")
    parser.add_argument("replica", help="Path to replica folder")
    parser.add_argument("interval", type=int, help="Synchronization interval in seconds")
    parser.add_argument("log_file", help="Path to the log file")
    
    args = parser.parse_args()

    source = args.source
    replica = args.replica
    interval = args.interval
    log_file = args.log_file

    # Start the synchronization loop
    while True:
        log_message(log_file, "Starting synchronization...")
        sync_folders(source, replica, log_file)
        log_message(log_file, f"Synchronization complete. Waiting for {interval} seconds...")
        time.sleep(interval)

if __name__ == "__main__":
    main()
