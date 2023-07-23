import json
import shutil
import os
import time
#  Import prompt
from prompt import Prompt
from descriptor import ImageDescriber

classifier = ImageDescriber()

# The path to the directory you want to organize
path = 'C:/Users/Psyfer/Desktop/'

schema = """{
    "file_remap": {
        "ExampleName.png": "Images/BetterExampleName.png",
        "file2.txt": "Notes/file2.txt",
        ...,
        "Some_Bad_Format.ext": "Folder/SomeGoodFormat.ext"
        }
    }"""

# Get a list of all files, but not folders
files = [f for f in os.listdir(path) if os.path.isfile(os.path.join(path, f))]
folders = [f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))]
created_folders = set()


def generate_prompt(file_metadata, folder_metadata):
    prompt = "Organize the following files. Infer project name from file type, file name and description. You can put files in existing folders if they make sense. You can create folders.\n"
    if len(created_folders) > 0:
        prompt += "Existing folders you can optionally use: "
        prompt += ", ".join(created_folders)
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
        if os.path.isdir(os.path.join(path, folder)):
            prompt += f"{folder}\n"

    return prompt


def get_file_meta_batch(files, range=[0, 20]):
    file_metadata = []
    if range[1] > len(files):
        range[1] = len(files)

    for file in files[range[0]:range[1]]:
        metadata = {}
        # Get the file extension
        metadata['file_ext'] = os.path.splitext(file)[1]
        metadata['file_name'] = os.path.splitext(file)[0]
        # Get the creation time
        creation_time = os.path.getctime(os.path.join(path, file))
        # Convert the creation time to a human readable format of just the month name, day and year
        metadata['creation_date'] = time.strftime(
            "%B %d, %Y", time.localtime(creation_time))

        # If this file is an image, classify it
        if metadata['file_ext'] == '.png' or metadata['file_ext'] == '.jpg':
            # Get the image path
            image_path = os.path.join(path, file)
            # Classify the image
            classification = classifier.classify_image(
                image_path, "Description:")
            # Get the description
            metadata['description'] = classification

        file_metadata.append(metadata)
    return file_metadata


def get_folder_meta_batch(folders, range=[0, 20]):
    folder_metadata = []

    if range[1] > len(folders):
        range[1] = len(folders)

    for folder in folders[range[0]:range[1]]:
        metadata = {}
        # Get the file extension
        metadata['folder_name'] = folder
        # Date created
        creation_time = os.path.getctime(os.path.join(path, folder))
        # Convert the creation time to a human readable format
        metadata['creation_date'] = time.strftime(
            "%B %d, %Y", time.localtime(creation_time))

        # Is it empty?
        metadata['is_empty'] = len(os.listdir(os.path.join(path, folder))) == 0

        folder_metadata.append(metadata)
    return folder_metadata


def move_and_rename_files(mapping, base_path):
    # Validate that the JSON is valid
    try:
        json.loads(mapping)
    except Exception as e:
        print(f'Error parsing JSON: {e}')
        return
    # Load JSON mapping
    file_remap = json.loads(mapping)['file_remap']

    for old_name, new_name in file_remap.items():
        old_file_path = os.path.join(base_path, old_name)
        new_file_path = os.path.join(base_path, new_name)
        try:
            # Check if old file exists
            if os.path.isfile(old_file_path):
                # Determine if we need to create folders, if so print them out
                if os.path.dirname(new_file_path) != '':
                    new_folder_name = os.path.dirname(new_file_path)
                    # remove the base path
                    new_folder_name = new_folder_name.replace(base_path, '')
                    created_folders.add(new_folder_name)

                # Create new directories if they don't exist
                os.makedirs(os.path.dirname(new_file_path), exist_ok=True)

                # Rename and move the file
                shutil.move(old_file_path, new_file_path)
            else:
                print(f'File {old_file_path} does not exist')
        except Exception as e:
            # couldn't move the file
            print(f'Error moving file {old_file_path} to {new_file_path}: {e}')


batch_size = 20
for i in range(0, len(files), batch_size):
    print("Batch " + str(i) + " to " + str(i+batch_size) + ":")
    batch = get_file_meta_batch(files, range=[i, i+batch_size])
    p = generate_prompt(batch, {})

    print(p)
    print("\n\n")
    while True:
        try:
            response = Prompt(
                p, "You are a file organizer, attempt to clean up the files into folders and rename them to be clearer. Only rename files with pointless names that are unrelated to their content. Group things by similarity and description when possible")
            result = response.call(schema=schema, tokens=2048)
            break  # if successful, break the loop
        except Exception as e:
            print(f'Failed to reach GPT: {e}')
            # wait
            time.sleep(2)

    # Continue with the rest of your code here
    print("Result:")
    print(result)

    # Call the function with JSON mapping and paths
    move_and_rename_files(mapping=json.dumps(result), base_path=path)
    print("Created Folders:")
    print(created_folders)
    # Wait a moment to let the GPT api cool down
    time.sleep(0.5)
