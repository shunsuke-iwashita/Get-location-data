"""
Update and delete IDs in a MOT format file based on changes in other MOT format files.

This script reads an original MOT format file and a folder containing changed MOT format files.
It then updates and deletes IDs in the original file based on the changes in the changed files.
The updated MOT format file is saved to a different folder.

The script takes the following command-line arguments:
    --folder_path (str): The path to the folder containing the original MOT format file.
    --changed_folder_path (str): The path to the folder containing the changed MOT format files.
    --file_name (str): The name of the original MOT format file (without extension).
    --output_folder_path (str): The path to save the output MOT format file.

Usage:
python integrate_id.py --folder_path <folder_path> --changed_folder_path <changed_folder_path> --file_name <file_name> --output_folder_path <output_folder_path>
"""

import os
import argparse
from collections import Counter, defaultdict


def arg_parse():
    """
    Parse command line arguments.
    """
    parser = argparse.ArgumentParser(
        description='Update and delete IDs in a MOT format file and save the result to a different file.')
    parser.add_argument('--folder_path', type=str, default='/home/s_iwashita/workspace6/detection/code_labelbox/result/original_mot',
                        help='The path to the folder containing the original MOT format file.')
    parser.add_argument('--changed_folder_path', type=str, default='/home/s_iwashita/workspace6/detection/code_labelbox/result/changed_mot',
                        help='The path to the folder containing the changed MOT format files.')
    parser.add_argument('--file_name', type=str, default='original_file',
                        help='The name of the original MOT format file (without extension).')
    parser.add_argument('--output_folder_path', type=str, default='/home/s_iwashita/workspace6/detection/code_labelbox/result/integrated_mot',
                        help='The path to save the output MOT format file.')
    return parser.parse_args()


def update_id(original_data, changed_data):
    """
    Update and delete IDs in the original MOT format file based on changes in the changed MOT format files.

    Args:
        original_data (list): List of lines from the original MOT format file.
        changed_data (list): List of lines from the changed MOT format files.

    Returns:
        list: List of updated lines for the original MOT format file.
    """
    # Convert changed_data to a dictionary for faster lookup
    changed_dict = defaultdict(list)
    for changed_line in changed_data:
        changed_frame, changed_id, changed_bb_left, changed_bb_top, changed_bb_width, changed_bb_height, changed_conf, changed_x, changed_y, changed_z, changed_class = changed_line.replace(' ', '').split(
            ',')
        key = (changed_frame, changed_bb_left, changed_bb_top,
               changed_bb_width, changed_bb_height)
        changed_dict[key].append(changed_id)

    updated_data = []
    for line in original_data:
        frame, id, bb_left, bb_top, bb_width, bb_height, conf, x, y, z, class_ = line.replace(' ', '').split(
            ',')
        key = (frame, bb_left, bb_top, bb_width, bb_height)
        matching_objects = changed_dict.get(key, [])
        if matching_objects:
            mode, new_id = count_id(matching_objects)
            if mode == 'change':
                updated_data.append(
                    f'{frame}, {new_id}, {bb_left}, {bb_top}, {bb_width}, {bb_height}, {conf}, {x}, {y}, {z}, {class_}')
            elif mode == 'delete':
                pass
            else:
                updated_data.append(line)
        else:
            updated_data.append(line)
    return updated_data


def count_id(ids_list):
    """
    Count the occurrence of each ID in a list and determine the mode of operation based on the counts.

    Args:
        ids_list (list): A list of IDs to be counted.

    Returns:
        tuple: A tuple containing the mode of operation ('not-change', 'change', 'delete') and the ID to process.
    """
    counts = Counter(ids_list)
    counts_list = counts.most_common()
    if len(counts) == 1:
        mode = 'not-change'
        target_id = counts_list[0][0]
    elif len(counts) >= 2:
        if len(counts) == 2:
            mode = 'change'
            target_id = counts_list[1][0]
            if int(counts_list[0][0]) <= 14:
                mode = 'delete'
        else:
            mode = 'delete'
            target_id = counts_list[0][0]
    return mode, target_id


def main():
    args = arg_parse()

    file_name = args.file_name
    file_path = os.path.join(args.folder_path, file_name + '.txt')
    changed_folder_path = args.changed_folder_path
    output_file_path = os.path.join(
        args.output_folder_path, file_name + '.txt')

    # Create the output folder if it does not exist
    os.makedirs(args.output_folder_path, exist_ok=True)

    # Load the original MOT format file
    with open(file_path, 'r') as f:
        original_data = f.readlines()

    # Load the changed MOT format files if the name includes the original file name
    changed_files = [f for f in os.listdir(
        changed_folder_path) if file_name in f]
    changed_data = []
    for changed_file in changed_files:
        with open(os.path.join(changed_folder_path, changed_file), 'r') as f:
            changed_data.extend(f.readlines())

    # Process the original MOT format file
    updated_data = update_id(original_data, changed_data)

    # Save the updated MOT format file
    with open(output_file_path, 'w') as f:
        f.writelines(updated_data)


if __name__ == '__main__':
    main()
