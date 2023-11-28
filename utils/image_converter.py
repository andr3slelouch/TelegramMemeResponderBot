from PIL import Image
import PIL
import os
import glob
import sys
import argparse

# This code is based in https://sempioneer.com/python-for-seo/converting-images-webp-python/

# Defining a Python user-defined exception
class Error(Exception):
    """Base class for other exceptions"""

    pass


def convert_image(image_path, image_type, custom_size=512) -> str:
    # 1. Opening the image:
    im = Image.open(image_path)
    # 2. Converting the image to RGB colour:
    im = im.convert("RGB")
    # 3. Spliting the image path (to avoid the .jpg or .png being part of the image name):
    image_name = image_path.split(".")[0]
    print(f"This is the image name: {image_name}")

    # Saving the images based upon their specific type:
    if image_type == "jpg" or image_type == "png":
        """
        if not im.size[0] == 512:
            im.thumbnail(size=((custom_size, custom_size)))
            im.save(f"{image_name}.webp", "webp")
        else:
            im.save(f"{image_name}.webp", "webp")
        """
        im.thumbnail(size=((custom_size, custom_size)))
        im.save(f"{image_name}.webp", "webp")
        return f"{image_name}.webp"
    else:
        # Raising an error if we didn't get a jpeg or png file type!
        raise Error


def main(argv):
    parser = argparse.ArgumentParser()
    parser.add_argument("--convert", "-c", help="Convert a jpg or png image to webp")
    args = parser.parse_args()
    if args.convert:
        image_path = str(argv[2])
        image_type = image_path.split(".")[-1]
        convert_image(image_path, image_type)


if __name__ == "__main__":
    main(sys.argv)
