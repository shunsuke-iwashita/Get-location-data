'''
This spript updates a MOT format file based on an NDJSON file exported from Labelbox.

The script reads the NDJSON file and extracts bounding box data for each object in each frame.
It then updates the MOT format file by adding new objects and removing objects that are not present in the NDJSON file.
The updated MOT format file is saved to a different folder.

The script takes the following command-line arguments:
    ndjson_file (str): The path to the NDJSON file exported from Labelbox.
    txt_file (str): The path to the MOT format file to be updated.

Usage:
python labelbox_ndjson_to_mot.py <ndjson_file> <txt_file>
'''
import argparse
import json


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Update TXT file based on NDJSON file.')
    parser.add_argument('ndjson_file', type=str,
                        help='Path to the NDJSON file.')
    parser.add_argument('txt_file', type=str, help='Path to the TXT file.')
    return parser.parse_args()


def load_ndjson_data(ndjson_path):
    with open(ndjson_path, 'r') as file:
        data = [json.loads(line) for line in file]
    return data


def update_txt_file(ndjson_data, txt_path):
    # Extract necessary data from ndjson
    ndjson_info = {}
    for data in ndjson_data:
        # annotations内のframesを取得
        frames = list(data.get('projects', {}).values())[
            0].get('labels', {})[0].get('annotations', {}).get('frames', {})

        # 各frameに対してループ
        for frame_number, frame_data in frames.items():
            # 各frame内のobjectsを取得
            objects = frame_data.get('objects', {})

            # 各objectに対してループ
            for object_id, object_data in objects.items():
                # bounding_box情報を取得
                bbox = object_data.get('bounding_box', {})
                id = object_data.get('name', None)

                ndjson_info[(int(frame_number)-1, int(id))] = (
                    bbox["left"], bbox["top"], bbox["width"], bbox["height"])

        # Read and update txt data
        updated_txt_data = []
        with open(txt_path, 'r') as file:
            for line in file:
                parts = line.strip().split(', ')
                frame_id, obj_id = int(parts[0]), int(parts[1])
                # ndjson_infoにframe_idとobj_idがともに一致するデータが存在する場合、updated_txt_dataに追加しない
                if (frame_id, obj_id) in ndjson_info:
                    continue
                updated_txt_data.append(parts)

        # Add new data from ndjson
        for (frame_id, obj_id), (left, top, width, height) in ndjson_info.items():
            updated_txt_data.append(
                [frame_id, obj_id, left, top, width, height, 1, -1, -1, -1, "player"])

        # Sort data
        updated_txt_data.sort(
            key=lambda x: (-int(x[0]), -int(x[1])), reverse=True)

        # Write updated data to a new txt file
        with open(txt_path.replace('integrated', 'complete'), 'w') as file:
            for item in updated_txt_data:
                file.write(', '.join(map(str, item)) + '\n')


def main():
    args = parse_arguments()
    ndjson_data = load_ndjson_data(args.ndjson_file)
    update_txt_file(ndjson_data, args.txt_file)


if __name__ == "__main__":
    main()
