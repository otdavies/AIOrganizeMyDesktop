import os
import argparse
from organizer import FileOrganizer

if __name__ == '__main__':
    try:
        # Get the directory of this script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        # Change the working directory to the script directory
        os.chdir(script_dir)

        print("Parsing arguments")
        # Parse the command line arguments
        parser = argparse.ArgumentParser(
            description="Organize files in the given directory")
        parser.add_argument("path", help="The directory to organize")
        args = parser.parse_args()
        target_path = args.path.replace('\\', '/').strip() + '/'
        print(f"Target path: {target_path}")

        # Organize the files
        print("Starting organizer")
        organizer = FileOrganizer(target_path)
        organizer.organize_files()
        print("Done")

    except Exception as e:
        print(f"An error occurred: {e}")
        input("Press Enter to exit...")
