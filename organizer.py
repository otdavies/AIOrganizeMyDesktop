import json
import shutil
import os
import time
from prompt import Prompt
from descriptor import ImageDescriber


class FileOrganizer:
    def __init__(self, target_path):
        self.user_prompt = "Organize the following files. Infer project name from file type, file name and description. You can put files in existing folders if they make sense. You can create folders.\n"
        self.system_prompt = "You are a file organizer, attempt to clean up the files into folders and optionally rename them to be clearer. Only rename files with non-descriptive names that are unrelated to their content. Group things by similarity and description when possible"
        self.schema = """{
            "file_remap": {
                "ExampleName.png": "Images/BetterExampleName.png",
                "file2.txt": "Notes/file2.txt",
                ...,
                "Some_Bad_Format.ext": "Folder/SomeGoodFormat.ext"
                }
            }"""

        self.target_path = target_path
        self.created_folders = set()

        print("Finding files and folders...")
        self.files = [f for f in os.listdir(self.target_path) if os.path.isfile(
            os.path.join(self.target_path, f))]
        self.folders = [f for f in os.listdir(self.target_path) if os.path.isdir(
            os.path.join(self.target_path, f))]
        # We want the localized path to the folders under the target path
        self.local_folders = [os.path.relpath(os.path.join(self.target_path, f), self.target_path)
                              for f in os.listdir(self.target_path)
                              if os.path.isdir(os.path.join(self.target_path, f))]
        print("Found " + str(len(self.files)) + " files and " +
              str(len(self.folders)) + " folders")
        print(self.local_folders)

        print("Initializing ImageDescriber... this can take a few minutes")
        self.image_descriptor = ImageDescriber()

    def generate_prompt(self, file_metadata, folder_metadata):
        prompt = self.user_prompt
        if len(self.created_folders) > 0:
            prompt += "Existing folders you can optionally use: "
            prompt += ", ".join(self.created_folders)
            prompt += "\n\n"

        prompt += "Files to organize:\n"
        # Include name, date and file extension
        for file in file_metadata:
            # If we have an image file, include the description
            if file['file_ext'] == '.png' or file['file_ext'] == '.jpg':
                prompt += f"{file['file_name']}{file['file_ext']}. Image Description: {file['description']}. Created on: {file['creation_date']}\n"
            else:
                prompt += f"{file['file_name']}{file['file_ext']}. Created on: {file['creation_date']}\n"

        if len(folder_metadata) > 0:
            prompt += "\n\nExisting Folders:\n"

        # Include existing folders
        for folder in folder_metadata:
            if os.path.isdir(os.path.join(self.target_path, folder)):
                prompt += f"{folder}\n"

        return prompt

    def get_file_meta_batch(self, files, range=[0, 20]):
        file_metadata = []
        if range[1] > len(files):
            range[1] = len(files)

        for file in files[range[0]:range[1]]:
            metadata = {}
            # Get the file extension
            metadata['file_ext'] = os.path.splitext(file)[1]
            metadata['file_name'] = os.path.splitext(file)[0]
            # Get the creation time
            creation_time = os.path.getctime(
                os.path.join(self.target_path, file))
            # Convert the creation time to a human readable format of just the month name, day and year
            metadata['creation_date'] = time.strftime(
                "%B %d, %Y", time.localtime(creation_time))

            # If this file is an image, classify it
            if metadata['file_ext'] == '.png' or metadata['file_ext'] == '.jpg':
                # Get the image path
                image_path = os.path.join(self.target_path, file)
                # Classify the image
                classification = self.image_descriptor.classify_image(
                    image_path, "Description:")
                # Get the description
                metadata['description'] = classification

            file_metadata.append(metadata)
        return file_metadata

    # Unused for now, but will likely be leveraged in the future
    def get_folder_meta_batch(self, folders, range=[0, 20]):
        folder_metadata = []
        if range[1] > len(folders):
            range[1] = len(folders)

        for folder in folders[range[0]:range[1]]:
            metadata = {}
            # Get the file extension
            metadata['folder_name'] = folder
            # Date created
            creation_time = os.path.getctime(
                os.path.join(self.target_path, folder))
            # Convert the creation time to a human readable format
            metadata['creation_date'] = time.strftime(
                "%B %d, %Y", time.localtime(creation_time))

            # Is the folder empty?
            metadata['is_empty'] = len(
                os.listdir(os.path.join(self.target_path, folder))) == 0

            folder_metadata.append(metadata)
        return folder_metadata

    def move_and_rename_files(self, mapping):
        # Validate the JSON
        try:
            json.loads(mapping)
        except Exception as e:
            print(f'Error parsing JSON: {e}')
            return
        # Load JSON mapping
        file_remap = json.loads(mapping)['file_remap']

        for old_name, new_name in file_remap.items():
            old_file_path = os.path.join(self.target_path, old_name)
            new_file_path = os.path.join(self.target_path, new_name)
            try:
                # Check if old file exists
                if os.path.isfile(old_file_path):
                    # Determine if we need to create folders
                    if os.path.dirname(new_file_path) != '':
                        new_folder_name = os.path.dirname(new_file_path)
                        new_folder_name = new_folder_name.replace(
                            self.target_path, '')
                        # We need to keep track of the folders we create so we can include them in the prompt (due to batching)
                        self.created_folders.add(new_folder_name)

                    # Create new directories if they don't exist
                    os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

                    print(f'Moving file {old_file_path} -> {new_file_path}')
                    # Rename and move the file
                    shutil.move(old_file_path, new_file_path)
                else:
                    print(f'File {old_file_path} does not exist')
            except Exception as e:
                # Couldn't move the file
                print(
                    f'Error moving file {old_file_path} to {new_file_path}: {e}')

    def organize_files(self, batch_size=20):
        print("Organizing files...")
        for i in range(0, len(self.files), batch_size):
            print("Batch " + str(i) + " to " + str(i+batch_size) + ":")
            batch = self.get_file_meta_batch(
                self.files, range=[i, i+batch_size])
            prompt = self.generate_prompt(batch, {})
            print("\n")

            while True:
                try:
                    response = Prompt(
                        prompt,
                        self.system_prompt
                    )
                    result = response.call(schema=self.schema, tokens=2048)
                    break
                except Exception as e:
                    print(f'Failed to reach GPT: {e}')
                    time.sleep(2)

            self.move_and_rename_files(mapping=json.dumps(result))
            time.sleep(0.5)
        print("Created Folders:")
        print(self.created_folders)
        print("Files organized!")
