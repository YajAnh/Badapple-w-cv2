import cv2
import os
import shutil
import subprocess
import sys
import time

VIDEO_PATH = "baddapple.mp4"
ASCII_CHARS = " .'`^\",:;Il!i><~+_-?][}{1)(|\\/tfjrxnuvczXYUJCLQ0OZmwqpdbkhao*MW&8%#"


def getterminalsize():
    size = shutil.get_terminal_size((120, 40))
    return size.columns, size.lines


def frame_to_ascii(frame, target_width, max_height):
    height, width, _ = frame.shape
    aspect_ratio = height / width
    target_height = max(1, int(target_width * aspect_ratio * 0.55))

    if target_height > max_height:
        scale = max_height / target_height
        target_width = max(20, int(target_width * scale))
        target_height = max(1, int(target_width * aspect_ratio * 0.55))

    resized_frame = cv2.resize(frame, (target_width, target_height))
    gray_frame = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2GRAY)

    ascii_lines = []
    for row in gray_frame:
        line = "".join(ASCII_CHARS[min(len(ASCII_CHARS) - 1, int(pixel / 255 * (len(ASCII_CHARS) - 1)))] for pixel in row)
        ascii_lines.append(line)

    return ascii_lines


def center_ascii(lines, terminal_width, terminal_height):
    if not lines:
        return []

    content_width = max(len(line) for line in lines)
    left_padding = max((terminal_width - content_width) // 2, 0)
    top_padding = max((terminal_height - len(lines)) // 2, 0)

    padded_lines = [" " * left_padding + line for line in lines]
    return [""] * top_padding + padded_lines


def start_music(video_path):
    ffplay = shutil.which("ffplay")
    if not ffplay:
        return False

    try:
        subprocess.Popen(
            [ffplay, "-nodisp", "-autoexit", video_path],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        return True
    except OSError:
        return False


def main():
    cap = cv2.VideoCapture(VIDEO_PATH)
    if not cap.isOpened():
        print(f"Unable to open video: {VIDEO_PATH}")
        return

    cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

    fps = cap.get(cv2.CAP_PROP_FPS) or 30
    speed_input = input("Enter speed multiplier (default 1.0): ").strip() or "1.0"
    try:
        speed_multiplier = max(0.1, float(speed_input))
    except ValueError:
        speed_multiplier = 1.0

    music_choice = input("Play music? (y/n): ").strip().lower()
    music_enabled = music_choice in {"y", "yes", "1", "true", "on"}

    if music_enabled:
        if start_music(VIDEO_PATH):
            print("Music enabled.")
        else:
            print("Music requested, but ffplay was not found. Continuing without audio.")
    else:
        print("Music disabled.")

    os.system("cls" if os.name == "nt" else "clear")

    while cap.isOpened():
        start_time = time.time()
        ret, frame = cap.read()
        if not ret:
            break

        terminal_width, terminal_height = getterminalsize()
        target_width = min(480, max(40, terminal_width - 6))
        max_height = max(8, terminal_height - 2)
        ascii_lines = frame_to_ascii(frame, target_width, max_height)
        centered_lines = center_ascii(ascii_lines, terminal_width, terminal_height)
        display = centered_lines[:terminal_height]

        sys.stdout.write("\033[H\033[2J" + "\n".join(display) + "\033[0m")
        sys.stdout.flush()

        elapsed = time.time() - start_time
        frame_delay = (1 / fps) / speed_multiplier
        if frame_delay > elapsed:
            time.sleep(frame_delay - elapsed)

    cap.release()
    print("\nPlayback finished.")


if __name__ == "__main__":
    main()