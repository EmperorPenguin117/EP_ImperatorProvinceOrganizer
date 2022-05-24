"""
This script just creates the definitions.csv file

Created by Emperor Penguin
11/16/2021
"""
import os
import random
import time
import numpy as np
from PIL import Image


start_time = time.time()
random.seed(1122)


def image_to_array(image_str):
    """
    Loads an image, hashes the RGB value, stores it in a numpy array, and returns it
    :param image_str:
    :return: bit_array
    """
    pic = Image.open(os.getcwd() + "\\" + image_str)
    array = np.array(pic, dtype="int32")
    bit_array = array[:, :, 0]*256*256 + array[:, :, 1]*256 + array[:, :, 2]
    return bit_array


def unhash_pixel(hashed_pixel):
    r = (hashed_pixel >> 16) & 0xFF
    g = (hashed_pixel >> 8) & 0xFF
    b = hashed_pixel & 0xFF
    return tuple((r, g, b))


def write_province_files_ir(prov_list, sea_prov_list):
    """
    Creates definitions.csv, provincenames_l_english.yml, and prov_names_adj_l_english.yml
    :return:
    """

    definitions = open(os.getcwd() + "\\definition.csv", "w")
    definitions.write(
        "#Province id 0 is ignored\n0;0;0;0;;x;;;;;;;;;;;;;;;;;\n")  # First line in any definitions file
    x = 0
    for x in range(len(prov_list)):
        color = prov_list[x]
        name = "Name"
        pixel = unhash_pixel(color)
        definitions.write("%d;%s;%s;%s;%s;x;;;;;;;;;;;;;;;;;;;\n" % (x + 1, pixel[0], pixel[1], pixel[2], name))
        x += 1

    # Sea
    for seacolor in sea_prov_list:
        pixel = unhash_pixel(seacolor)
        definitions.write("%d;%s;%s;%s;%s;x;;;;;;;;;;;;;;;;;;;\n" % (
            x + 1, pixel[0], pixel[1], pixel[2],
            "SeaName"))

        x += 1

    print("Finished Writing Province Files --- %s seconds ---" % (time.time() - start_time))


def main():
    print("Starting Script")
    land_prov_array = image_to_array("land_provinces.png")
    land_provs_set = set(land_prov_array.flatten())
    land_provs_set.remove(0)
    land_provs_list = list(land_provs_set)
    sea_prov_array = image_to_array("sea_provinces.png")
    sea_provs_set = set(sea_prov_array.flatten())
    sea_provs_list = list(sea_provs_set)
    write_province_files_ir(land_provs_list, sea_provs_list)


if __name__ == '__main__':
    main()
