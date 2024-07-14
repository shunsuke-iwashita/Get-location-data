"""
This script draws bounding boxes from MOT (Multiple Object Tracking) format data on a video and saves the output.
It demonstrates how to parse MOT format data, generate unique colors for each object ID, and overlay bounding boxes on video frames.

Usage:
python draw_bboxes_on_video.py <path_to_mot_file> <path_to_input_video> <path_to_output_video>

Arguments:
- path_to_mot_file: The path to the MOT format file containing bounding box data.
- path_to_input_video: The path to the input video file on which bounding boxes will be drawn.
- path_to_output_video: The path to save the output video with bounding boxes drawn on it.

Example Command:
python draw_bboxes_on_video.py data/mot_data.txt input_video.mp4 output_video.mp4
"""
import cv2
import random
import argparse


def generate_unique_color(id):
    """
    Generates a unique color for a given ID using a deterministic random process.

    Args:
        id (int): The object ID for which to generate a color.

    Returns:
        tuple: A tuple representing the color in BGR format.
    """
    random.seed(id)
    return (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))


def load_mot_data(mot_file):
    """
    Loads MOT format data from a file.

    Args:
        mot_file (str): The path to the MOT format file.

    Returns:
        dict: A dictionary where each key is a frame ID and the value is a list of tuples containing object ID and bounding box coordinates.
    """
    data = {}
    with open(mot_file, 'r') as f:
        for line in f:
            parts = line.strip().split(',')
            frame_id, obj_id, bb_left, bb_top, bb_width, bb_height = map(
                float, parts[:6])
            if frame_id not in data:
                data[frame_id] = []
            data[frame_id].append(
                (int(obj_id), (int(bb_left), int(bb_top), int(bb_width), int(bb_height))))
    return data


def draw_bboxes_on_video(video_path, mot_data, output_path):
    """
    Draws bounding boxes on each frame of a video based on MOT format data and saves the output video.

    Args:
        video_path (str): The path to the input video file.
        mot_data (dict): The MOT format data loaded using load_mot_data function.
        output_path (str): The path to save the output video.

    Returns:
        None
    """
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print("Error: Video file could not be opened.")
        return

    frame_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    frame_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    frame_rate = cap.get(cv2.CAP_PROP_FPS)

    fourcc = cv2.VideoWriter_fourcc(*'mp4v')
    out = cv2.VideoWriter(output_path, fourcc, frame_rate,
                          (frame_width, frame_height))

    frame_id = 0
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if frame_id in mot_data:
            for obj_id, bbox in mot_data[frame_id]:
                color = generate_unique_color(obj_id)
                cv2.rectangle(
                    frame, (bbox[0], bbox[1]), (bbox[0]+bbox[2], bbox[1]+bbox[3]), color, 2)
                cv2.putText(frame, str(
                    obj_id), (bbox[0], bbox[1]-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

        out.write(frame)
        frame_id += 1

    cap.release()
    out.release()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Draw bounding boxes from MOT format on video.')
    parser.add_argument('--mot_file', type=str,
                        help='Path to the MOT format file.')
    parser.add_argument('--video_path', type=str,
                        help='Path to the input video file.')
    parser.add_argument('output_path', type=str,
                        help='Path to the output video file.')

    args = parser.parse_args()

    mot_data = load_mot_data(args.mot_file)
    draw_bboxes_on_video(args.video_path, mot_data, args.output_path)
