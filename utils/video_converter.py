import os
import glob
import subprocess
import sys
import argparse


# This code is based in https://sempioneer.com/python-for-seo/converting-images-webp-python/

# Defining a Python user-defined exception


class Error(Exception):
    """Base class for other exceptions"""

    pass


def convert_video(video_path: str, long_video: bool) -> bool:
    try:
        command_list = ['ffmpeg', '-y', '-i', video_path, '-framerate', '30',
                        '-c:v', 'libvpx-vp9', '-an', '-vf', 'scale=512:512', '-pix_fmt', 'yuva420p',
                        'output_sticker.webm']
        if long_video:
            command_list.insert(1, "-threads")
            command_list.insert(2, "4")
            command_list.insert(3, "-ss")
            command_list.insert(4, "00:00:0.0")
            command_list.insert(5, "-t")
            command_list.insert(6, "3")

        print("Added cut args")
        print(command_list)
        subprocess.check_output(command_list)
        return True
    except subprocess.CalledProcessError as err:
        print("Error:" + str(err))
        return False


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--convert", "-c", help="Convert a jpg or png image to webp")
    args = parser.parse_args()
    if args.convert:
        image_path = str(argv[2])
        print(convert_video(image_path))


if __name__ == "__main__":
    main(sys.argv)
