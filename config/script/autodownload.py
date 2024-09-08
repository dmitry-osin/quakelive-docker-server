import os
import subprocess
import argparse


def download_workshop_items(steamcmd_path, workshop_file):
    # Check if the file exists
    if not os.path.exists(workshop_file):
        print(f"File {workshop_file} not found.")
        return

    # Read the workshop.txt file
    with open(workshop_file, 'r') as file:
        item_ids = [line.strip() for line in file if line.strip() and not line.strip().startswith('#')]

    # Command to login to steamcmd
    login_command = f'{steamcmd_path} +login anonymous'

    # Loop through all items and download each
    for item_id in item_ids:
        download_command = f'{steamcmd_path} +login anonymous +workshop_download_item 282440 {item_id} +quit'

        # Execute the command
        try:
            subprocess.run(download_command, check=True, shell=True)
            print(f"Item {item_id} downloaded successfully.")
        except subprocess.CalledProcessError as e:
            print(f"Error downloading item {item_id}: {e}")


if __name__ == "__main__":
    # Command-line argument parser
    parser = argparse.ArgumentParser(
        description='Script to download Workshop items from a workshop.txt file using steamcmd.')
    parser.add_argument('--steamcmd', type=str, required=True, help='Path to steamcmd')
    parser.add_argument('--workshop_file', type=str, required=True, help='Path to the workshop.txt file')

    args = parser.parse_args()

    download_workshop_items(args.steamcmd, args.workshop_file)
