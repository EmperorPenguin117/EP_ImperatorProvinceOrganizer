# Script to take RGB values from a PNG file and save them in an excel document. Formatting is consistent with naming
# files used in the province organizer.
# Author: Emperor Penguin 25-01-2021

import time
import numpy as np
from PIL import Image
import pandas as pd


start_time = time.time()
RGB_IMAGE_FILE = "characters.png"

def image_to_array_no_hash(image_str):
    """
    Loads an image, hashes the RGB value, stores it in a numpy array, and returns it
    :param image_str:
    :return: bit_array
    """
    pic = Image.open(image_str)
    array = np.array(pic, dtype="int32")
    return array

def image_to_array(image_str):
    """
    Loads an image, hashes the RGB value, stores it in a numpy array, and returns it
    :param image_str:
    :return: bit_array
    """
    pic = Image.open(image_str)
    array = np.array(pic, dtype="int32")
    bit_array = array[:,:,0]*256*256 + array[:,:,1]*256 + array[:,:,2]
    return bit_array

def unhash_pixel(hashed_pixel):
    r = (hashed_pixel >> 16) & 0xFF
    g = (hashed_pixel >> 8) & 0xFF
    b = hashed_pixel & 0xFF
    return tuple((r, g, b))

def main():
    print(f"Script Started -- {time.time() - start_time} seconds --")
    rgb_array = image_to_array(RGB_IMAGE_FILE)
    print(f"Image Read In -- {time.time() - start_time} seconds --")
    rgb_df = pd.DataFrame(set(rgb_array.flatten()))
    rgb_df.columns = ["RGB"]
    rgb_df["code_name"] = ""
    rgb_df["Name"] = ""
    print(f"Image Stored in Dataframe -- {time.time() - start_time} seconds --")
    rgb_df["RGB"] = rgb_df["RGB"].apply(lambda row: unhash_pixel(row))
    print(f"Pixels Unhashed -- {time.time() - start_time} seconds --")
    rgb_df.to_excel("RGB_excel_file.xlsx", index=False)
    print(f"File Written -- {time.time() - start_time} seconds --")

if __name__ == '__main__':
    main()