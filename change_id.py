"""
This script updates the ID of objects in a MOT format file and saves the updated data to a new file.

The script takes the following command-line arguments:
    --folder_path (str): The path to the folder containing the MOT format file.
    file_name (str): The name of the MOT format file (without extension).
    --output_folder_path (str): The path to save the output MOT format file.
    old_ids (str): The old ID values to be updated, separated by commas.
    new_id (float): The new ID value.

The script performs the following steps:
1. Reads the input MOT format file.
2. Searches for objects with IDs matching the provided old IDs.
3. Updates the ID of matching objects with the new ID value.
4. Saves the updated MOT format data to a new file in the specified output folder.

Usage:
python change_id.py --folder_path <folder_path> --output_folder_path <output_folder_path> <file_name> <old_ids> <new_id>

Example usage:
python change_id.py --folder_path /path/to/folder --file_name input_file --output_folder_path /path/to/output --old_ids 1,2,3 --new_id 4
"""

import json
import os
import re
import argparse


def update_id(file_path, output_file_path, old_ids, new_id):
    """
    Update the ID of objects in a MOT format file and save the updated data to a new file.

    Args:
        file_path (str): The path to the input MOT format file.
        output_file_path (str): The path where the updated MOT format file will be saved.
        old_ids (str): A comma-separated string of old IDs to be updated.
        new_id (float): The new ID value to replace the old IDs with.
    """
    old_ids_list = [int(id_str) for id_str in old_ids.split(',')]
    updated_lines = []

    with open(file_path, 'r') as file:
        lines = file.readlines()

    updated = False
    for line in lines:
        parts = line.strip().split(',')
        if int(parts[1]) in old_ids_list:
            parts[1] = str(int(new_id))
            updated_lines.append(','.join(parts))
            updated = True
        else:
            updated_lines.append(line.strip())

    if updated:
        with open(output_file_path, 'w') as file:
            for line in updated_lines:
                file.write(f"{line}\n")
        print(
            f"ID from {old_ids} was updated to {new_id} and saved to {output_file_path}.")
    else:
        print(f"No matching ID from {old_ids} found.")


def main():
    """
    Main function to parse arguments and initiate the ID update process.
    """
    parser = argparse.ArgumentParser(
        description='Update ID in the MOT format file.')
    parser.add_argument('--folder_path', type=str, default='/home/s_iwashita/workspace6/detection/code_labelbox/result/yolo_mot',
                        help='The path to the folder containing the MOT format file.')
    parser.add_argument('file_name', type=str,
                        help='The name of the MOT format file (without extension).')
    parser.add_argument('--output_folder_path', type=str,
                        default='/home/s_iwashita/workspace6/detection/code_labelbox/result/changed_mot', help='The path to save the output MOT format file.')
    parser.add_argument(
        'old_ids', type=str, help='The old id values to be updated, separated by commas.')
    parser.add_argument('new_id', type=int, help='The new id value.')

    args = parser.parse_args()

    file_path = os.path.join(args.folder_path, args.file_name + '.txt')
    # Get output file name
    file_name = args.file_name
    pattern = re.compile(rf"^{re.escape(file_name)}_val(\d+).txt$")

    # Create output folder if it doesn't exist
    os.makedirs(os.path.dirname(args.output_folder_path), exist_ok=True)
    existing_files = os.listdir(args.output_folder_path)
    val_numbers = []
    for existing_file in existing_files:
        match = pattern.match(existing_file)
        if match:
            val_numbers.append(int(match.group(1)))
    if val_numbers:
        new_val_number = max(val_numbers) + 1
        new_file_name = f"{file_name}_val{new_val_number:02}.txt"
    else:
        new_file_name = f"{file_name}_val00.txt"

    output_file_path = os.path.join(args.output_folder_path, new_file_name)

    update_id(file_path, output_file_path, args.old_ids, args.new_id)


if __name__ == '__main__':
    main()
