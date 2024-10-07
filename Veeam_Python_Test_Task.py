import argparse
import logging
import os
import shutil
import time

#
def setup_logging(log_file):
    logging.basicConfig(
        level=logging.INFO, #Any log messages with level above INFO will be reported
        format='%(asctime)s - %(levelname)s - %(message)s', #timestamp, level and the message shown for the log
        handlers=[
            logging.FileHandler(log_file), #log messages will be written to a file
            logging.StreamHandler() #log messages will be printed in the console
        ]
    )

def sync_folders(source_folder, replica_folder, log_file):
    logger = logging.getLogger(__name__)

    try:
        #If there isnt any replica folder it is created
        if not os.path.exists(replica_folder):
            os.makedirs(replica_folder)
            logger.info(f"Created replica folder: {replica_folder}")

        #Copy files from source to replica
        logger.info(f"Starting to copy files from source to replica.")
        
        for root, dirs, files in os.walk(source_folder): #goes through every directory in the source folder
            #Calculates the relative path of the current directory (root) from the source_folder.
            relative_path = os.path.relpath(root, source_folder)
            
            #Creates the corresponding directory path in the replica folder using the relative path.
            target_dir = os.path.join(replica_folder, relative_path)

            os.makedirs(target_dir, exist_ok=True)  #Ensures that target directory exists and if not creates it

            for file in files:
                source_file = os.path.join(root, file)
                target_file = os.path.join(target_dir, file)

                logger.info(f"Copying file: {source_file} -> {target_file}")
                shutil.copy2(source_file, target_file)

        #If there are files that dont exist in the source folder they will be removed from the replica folder
        logger.info(f"Checking for files to remove in replica.")
        for root, dirs, files in os.walk(replica_folder):
            relative_path = os.path.relpath(root, replica_folder)
            target_dir = os.path.join(source_folder, relative_path)

            for file in files:
                source_file = os.path.join(target_dir, file)
                target_file = os.path.join(root, file)

                if not os.path.exists(source_file):
                    logger.info(f"Removing file: {target_file} (does not exist in source)")
                    os.remove(target_file)

    except Exception as e:
        logger.error(f"Error during synchronization: {str(e)}")
        raise

def schedule_sync(source_folder, replica_folder, interval, log_file):
    while True:
        try:
            sync_folders(source_folder, replica_folder, log_file)
            logging.info("Synchronization completed successfully.")
        except Exception as e:
            logging.error(f"Error during synchronization: {str(e)}")

        time.sleep(interval * 60)  #Wait for the specified interval

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Folder Synchronization")
    parser.add_argument("--source", required=True, help="Path to source folder")
    parser.add_argument("--replica", required=True, help="Path to replica folder")
    parser.add_argument("--interval", type=int, default=30, help="Synchronization Interval in minutes")
    parser.add_argument("--log-file", default="sync_log.txt", help="Log File Path")
    
    args = parser.parse_args()

    setup_logging(args.log_file)
    logging.info(f"Synchronization has started. Source: {args.source}, Replica: {args.replica}")
    schedule_sync(args.source, args.replica, args.interval, args.log_file)
