import ast
import os
import random
import time
import numpy as np
import xlrd
from PIL import Image
import pandas as pd
from collections import Counter
import glob
import io
import openpyxl
import codecs


start_time = time.time()

# INPUT_FILES_DIR = os.getcwd() + "\\Input_Files\\CK3Debug\\"
# INPUT_FILES_DIR = os.getcwd() + "\\Input_Files\\mu\\"
# INPUT_FILES_DIR = os.getcwd() + "\\Input_Files\\small\\"
# INPUT_FILES_DIR = os.getcwd() + "\\Input_Files\\IngameSmall\\"
# INPUT_FILES_DIR = os.getcwd() + "\\Input_Files\\GEMUpdate\\"
INPUT_FILES_DIR = os.getcwd() + "\\Input_Files\\"
OUTPUT_FILES_DIR = os.getcwd() + "\\Output_Files\\"

PIXEL_CHECKER = 1

class Province():
    def __init__(self, rgb, codename, name, capital_name, capital_loc_name):
        self.rgb = rgb
        self.codename = codename
        self.name = name#name.replace(' ', '_')
        self.capital_name = capital_name#capital_name.replace(' ', '_')
        self.capital_loc_name = capital_loc_name
        self.localisation_name = name
        self.county = []
        self.area = []
        self.region = []
        self.superregion = []
        self.country = []  # Used for IR
        self.character = []  # Used for CK3
        self.culture = []
        self.religion = []
        self.terrain = []
        self.trade_good = []
        self.province_modifier = []
        self.num_citizens, self.num_freemen, self.num_slaves, self.num_tribesmen =[], [], [], []
        self.development = []

    def add_all_pixels(self, prov_pix, area_pix, region_pix, superregion_pix, country_pix, char_pix, cul_pix, rel_pix, ter_pix, trade_goods_pix, prov_mod_mix, civ_pop_pix, tribe_pop_pix, dev_pix):
        # self.add_county_pix(county_pix)
        self.add_area_pix(area_pix)
        self.add_region_pix(region_pix)
        self.add_superregion_pix(superregion_pix)
        self.add_country_pix(country_pix)
        self.add_char_pix(char_pix)
        self.add_culture_pix(cul_pix)
        self.add_religion_pix(rel_pix)
        self.add_terrain_pix(ter_pix)
        self.add_trade_good_pix(trade_goods_pix)
        self.add_province_modifier_pix(prov_mod_mix)
        self.add_pop_pix(civ_pop_pix, tribe_pop_pix)
        self.add_dev_pix(dev_pix)

    def add_county_pix(self, county_pix):
        self.county.append(county_pix)

    def add_area_pix(self, area_pix):
        self.area.append(area_pix)

    def add_region_pix(self, region_pix):
        self.region.append(region_pix)

    def add_superregion_pix(self, superregion_pix):
        self.superregion.append(superregion_pix)

    def add_country_pix(self, country_pix):
        self.country.append(country_pix)

    def add_char_pix(self, char_pix):
        self.character.append(char_pix)

    def add_culture_pix(self, culture_pix):
        self.culture.append(culture_pix)

    def add_religion_pix(self, religion_pix):
        self.religion.append(religion_pix)

    def add_terrain_pix(self, terrain_pix):
        self.terrain.append(terrain_pix)

    def add_trade_good_pix(self, trade_good_pix):
        self.trade_good.append(trade_good_pix)

    def add_province_modifier_pix(self, province_modifier_pix):
        self.province_modifier.append(province_modifier_pix)

    def add_pop_pix(self, civ_pop_pix, tribe_pop_pix):
        self.num_citizens.append(civ_pop_pix[0])
        self.num_freemen.append(civ_pop_pix[1])
        self.num_slaves.append(civ_pop_pix[2])
        self.num_tribesmen.append(tribe_pop_pix[0])

    def add_dev_pix(self, dev_pix):
        self.development.append(dev_pix)

    def get_dominant_pixels(self):
        self.dom_area = Counter(self.area).most_common(1)


# class Character():
#     def __init__(self, rgb):
#         self.


class Map():
    def __init__(self):
        self.gen_kingdoms = True
        self.gen_empires = True
        self.load_excel_province_assignments()
        self.load_all_names()
        self.get_province_modifiers((88, 11, 17))
        self.get_country_params()  # Loads country parameters from an excel file and stores them in a list of lists
        self.initial_file_setup_ir()
        self.initial_file_setup_ck3()
        self.load_images()  # Loading in all images used to create game files
        self.width = len(self.land_province_array)  # Width dimension of the map
        self.height = len(self.land_province_array[0])  # Height dimension of the map
        self.create_sets()  # Creates sets of all province arrays
        self.create_lists()  # Converts the appropriate sets to lists
        self.generate_random_names()  # Generates random names for provinces, areas, and regions
        self.reconcile_all_names()
        self.assign_provinces()  # Main loops that creates hierarchical relationships and province histories


        self.write_files()  # Writes all the files that are used in game
        print("Program Complete --- %s seconds ---" % (time.time() - start_time))

    @staticmethod
    def image_to_array(image_str):
        """
        Loads an image, hashes the RGB value, stores it in a numpy array, and returns it
        :param image_str:
        :return: bit_array
        """
        pic = Image.open(INPUT_FILES_DIR + image_str)
        array = np.array(pic, dtype="int32")
        bit_array = array[:,:,0]*256*256 + array[:,:,1]*256 + array[:,:,2]
        return bit_array

    @staticmethod
    def image_to_array_no_hash(image_str):
        """
        Loads an image, hashes the RGB value, stores it in a numpy array, and returns it
        :param image_str:
        :return: bit_array
        """
        pic = Image.open(INPUT_FILES_DIR + image_str)
        array = np.array(pic, dtype="int32")
        return array

    @staticmethod
    def directory_setup(path):
        """
        Creates directories if they do not exist
        :param path:
        :return: path
        """

        try:
            os.makedirs(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
            return path
        else:
            print("Successfully created the directory %s " % path)
            return path

    def initial_file_setup_ir(self):
        """
        Creates the necessary directories and files. Will throw an error if the directories already exist but that can be ignored
        :return: map directory, localisation directory
        """
        self.out_dir = self.directory_setup(os.getcwd() + "\\Output_Files\\")
        self.localisation_dir = self.directory_setup(os.getcwd() + "\\Output_Files\\localisation\\")
        self.map_dir = self.directory_setup(os.getcwd() + "\\Output_Files\\map_data\\")
        self.setup_dir = self.directory_setup(os.getcwd() + "\\Output_Files\\setup\\provinces\\")

        self.prov_setup = open(self.setup_dir + "ge_provinces.txt", "w")
        self.area_file = open(self.map_dir + "areas.txt", "w")
        self.area_file.write("# Administrative areas.\n\n")
        self.region_file = open(self.map_dir + "regions.txt", "w")
        self.region_file.write("## Regions ##\n")
        self.country_file = open(self.map_dir + "country_setup_provinces.txt", "w")
        self.country_file.write("## Countries ##\n")

        self.country_tags_file = open(self.map_dir + "countries.txt", "w")
        self.country_tags_file.write("## Generic ##\n")
        self.country_tags_file.write(
            'REB = "countries/rebels.txt"\nPIR = "countries/pirates.txt"\nBAR = "countries/barbarians.txt"\nMER = "countries/mercenaries.txt"\n\n')
        
    def initial_file_setup_ck3(self):
        """
        Creates the necessary directories and files. Will throw an error if the directories already exist but that can be ignored
        :return: map directory, localisation directory
        """
        self.out_dir_ck3 = self.directory_setup(os.getcwd() + "\\Output_Files\\CK3\\")
        self.localisation_dir_ck3 = self.directory_setup(self.out_dir_ck3 + "localisation\\")
        self.map_dir_ck3 = self.directory_setup(self.out_dir_ck3 + "map_data\\")
        self.history_dir_ck3 = self.directory_setup(self.out_dir_ck3 + "history\\provinces\\")

        self.common_dir_ck3 = self.directory_setup(self.out_dir_ck3 + "common\\")

    def load_images(self):
        """
        Loads all images
        :return:
        """
        self.culture_array = self.image_to_array("culture.png")
        self.religion_array = self.image_to_array("religion.png")
        self.terrain_array = self.image_to_array("terrain.png")
        self.trade_good_array = self.image_to_array("trade_goods.png")
        self.province_modifier_array = self.image_to_array("province_modifiers.png")

        self.civilized_population_array = self.image_to_array("civilized_population.png")
        self.tribal_population_array = self.image_to_array("tribal_population.png")
        self.development_array = self.image_to_array("development.png")

        self.land_province_array = self.image_to_array("land_provinces.png")
        # self.county_array = self.image_to_array("land_counties.png")
        self.area_array = self.image_to_array("land_areas.png")
        self.region_array = self.image_to_array("land_regions.png")
        self.superregion_array = self.image_to_array("superregions.png")
        self.country_array = self.image_to_array("countries_ir.png")
        self.character_array = self.image_to_array("characters.png")

        self.sea_province_array = self.image_to_array("sea_provinces.png")
        self.river_province_array = self.image_to_array("river_provinces.png")

        print("All images loaded --- %s seconds ---" % (time.time() - start_time))

    def create_sets(self):
        """
        Creates sets used for assignments. Some are later converted to lists in the function create_lists. They are
        loaded as sets first because sets only contain unique values, meaning loading them as sets first is a fast way
        to get rid of duplicates.
        :return:
        """

        self.land_provs_set = set(self.land_province_array.flatten())
        # self.counties_set = set(self.county_array.flatten())
        self.areas_set = set(self.area_array.flatten())
        self.regions_set = set(self.region_array.flatten())
        self.superregions_set = set(self.superregion_array.flatten())
        self.countries_set = set(self.country_array.flatten())
        self.sea_provs_set = set(self.sea_province_array.flatten())
        self.river_prov_set = set(self.river_province_array.flatten())
        self.characters_set = set(self.character_array.flatten())
        self.character_id_set = set()

        # These sets are created for assigning provinces and areas.
        # When a province is assigned to an area, it is removed from self.used_provs so it can't be assigned again
        self.used_provs = self.land_provs_set.copy()
        self.region_areas_set = self.areas_set.copy()
        self.country_provs_set = self.land_provs_set.copy()


        self.sea_level_pixel = self.hash_pixel((0, 0, 0))
        self.impassable_pixel = self.hash_pixel((50, 50, 50))
        self.remove_waste_sea(self.sea_provs_set)
        self.remove_waste_sea(self.river_prov_set)
        print("All sets created --- %s seconds ---" % (time.time() - start_time))

    def create_lists(self):
        """
        Converts sets into lists. This gives them index values so they can be assigned by number. Essentially this makes
        sure that when a province RGB is written in definitions.csv it has the same province id as when it is assigned
        to an area or a country.

        The second group of lists created are lists of lists for assigning provinces to areas, areas to regions, etc.
        :return:
        """
        self.prov_list = list(self.land_provs_set)
        # self.counties_list = list(self.counties_list)
        self.areas_list = list(self.areas_set)
        self.regions_list = list(self.regions_set)
        self.superregions_list = list(self.superregions_set)
        self.sea_prov_list = list(self.sea_provs_set)
        self.river_prov_list = list(self.river_prov_set)
        self.countries_list = list(self.countries_set)

        self.prov_characters_list = [""] * len(self.land_provs_set)
        self.area_characters_list = [""] * len(self.areas_set)
        self.region_characters_list = [""] * len(self.regions_set)
        self.superregion_characters_list = [""] * len(self.superregions_set)

        self.culture_list = [""] * len(self.land_provs_set)
        self.religion_list = [""] * len(self.land_provs_set)
        self.terrain_list = [""] * len(self.land_provs_set)
        self.trade_good_list = [""] * len(self.land_provs_set)
        self.province_modifier_list = [""] * len(self.land_provs_set)
        self.province_population_list = [(100,100,100,101)] * len(self.land_provs_set)
        self.development_list = [0] * len(self.land_provs_set)
        ######################## Initializes lists of lists for storing hierarchical assignments #######################
        self.prov_obj = [None]*len(self.prov_list)

        self.area_prov_assign = [[] for x in range(0, len(self.areas_list))]
        self.region_area_assign = [set() for x in range(0, len(self.regions_list))]
        self.superregion_region_assign = [set() for x in range(0, len(self.superregions_list))]
        self.country_prov_assign = [[] for x in range(0, len(self.countries_list))]
        ################################################################################################################
        print("All lists created --- %s seconds ---" % (time.time() - start_time))

    def load_names(self, dir):
        all_name_files = glob.glob(INPUT_FILES_DIR + dir + "\\" + "/*.xlsx")
        list_of_name_files = []
        for filename in all_name_files:
            df = pd.read_excel(filename)
            list_of_name_files.append(df)
        all_names_df = pd.concat(list_of_name_files, axis=0, ignore_index=True)
        all_names_rgb_array = np.array(all_names_df["RGB"])
        all_prov_names_rgb_set = set()
        for rgb in all_names_rgb_array:
            all_prov_names_rgb_set.add(rgb)
        #     self.all_names_df.set_value()
        #all_names_df["code_name"] = all_names_df["code_name"].replace(' ', '_', regex=True)
        return all_names_df, all_prov_names_rgb_set


    def load_all_names(self):
        self.all_prov_names_df, self.all_prov_names_rgb_set = self.load_names("province_names")
        self.all_area_names_df, self.all_area_names_rgb_set = self.load_names("duchy_names")
        self.all_region_names_df, self.all_region_names_rgb_set = self.load_names("kingdom_names")
        self.all_superregion_names_df, self.all_superregion_names_rgb_set = self.load_names("empire_names")
        self.test_names_for_utf8(self.all_prov_names_df, 'codename_county')
        x=0


    @staticmethod
    def test_names_for_utf8(df, column):
        for name_idx, name in enumerate(df[column]):
            try:
                for char_idx, character in enumerate(name):
                    order = ord(character)
                    if order > 128:
                        print(f"Problem with index {name_idx}, {char_idx}th character")
                        print(name)
            except:
                print(f'Problem with name_idx = {name_idx}')
                print(f'Problem with name {name}')

    def assign_provinces(self):
        """
        The main loop where the magic happens
        :return:
        """
        seacheck = 0
        impcheck = 0
        print("Starting Assignments --- %s seconds ---" % (time.time() - start_time))
        for x in range(int(self.width)):
            if x % 100 == 0:
                print(f"idx = {x} --- {time.time() - start_time} seconds ---")

            land_prov_array_x = self.land_province_array[x]
            areas_array_x = self.area_array[x]
            regions_array_x = self.region_array[x]
            superregion_array_x = self.superregion_array[x]
            countries_array_x = self.country_array[x]
            character_array_x = self.character_array[x]

            culture_array_x = self.culture_array[x]
            religion_array_x = self.religion_array[x]
            terrain_array_x = self.terrain_array[x]
            trade_good_array_x = self.trade_good_array[x]
            province_modifier_array_x = self.province_modifier_array[x]
            civilized_population_array_x = self.civilized_population_array[x]
            tribal_population_array_x = self.tribal_population_array[x]
            development_array_x = self.development_array[x]


            for y in range(self.height):
                prov_pixel = land_prov_array_x[y]
                area_pixel = areas_array_x[y]
                region_pixel = regions_array_x[y]
                superregion_pixel = superregion_array_x[y]
                country_pixel = countries_array_x[y]
                character_pixel = character_array_x[y]

                culture_pixel = culture_array_x[y]
                religion_pixel = religion_array_x[y]
                terrain_pixel = terrain_array_x[y]
                trade_good_pixel = trade_good_array_x[y]
                province_modifier_pixel = province_modifier_array_x[y]
                civilized_population_pixel = civilized_population_array_x[y]
                tribal_population_pixel = tribal_population_array_x[y]
                development_pixel = development_array_x[y]
                if prov_pixel == self.sea_level_pixel and seacheck == 0:
                    self.create_prov_history(prov_pixel)
                    self.used_provs.remove(prov_pixel)

                    seacheck = 1
                if prov_pixel == self.impassable_pixel and impcheck == 0:
                    self.create_prov_history(prov_pixel)
                    self.used_provs.remove(prov_pixel)

                    impcheck = 1

                if prov_pixel != self.sea_level_pixel and prov_pixel != self.impassable_pixel:
                    if prov_pixel in self.used_provs:
                        self.create_prov_history(prov_pixel)
                        self.used_provs.remove(prov_pixel)
                    elif x*y % PIXEL_CHECKER**2 == 0:
                        self.expand_prov_history(prov_pixel, area_pixel, region_pixel, superregion_pixel, country_pixel,
                                                 character_pixel, culture_pixel, religion_pixel, terrain_pixel,
                                                 trade_good_pixel, province_modifier_pixel, civilized_population_pixel,
                                                 tribal_population_pixel, development_pixel)

        print(f"Length of self.used_provs = {len(self.used_provs)}")

        self.consolidate_prov_history()
        print("Assignments Completed --- %s seconds ---" % (time.time() - start_time))

    def expand_prov_history(self, prov_pixel, area_pixel, region_pixel, superregion_pixel, country_pixel, character_pixel, culture_pixel, religion_pixel, terrain_pixel, trade_good_pixel, province_modifier_pixel, civilized_population_pixel, tribal_population_pixel, development_pixel):
        idx = self.prov_list.index(prov_pixel)
        self.prov_obj[idx].add_all_pixels(prov_pixel, area_pixel, region_pixel, superregion_pixel, country_pixel,
                                          character_pixel, (culture_pixel), (religion_pixel),
                                          (terrain_pixel), (trade_good_pixel),
                                          (province_modifier_pixel), self.unhash_pixel(civilized_population_pixel), self.unhash_pixel(tribal_population_pixel),
                                          self.unhash_pixel(development_pixel))


    def create_prov_history(self, prov_pixel):
        unhashed_prov_pixel = str(self.unhash_pixel(prov_pixel))
        idx = self.prov_list.index(prov_pixel)

        if unhashed_prov_pixel in self.all_prov_names_rgb_set:
            if not pd.isna((self.all_prov_names_df.loc[self.all_prov_names_df["RGB"] == unhashed_prov_pixel].iloc[0])["codename_county"]):
                prov_name = (self.all_prov_names_df.loc[self.all_prov_names_df["RGB"] == unhashed_prov_pixel].iloc[0])["codename_county"]
                prov_loc_name = (self.all_prov_names_df.loc[self.all_prov_names_df["RGB"] == unhashed_prov_pixel].iloc[0])["Name_county"]
            else:
                if not pd.isna((self.all_prov_names_df.loc[self.all_prov_names_df["RGB"] == unhashed_prov_pixel].iloc[0])["codename_barony"]):
                    capital_name = (self.all_prov_names_df.loc[self.all_prov_names_df["RGB"] == unhashed_prov_pixel].iloc[0])["codename_barony"]
                    capital_loc_name = (self.all_prov_names_df.loc[self.all_prov_names_df["RGB"] == unhashed_prov_pixel].iloc[0])["Name_barony"]
                    # print(f"Province with RGB {unhashed_prov_pixel} is called {prov_name}")
                    prov_name = capital_name
                    prov_loc_name = capital_loc_name
                else:
                    prov_name = self.prov_names[idx]
                    prov_loc_name = self.prov_loc_names[idx]

            if not pd.isna((self.all_prov_names_df.loc[self.all_prov_names_df["RGB"] == unhashed_prov_pixel].iloc[0])["codename_barony"]):
                capital_name = (self.all_prov_names_df.loc[self.all_prov_names_df["RGB"] == unhashed_prov_pixel].iloc[0])["codename_barony"]
                capital_loc_name = (self.all_prov_names_df.loc[self.all_prov_names_df["RGB"] == unhashed_prov_pixel].iloc[0])["Name_barony"]
                # print(f"Province with RGB {unhashed_prov_pixel} is called {prov_name}")
            else:
                capital_name = self.prov_capital_names[idx]
                capital_loc_name = self.prov_loc_capital_names[idx]

        else:
            prov_name = self.prov_names[idx]
            prov_loc_name = self.prov_loc_names[idx]
            capital_name = self.prov_capital_names[idx]
            capital_loc_name = self.prov_loc_capital_names[idx]


        self.prov_obj[idx] = Province(prov_pixel, prov_name, prov_loc_name, capital_name, capital_loc_name)

        self.prov_names[idx] = prov_name
        self.prov_capital_names[idx] = capital_name
        self.prov_loc_names[idx] = prov_loc_name
        self.prov_loc_capital_names[idx] = capital_loc_name

    def reconcile_names(self, pixel, pixel_list, names_df, names_set, names_list, titletype="code_name"):
        unhashed_prov_pixel = str(self.unhash_pixel(pixel))

        idx = pixel_list.index(pixel)
        if unhashed_prov_pixel in names_set:
            prov_name = (names_df.loc[names_df["RGB"] == unhashed_prov_pixel].iloc[0])[titletype]
            # print(f"Province with RGB {unhashed_prov_pixel} is called {prov_name}")
        else:
            prov_name = self.prov_names[idx]
        names_list[idx] = prov_name
        return names_list

    def reconcile_all_names(self):
        for area in self.areas_list:
            self.area_names = self.reconcile_names(area, self.areas_list, self.all_area_names_df, self.all_area_names_rgb_set, self.area_names, titletype="codename_duchy")
            self.area_loc_names = self.reconcile_names(area, self.areas_list, self.all_area_names_df, self.all_area_names_rgb_set, self.area_loc_names, titletype="Name")
        for region in self.regions_list:
            self.region_names = self.reconcile_names(region, self.regions_list, self.all_region_names_df, self.all_region_names_rgb_set, self.region_names, titletype="codename_kingdom")
            self.region_loc_names = self.reconcile_names(region, self.regions_list, self.all_region_names_df, self.all_region_names_rgb_set, self.region_loc_names, titletype="Name")
        for superregion in self.superregions_list:
            self.superregion_names = self.reconcile_names(superregion, self.superregions_list, self.all_superregion_names_df, self.all_superregion_names_rgb_set, self.superregion_names, titletype="codename_empire")
            self.superregion_loc_names = self.reconcile_names(superregion, self.superregions_list, self.all_superregion_names_df, self.all_superregion_names_rgb_set, self.superregion_loc_names, titletype="Name")

        x = 0



    def consolidate_prov_history(self):
        print("Consolidating Provinces --- %s seconds ---" % (time.time() - start_time))
        for province in self.prov_obj:
            idx = self.prov_obj.index(province)
            if idx % 100 == 0:
                print(f"idx = {idx} --- {time.time() - start_time} seconds ---")
            try:
                area_pix = Counter(province.area).most_common()[0][0]
                region_pix = Counter(province.region).most_common()[0][0]
                superregion_pix = Counter(province.superregion).most_common()[0][0]
                country_pix = Counter(province.country).most_common()[0][0]
                if country_pix == 0:
                    country_pix = Counter(province.country).most_common()[1][0]

                prov_character_pix = Counter(province.character).most_common()[0][0]


                culture_pix = Counter(province.culture).most_common()[0][0]
                religion_pix = Counter(province.religion).most_common()[0][0]
                terrain_pix = Counter(province.terrain).most_common()[0][0]
                trade_good_pix = Counter(province.trade_good).most_common()[0][0]
                province_modifier_pix = Counter(province.province_modifier).most_common()[0][0]
                num_citizens_pix = Counter(province.num_citizens).most_common()[0][0]
                num_freemen_pix = Counter(province.num_freemen).most_common()[0][0]
                num_slaves_pix = Counter(province.num_slaves).most_common()[0][0]
                num_tribesmen_pix = Counter(province.num_tribesmen).most_common()[0][0]
                development_pix = Counter(province.development).most_common()[0][0]
            except:
                print(f"Problem RGB")# = {self.unhash_pixel(province.rgb)}")


            if province.rgb != self.impassable_pixel and province.rgb != self.sea_level_pixel:
                self.area_prov_assign[self.areas_list.index((area_pix))].append(idx + 1)

                # try:
                #     country_pix = str(self.unhash_pixel(country_pix)) # CHANGED
                # except:
                #     print(f'Problem Country Pixel Province: RGB = {province.rgb}, country_pix type = {type(country_pix)}')
                try:
                    country_idx = self.countries_list.index((country_pix))
                except:
                    country_idx = 0

                self.country_prov_assign[country_idx].append(idx + 1)
                # if area_pix not in self.regions_list.index(region_pix):
                self.region_area_assign[self.regions_list.index((region_pix))].add(self.areas_list.index(area_pix))
                self.superregion_region_assign[self.superregions_list.index((superregion_pix))].add(self.regions_list.index(region_pix))

                character_id = self.get_character(self.unhash_pixel(prov_character_pix))
                culture = self.get_culture((self.unhash_pixel(culture_pix)))
                religion = self.get_religion((self.unhash_pixel(religion_pix)))
                terrain = self.get_terrain((self.unhash_pixel(terrain_pix)))
                trade_good = self.get_trade_good((self.unhash_pixel(trade_good_pix)))
                province_modifier = self.get_province_modifiers((self.unhash_pixel(province_modifier_pix)))
                num_citizens, num_freemen, num_slaves, num_tribesmen = self.get_population((num_citizens_pix, num_freemen_pix, num_slaves_pix), num_tribesmen_pix)
                development = self.get_development(development_pix)

                self.prov_characters_list[idx] = character_id
                self.culture_list[idx] = culture
                self.religion_list[idx] = religion
                self.terrain_list[idx] = terrain
                self.trade_good_list[idx] = trade_good
                self.province_modifier_list[idx] = province_modifier
                self.province_population_list[idx] = (num_citizens, num_freemen, num_slaves, num_tribesmen)
                self.development_list[idx] = development

        for region in (self.region_area_assign):
            self.region_area_assign[self.region_area_assign.index(region)] = list(region)
        for superregion in self.superregion_region_assign:
            self.superregion_region_assign[self.superregion_region_assign.index(superregion)] = list(superregion)

    def load_all_excel_files_in_folder(self, folder):
        all_name_files = glob.glob(folder + "\\" + "/*.xlsx")
        list_of_name_files = []
        for filename in all_name_files:
            df = pd.read_excel(filename)
            list_of_name_files.append(df)
        all_names_df = pd.concat(list_of_name_files, axis=0, ignore_index=True)
        return all_names_df

    def load_excel_province_assignments(self):
        cultures_folder_directory = (INPUT_FILES_DIR + "cultures" + "\\")
        self.cultures_df = self.load_all_excel_files_in_folder(cultures_folder_directory)
        religions_folder_directory = (INPUT_FILES_DIR + "religions" + "\\")
        self.religions_df = self.load_all_excel_files_in_folder(religions_folder_directory)
        terrains_file_location = (INPUT_FILES_DIR + "terrains.xlsx")
        self.terrains_df = pd.read_excel(terrains_file_location, engine="openpyxl")
        trade_goods_file_location = (INPUT_FILES_DIR + "trade_goods.xlsx")
        self.trade_goods_df = pd.read_excel(trade_goods_file_location, engine="openpyxl")
        province_modifiers_file_location = (INPUT_FILES_DIR + "province_modifiers.xlsx")
        self.province_modifiers_df = pd.read_excel(province_modifiers_file_location, engine="openpyxl")

        characters_folder_directory = (INPUT_FILES_DIR + "characters" + "\\")
        self.characters_df = self.load_all_excel_files_in_folder(characters_folder_directory)
        x=0

    def get_culture(self, culture_pixel):

        """
        Returns the culture of the province
        :return:
        """


        try:
            cul = self.cultures_df['Culture'][np.where(self.cultures_df['RGB'] == str((culture_pixel[0], culture_pixel[1], culture_pixel[2])))[0][0]]
        except:
            cul = "test_culture"
        return cul

    def get_religion(self, religion_pixel):
        """
        Returns the religion of the province
        :return:
        """

        try:
            rel = self.religions_df['Religion'][np.where(self.religions_df['RGB'] == str((religion_pixel[0], religion_pixel[1], religion_pixel[2])))[0][0]]
        except:
            rel = "test_faith"
        return rel

    def get_terrain(self, terrain_pixel):
        """
        Returns the terrain of the province
        :return:
        """

        try:
            ter = self.terrains_df['Terrain'][np.where(self.terrains_df['RGB'] == str((terrain_pixel[0], terrain_pixel[1], terrain_pixel[2])))[0][0]]
        except:
            ter = "plains"
        return ter

    def get_trade_good(self, trade_good_pixel):
        """
        Returns the trade good of the province
        :return:
        """

        try:
            tg = self.trade_goods_df['Trade Good'][np.where(self.trade_goods_df['RGB'] == str((trade_good_pixel[0], trade_good_pixel[1], trade_good_pixel[2])))[0][0]]
        except:
            tg = "fur"
        return tg

    def get_character(self, char_pixel):
        """
        Returns the trade good of the province
        :return:
        """

        try:
            char = self.characters_df['ID'][np.where(self.characters_df['RGB'] == str((char_pixel[0], char_pixel[1], char_pixel[2])))[0][0]]
            self.character_id_set.add(char)
        except:
            char = "empty"
        return char

    def get_province_modifiers(self, pm_pixel):
        """
        Returns the province modifier of the province
        :return:
        """

        try:
            pm = self.province_modifiers_df['Province Modifier'][np.where(self.province_modifiers_df['RGB'] == str((pm_pixel[0], pm_pixel[1], pm_pixel[2])))[0][0]]
        except:
            pm = None
        return pm

    def get_population(self, civ_pop_pixel, tribal_pop_pixel):
        num_citizens = (civ_pop_pixel[0]-100)
        num_freemen = (civ_pop_pixel[1]-100)
        num_slaves = (civ_pop_pixel[2] - 100)
        num_tribesmen = (tribal_pop_pixel - 100)
        return num_citizens, num_freemen, num_slaves, num_tribesmen

    def get_development(self, dev_pixel):
        dev = dev_pixel[0]
        development = (dev-50)/10
        return development

    def write_files(self):

        self.write_province_files_ck3()
        self.write_landed_titles_ck3()
        self.write_province_history_files_ck3()
        self.write_characters_and_owners_ck3()
        self.write_province_files_ir()
        self.write_area_file()
        self.write_region_file()
        self.write_country_files()# XLRD DEPRECATED
        self.write_terrain_file()

    def get_country_params(self): # XLRD DEPRECATED
        """
        Reads in country parameters file and stores it in a list of lists
        :return:
        """

        country_parameters_file_location = (INPUT_FILES_DIR + "country_parameters.xlsx")
        country_parameters_file = xlrd.open_workbook(country_parameters_file_location)
        country_params = list(map(list, []))
        for s in country_parameters_file.sheets():
            for row in range(s.nrows):
                values = []
                for col in range(s.ncols):
                    values.append(s.cell(row, col).value)
                country_params.append(values)

        self.country_params = country_params

    def generate_random_names(self):
        """
        Generates random names if the names aren't being loaded from another source.
        :return:
        """
        self.prov_names, self.prov_adj = self.random_name_generator(len(self.prov_list))
        self.prov_loc_names, self.prov_loc_adj = self.prov_names.copy(), self.prov_adj.copy()
        self.prov_capital_names, self.prov_capital_adj = self.prov_names.copy(), self.prov_adj.copy()
        self.prov_loc_capital_names, self.prov_loc_capital_adj = self.prov_names.copy(), self.prov_adj.copy()

        self.area_names, self.area_adj = self.random_name_generator(len(self.area_prov_assign))
        self.area_loc_names, self.area_loc_adj = self.area_names.copy(), self.area_adj.copy()
        self.region_names, self.region_adj = self.random_name_generator(len(self.region_area_assign))
        self.region_loc_names, self.region_loc_adj = self.region_names.copy(), self.region_adj.copy()
        self.superregion_names, self.superregion_adj = self.random_name_generator(len(self.superregion_region_assign))
        self.superregion_loc_names, self.superregion_loc_adj = self.superregion_names.copy(), self.superregion_adj.copy()

        self.sea_prov_names, self.sea_adj = self.random_name_generator(len(self.sea_prov_list)*2, sea=True)
        self.river_prov_names, self.river_prov_adj = self.random_name_generator((len(self.river_prov_list)*2), river=True)
        print("Random Names Generated --- %s seconds ---" % (time.time() - start_time))

    def random_name_generator(self, number_names, num_syllables=2, sea=False, river=False):
        """
        Generates a list of names and their adjectives
        :param number_names:
        :param num_syllables:
        :param sea:
        :return: name_list, adjective_list
        """
        syllables_file = open(INPUT_FILES_DIR + "syllables.csv", "r")  # Opens csv file with all syllables
        end_syllables_file = open(INPUT_FILES_DIR + "end_syllables.csv", "r")  # Opens csv file with all end syllables

        syllables = [syl.rstrip('\n') for syl in syllables_file]  # Reads in syllables from a csv file
        end_syllables = [esyl.rstrip('\n') for esyl in end_syllables_file]  # Reads in end syllables from a csv files

        name_list = set()
        adjective_list = set()
        i = 0

        while i < number_names:
            # if i % 1000 == 0:
            #     print(i)

            Name = ""

            for s in range(0, num_syllables):
                pick_syllable = random.randint(0, len(syllables) - 1)
                syllable_used = syllables[pick_syllable]
                Name += syllable_used

            end_syllable_picker = random.randint(0, len(end_syllables) - 1)
            end_syllable_used = end_syllables[end_syllable_picker]
            Name += end_syllable_used

            FinalName = Name.title()
            if FinalName not in name_list:

                Adj = Name
                if Adj.endswith("n"):
                    Adj += "ish"
                elif Adj.endswith("d"):
                    Adj = Adj[:3]
                    Adj += "ish"
                elif Adj.endswith("a"):
                    Adj += "n"
                else:
                    Adj += "ic"

                FinalAdj = Adj.title()
                # if FinalAdj in adjective_list:
                # print("Debug")
                adjective_list.add(FinalAdj)

                if sea:
                    FinalName += "an Sea"
                elif river:
                    FinalName += "River"
                name_list.add(FinalName)

                i += 1
        return list(name_list), list(adjective_list)

    def write_province_files_ir(self):
        """
        Creates definitions.csv, provincenames_l_english.yml, and prov_names_adj_l_english.yml
        :return:
        """
        # prov_list[x].province_id.index(prov_list[x].rgb)
        # prov_list = prov_list[0].province_id
        # sea_prov_list = sea_prov_list[0].sea_province_id
        # river_prov_list = river_prov_list[0].river_province_id

        local_file = io.open(self.localisation_dir + "provincenames_l_english.yml", "w", encoding="utf-8")
        local_file.write("l_english:\n")  # First line in any English localisation file
        local_file_adj = io.open(self.localisation_dir + "prov_names_adj_l_english.yml", "w", encoding="utf-8")
        local_file_adj.write("l_english:\n")

        definitions = open(self.map_dir + "definition.csv", "w")
        definitions.write(
            "#Province id 0 is ignored\n0;0;0;0;;x;;;;;;;;;;;;;;;;;\n")  # First line in any definitions file
        prov_setup = open(self.setup_dir + "ge_provinces.txt", "w")
        x = 0
        for x in range(len(self.prov_list)):
            color = self.prov_list[x]
            name = self.prov_obj[x].codename
            ind = self.prov_list.index(color)

            out = "%d - " % (x + 1)
            out += name
            out2 = self.prov_loc_adj[self.prov_list.index(color)]


            local_file.write(' PROV{0}:0 "{1}"\n'.format(x + 1, out.split(" - ")[1]))
            local_file_adj.write(' PROV{0}:0 "{1}"\n'.format(x + 1, out2))


            pixel = self.unhash_pixel(color)

            try:
                definitions.write("%d;%s;%s;%s;%s;x;;;;;;;;;;;;;;;;;;;\n" % (
                x + 1, pixel[0], pixel[1], pixel[2], self.prov_obj[x].codename))
            except:
                print("x")

            prov_setup.write(f"""
    {x+1}={{ #{name}
        terrain="{self.terrain_list[ind]}"
        culture="{self.culture_list[ind]}"
        religion="{self.religion_list[ind]}"
        trade_goods="{self.trade_good_list[ind]}"
        civilization_value=0
        barbarian_power=0
        province_rank="settlement"
        citizen={{
            amount={self.province_population_list[ind][0]}
        }}
        freemen={{
            amount={self.province_population_list[ind][1]}
        }}
        slaves={{
            amount={self.province_population_list[ind][2]}
        }}
        tribesmen={{
            amount={self.province_population_list[ind][3]}
        }}
    }}
            """)

            x += 1
        # Sea
        s = 0
        for seacolor in self.sea_prov_list:
            ind = self.sea_prov_list.index(seacolor)

            out = "%d - " % (x + 1)
            out += self.sea_prov_names[self.sea_prov_list.index(seacolor)]

            local_file.write(' PROV{0}:0 "{1}"\n'.format(x + 1, out.split(" - ")[1]))

            pixel = self.unhash_pixel(seacolor)
            definitions.write("%d;%s;%s;%s;%s;x;;;;;;;;;;;;;;;;;;;\n" % (
                x + 1, pixel[0], pixel[1], pixel[2],
                self.sea_prov_names[ind]))

            prov_setup.write("""
    {0}={{ #{1}
        terrain="coastal_terrain"
        culture=""
        religion=""
        trade_goods=""
        civilization_value=0
        barbarian_power=0
        province_rank=""
    }}
                    """.format(x + 1, self.sea_prov_names[self.sea_prov_list.index(seacolor)]))

            # print(s)
            s += 1
            x += 1

        r = 0
        for rivercolor in self.river_prov_list:
            ind = self.river_prov_list.index(rivercolor)
            out = "%d - " % (x + 1)
            out += self.river_prov_names[ind]

            local_file.write(' PROV{0}:0 "{1}"\n'.format(x + 1, out.split(" - ")[1]))
            pixel = self.unhash_pixel(rivercolor)
            definitions.write("%d;%s;%s;%s;%s;x;;;;;;;;;;;;;;;;;;;\n" % (
                x + 1, pixel[0], pixel[1],pixel[2],
                self.river_prov_names[self.river_prov_list.index(rivercolor)]))

            prov_setup.write("""
    {0}={{ #{1}
        terrain="riverine_terrain"
        culture=""
        religion=""
        trade_goods=""
        civilization_value=0
        barbarian_power=0
        province_rank=""
    }}
                    """.format(x + 1, self.river_prov_names[self.river_prov_list.index(rivercolor)]))

            # print(s)
            s += 1
            x += 1
            r += 1
        print("Finished Writing Province Files --- %s seconds ---" % (time.time() - start_time))

    def write_province_files_ck3(self):
        """
        Creates definitions.csv, provincenames_l_english.yml, and prov_names_adj_l_english.yml
        :return:
        """
        # prov_list[x].province_id.index(prov_list[x].rgb)
        # prov_list = prov_list[0].province_id
        # sea_prov_list = sea_prov_list[0].sea_province_id
        # river_prov_list = river_prov_list[0].river_province_id

        local_file = open(self.localisation_dir_ck3 + "provincenames_l_english.yml", "w", encoding="utf-8")
        local_file.write("l_english:\n")  # First line in any English localisation file
        local_file_adj = open(self.localisation_dir_ck3 + "prov_names_adj_l_english.yml", "w", encoding="utf-8")
        local_file_adj.write("l_english:\n")

        definitions = open(self.map_dir_ck3 + "definition.csv", "w")
        definitions.write("0;0;0;0;x;x;\n")  # First line in any definitions file

        x = 0
        for x in range(len(self.prov_list)):
            color = self.prov_list[x]
            ind = self.prov_list.index(color)

            out = "%d - " % (x + 1)
            out += self.prov_loc_names[self.prov_list.index(color)]
            out2 = self.prov_adj[self.prov_list.index(color)]
            local_file.write(' PROV{0}:0 "{1}"\n'.format(x + 1, out.split(" - ")[1]))
            local_file_adj.write(' PROV{0}:0 "{1}"\n'.format(x + 1, out2))

            pixel = self.unhash_pixel(color)
            col_ind = self.prov_list.index(color)
            def_name = self.prov_names[col_ind]
            loc_name = self.prov_loc_names[col_ind]
            # print(f'pixel = {pixel}, col_ind = {col_ind}, def_name = {def_name}, loc_name = {loc_name}')
            definitions.write("%d;%s;%s;%s;%s;x;\n" % (
                x + 1, pixel[0], pixel[1], pixel[2], def_name))



            x += 1
        # Sea
        s = 0
        for seacolor in self.sea_prov_list:
            ind = self.sea_prov_list.index(seacolor)

            out = "%d - " % (x + 1)
            out += self.sea_prov_names[ind]

            local_file.write(' PROV{0}:0 "{1}"\n'.format(x + 1, out.split(" - ")[1]))

            pixel = self.unhash_pixel(seacolor)
            definitions.write("%d;%s;%s;%s;%s;x;\n" % (
                x + 1, pixel[0], pixel[1], pixel[2],
                self.sea_prov_names[ind]))


            s += 1
            x += 1

        r = 0
        for rivercolor in self.river_prov_list:
            ind = self.river_prov_list.index(rivercolor)
            out = "%d - " % (x + 1)
            out += self.river_prov_names[ind]

            local_file.write(' PROV{0}:0 "{1}"\n'.format(x + 1, out.split(" - ")[1]))
            pixel = self.unhash_pixel(rivercolor)
            definitions.write("%d;%s;%s;%s;%s;x;\n" % (
                x + 1, pixel[0], pixel[1],pixel[2],
                self.river_prov_names[self.river_prov_list.index(rivercolor)]))



            # print(s)
            s += 1
            x += 1
            r += 1
        print("Finished Writing Province Files --- %s seconds ---" % (time.time() - start_time))

    def write_landed_titles_ck3(self):
        geo_regions_file = open(self.map_dir_ck3 + "geographical_region.txt", "w")
        landed_title_file = open(self.common_dir_ck3 + "00_landed_titles.txt", "w")
        localisation_file = open(self.localisation_dir_ck3 + "CKU_generated_titles_l_english.yml", "w", encoding="utf-8")
        localisation_file.write('\ufeff')
        localisation_file.write("l_english:\n")
        landed_title_file.write("@correct_culture_primary_score = 100\n@better_than_the_alternatives_score = 50\n@always_primary_score = 1000\n\n#Empires\n\n\n")

        ar = 0
        co = 0

        sre = 0

        while sre < len(self.superregion_region_assign):
            if self.superregion_region_assign[sre]:
                sreg_pix = self.unhash_pixel(self.superregions_list[sre])
                if self.gen_empires:
                    empire_capital = self.prov_names[self.area_prov_assign[self.region_area_assign[self.superregion_region_assign[sre][0]][0]][0]-1]
                    landed_title_file.write(f"e_{self.superregion_names[sre]} = {{\n"
                                            f"\tcolor = {{ {sreg_pix[0]} {sreg_pix[1]} {sreg_pix[2]} }}\n\tcolor2 = {{ 255 255 255 }}\n\t"
                                            f"capital = c_{empire_capital}\n\n"
                                            f"\tcan_create = {{\n\t\t\tNOT = {{\n\t\t\tfaith = {{\n\t\t\t\t"
                                            f"religion_tag = christianity_religion\n\t\t\t\t"
                                            f"has_doctrine = doctrine_spiritual_head\n\t\t\t}}\n\t\t}}\n\t}}"
                                            f"\n\n\tai_primary_priority = {{\n\t\tif = {{\n\t\t\tlimit = {{\n\t\t\t\t"
                                            f"culture_group = culture_group:central_germanic_group\n\t\t\t}}\n\t\t\t"
                                            f"add = @correct_culture_primary_score\n\t\t}}\n\t}}")



                # landed_title_file.write("regions = {\n\t\t")
                re = 0
                localisation_file.write(f' e_{self.superregion_names[sre-1]}:0 "{self.superregion_loc_names[sre-1]}"\n')
                for region in (self.superregion_region_assign[sre]):
                    reg_pix = self.unhash_pixel(self.regions_list[region])
                    if self.gen_kingdoms:
                        kingdom_capital = self.prov_names[self.area_prov_assign[self.region_area_assign[self.superregion_region_assign[sre][self.superregion_region_assign[sre].index(region)]][0]][0]-1]
                        landed_title_file.write(f"\n\n\tk_{self.region_names[region]} = {{\n\t\tcolor = {{ {reg_pix[0]} {reg_pix[1]} {reg_pix[2]} }}\n"
                                                f"\n\t\tcapital = c_{kingdom_capital}\n" # COULD BE PROBLEMATIC
                                                f"\n\t\tcan_create = {{\n\t\t\tNOT = {{\n\t\t\t\tfaith = {{\n\t\t\t\t\t"
                                                f"religion_tag = christianity_religion\n\t\t\t\t\t"
                                                f"has_doctrine = doctrine_spiritual_head\n\t\t\t\t}}\n\t\t\t}}\n\t\t}}"
                                                f"\n\n\t\tai_primary_priority = {{\n\t\t\tif = {{\n\t\t\t\tlimit = {{\n\t\t\t\t\t"
                                                f"culture_group = culture_group:central_germanic_group\n\t\t\t\t}}\n\t\t\t\t"
                                                f"add = @correct_culture_primary_score\n\t\t\t}}\n\t\t}}")

                    ar = 0
                    localisation_file.write(f' k_{self.region_names[region]}:0 "{self.region_loc_names[region]}"\n')
                    for area in (self.region_area_assign[region]):
                        area_pix = self.unhash_pixel(self.areas_list[area])
                        duchy_capital = self.prov_names[self.area_prov_assign[self.region_area_assign[self.superregion_region_assign[sre][self.superregion_region_assign[sre].index(region)]][ar]][0]-1]
                        landed_title_file.write(f"\n\n\t\td_{self.area_names[(area)]} = {{"
                                                f"\n\t\t\tcolor = {{ {area_pix[0]} {area_pix[1]} {area_pix[2]} }}\n\t\t\tcolor2 = {{ 255 255 255 }}"
                                                f"\n\n\t\t\tcapital = c_{duchy_capital}")
                        co = 0
                        localisation_file.write(f' d_{self.area_names[area-1]}:0 "{self.area_loc_names[area-1]}"\n')
                        for county in self.area_prov_assign[area]:
                            co_pix = self.unhash_pixel(self.prov_list[county-1])
                            county_name = self.prov_names[county-1]
                            capital_name = self.prov_capital_names[county-1]
                            county_loc_name = self.prov_loc_names[county-1]
                            capital_loc_name = self.prov_loc_capital_names[county-1]
                            landed_title_file.write(f"\n\n\t\t\tc_{county_name} = {{\n\t\t\t\t"
                                                    f"color = {{ {co_pix[0]} {co_pix[1]} {co_pix[2]} }}\n\t\t\t\tcolor2 = {{ 255 255 255 }}\n"
                                                    f"\n\t\t\t\tb_{capital_name} = {{\n\t\t\t\t\t"
                                                    f"province = {county}\n\n\t\t\t\t\t"
                                                    f"color = {{ {co_pix[0]} {co_pix[1]} {co_pix[2]} }}\n\t\t\t\t\tcolor2 = {{ 255 255 255 }}\n"
                                                    f"\n\t\t\t\t}}")
                            localisation_file.write(f' c_{county_name}:0 "{county_loc_name}"\n'
                                                    f' b_{capital_name}:0 "{capital_loc_name}"\n')


                            landed_title_file.write(f"\n\t\t\t}}")
                            co += 1


                        landed_title_file.write(f"\n\t\t}}")
                        ar += 1

                    if self.gen_kingdoms:
                        landed_title_file.write(f"\n\t}}")
                    re += 1
                if self.gen_empires:
                    landed_title_file.write(f"\n}}\n\n")
            sre += 1


    def write_characters_and_owners_ck3(self):
        self.char_written_checker = set()
        self.character_file = open(self.history_dir_ck3 + "gem_test_characters.txt", "w")
        self.title_history_file_ck3 = open(self.history_dir_ck3 + "gem_test_holdings.txt", "w")
        self.dynasty_file_ck3 = open(self.common_dir_ck3 + "gem_dynasties.txt", "w")
        for emp_idx,empire in enumerate(self.all_superregion_names_df.values):
            empire_owner_id = self.all_superregion_names_df.iloc[emp_idx]["owner_id"]
            if empire[1] in self.superregion_names:
                if not pd.isna(empire_owner_id):
                    empire_name = np.array(self.all_superregion_names_df["codename_empire"])[emp_idx]
                    empire_gov = np.array(self.all_superregion_names_df["government"])[emp_idx]
                    if pd.isna(empire_gov):
                        empire_gov = "feudal_government"
                    self.title_history_file_ck3.write(f'e_{empire_name} = {{'
                                                      f'\n\t1443.1.1 = {{'
                                                      f'\n\t\tgovernment = {empire_gov}'
                                                      f'\n\t\tholder = {empire_owner_id}'
                                                      f'\n\t}}'
                                                      f'\n}}\n')
        for king_idx,kingdom in enumerate(self.all_region_names_df.values):
            kingdom_owner_id = self.all_region_names_df.iloc[king_idx]["owner_id"]
            if kingdom[1] in self.region_names:
                if not pd.isna(kingdom_owner_id):
                    kingdom_name = np.array(self.all_region_names_df["codename_kingdom"])[king_idx]
                    kingdom_gov = np.array(self.all_region_names_df["government"])[king_idx]
                    if pd.isna(kingdom_gov):
                        kingdom_gov = "feudal_government"
                    self.title_history_file_ck3.write(f'k_{kingdom_name} = {{'
                                                      f'\n\t1443.1.1 = {{'
                                                      f'\n\t\tgovernment = {kingdom_gov}'
                                                      f'\n\t\tholder = {kingdom_owner_id}')
                    if not pd.isna(np.array(((self.characters_df.loc[self.characters_df["ID"] == kingdom_owner_id])["Liege Title"])))\
                            and kingdom_owner_id in list(self.characters_df["ID"].astype(str)): # Checking if the kingdom has an owner
                        self.title_history_file_ck3.write(
                                                          f'\n\t\tliege = {np.array(((self.characters_df.loc[self.characters_df["ID"] == kingdom_owner_id])["Liege Title"]))[0]}'
                                                          f'\n\t}}'
                                                          f'\n}}\n')
                    else:
                        self.title_history_file_ck3.write(
                                                          f'\n\t}}'
                                                          f'\n}}\n')
        for duc_idx,duchy in enumerate(self.all_area_names_df.values):
            duchy_owner_id = self.all_area_names_df.iloc[duc_idx]["owner_id"]
            if duchy[1] in self.area_names:
                if not pd.isna(duchy_owner_id):
                    duchy_name =np.array(self.all_area_names_df["codename_duchy"])[duc_idx]
                    duchy_gov = np.array(self.all_area_names_df["government"])[duc_idx]
                    if pd.isna(duchy_gov):
                        duchy_gov = "feudal_government"
                    self.title_history_file_ck3.write(f'd_{duchy_name} = {{'
                                                      f'\n\t1443.1.1 = {{'
                                                      f'\n\t\tgovernment = {duchy_gov}'
                                                      f'\n\t\tholder = {duchy_owner_id}')

                    try:
                        if not pd.isna(np.array(((self.characters_df.loc[self.characters_df["ID"] == duchy_owner_id])["Liege Title"])))\
                                and duchy_owner_id in list(self.characters_df["ID"].astype(str)):
                            self.title_history_file_ck3.write(
                                                              f'\n\t\tliege = {np.array(((self.characters_df.loc[self.characters_df["ID"] == duchy_owner_id])["Liege Title"]))[0]}'
                                                              f'\n\t}}'
                                                              f'\n}}\n')
                        else:
                            self.title_history_file_ck3.write(
                                                              f'\n\t}}'
                                                              f'\n}}\n')
                    except:
                        print(f'characters_df["ID"] == {self.characters_df["ID"]}\n'
                              f'duchy_owner_id = {duchy_owner_id}\n'
                              f'self.characters_df.loc[self.characters_df["ID"] == duchy_owner_id] = {self.characters_df.loc[self.characters_df["ID"] == duchy_owner_id]}')
        for i1, area in enumerate(self.area_prov_assign):
            # dynasty = 5000000+i1
            # self.character_file.write(f'{i1+10000} = {{'
            #                           f'\n\tname = "Test_{i1+10000}"'
            #                           f'\n\tdynasty = {dynasty}'
            #                           f'\n\treligion = "test_faith"'
            #                           f'\n\tculture = "test_culture"'
            #                           f'\n\t980.1.1 = {{'
            #                           f'\n\t\tbirth = yes'
            #                           f'\n\t}}'
            #                           f'\n}}\n')
            # self.dynasty_file_ck3.write(f'\n{dynasty} = {{'
            #                             f'\n\tname = "TestDynasty_{dynasty}"'
            #                             f'\n\tculture = "test_culture"'
            #                             f'\n}}')
            for i2, province in enumerate(area):
                try:
                    idx = province - 1
                    if self.prov_characters_list[idx] != "0" and self.prov_characters_list[idx] not in self.char_written_checker:
                        self.char_written_checker.add(self.prov_characters_list[idx])
                        char_id = self.characters_df['ID'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_liege_title = self.characters_df['Liege Title'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        primary_title = self.characters_df['Primary Title'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        # if not pd.isna(char_liege_title):
                        #     char_liege_id = self.characters_df['ID'][np.where(self.characters_df['RGB'] == char_liege_title)[0][0]]

                        char_write = self.characters_df['write_to_file'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]

                        char_name = self.characters_df['name'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]

                        char_birthdate = self.characters_df['birth date'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_deathdate = self.characters_df['death date'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_female = self.characters_df['female'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_martial = self.characters_df['martial'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_prowess = self.characters_df['prowess'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_diplomacy = self.characters_df['diplomacy'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_intrigue = self.characters_df['intrigue'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_stewardship = self.characters_df['stewardship'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_learning = self.characters_df['learning'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_father = self.characters_df['father'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_mother = self.characters_df['mother'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_disallow_rand_traits = self.characters_df['disallow_random_traits'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_faith = self.characters_df['faith'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_culture = self.characters_df['culture'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_dynasty = self.characters_df['dynasty'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_dynasty_house = self.characters_df['dynasty_house'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_nickname = self.characters_df['give_nickname'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_sexuality = self.characters_df['sexuality'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_health = self.characters_df['health'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_fertility = self.characters_df['fertility'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait1 = self.characters_df['trait1'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait2 = self.characters_df['trait2'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait3 = self.characters_df['trait3'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait4 = self.characters_df['trait4'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait5 = self.characters_df['trait5'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait6 = self.characters_df['trait6'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait7 = self.characters_df['trait7'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait8 = self.characters_df['trait8'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait9 = self.characters_df['trait9'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait10 = self.characters_df['trait10'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait11 = self.characters_df['trait11'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait12 = self.characters_df['trait12'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait13 = self.characters_df['trait13'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait14 = self.characters_df['trait14'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait15 = self.characters_df['trait15'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait16 = self.characters_df['trait16'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait17 = self.characters_df['trait17'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait18 = self.characters_df['trait18'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait19 = self.characters_df['trait19'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait20 = self.characters_df['trait20'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait21 = self.characters_df['trait21'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait22 = self.characters_df['trait22'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait23 = self.characters_df['trait23'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait24 = self.characters_df['trait24'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait25 = self.characters_df['trait25'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait26 = self.characters_df['trait26'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait27 = self.characters_df['trait27'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait28 = self.characters_df['trait28'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait29 = self.characters_df['trait29'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]
                        char_trait30 = self.characters_df['trait30'][np.where(self.characters_df['ID'] == self.prov_characters_list[idx])[0][0]]

                        if char_write != "No" and char_write != "no" and char_write != "N" and char_write != "n":

                            self.character_file.write(f'{char_id} = {{')
                            if not pd.isna(char_name):
                                self.character_file.write(f'\n\tname = "{char_name}"')
                            if not pd.isna(char_dynasty_house):
                                self.character_file.write(f'\n\tdynasty_house = {char_dynasty_house}')
                            elif not pd.isna(char_dynasty):
                                self.character_file.write(f'\n\tdynasty = {char_dynasty}')

                            if not pd.isna(char_faith):
                                self.character_file.write(f'\n\treligion = {char_faith}')
                            if not pd.isna(char_culture):
                                self.character_file.write(f'\n\tculture = {char_culture}')
                            if not pd.isna(char_father):
                                self.character_file.write(f'\n\tfather = {char_father}')
                            if not pd.isna(char_mother):
                                self.character_file.write(f'\n\tmother = {char_mother}')
                            if not pd.isna(char_martial):
                                self.character_file.write(f'\n\tmartial = {int(char_martial)}')
                            if not pd.isna(char_diplomacy):
                                self.character_file.write(f'\n\tdiplomacy = {int(char_diplomacy)}')
                            if not pd.isna(char_intrigue):
                                self.character_file.write(f'\n\tintrigue = {int(char_intrigue)}')
                            if not pd.isna(char_stewardship):
                                self.character_file.write(f'\n\tstewardship = {int(char_stewardship)}')
                            if not pd.isna(char_learning):
                                self.character_file.write(f'\n\tlearning = {int(char_learning)}')
                            if not pd.isna(char_prowess):
                                self.character_file.write(f'\n\tprowess = {int(char_prowess)}')
                            if not pd.isna(char_female):
                                self.character_file.write(f'\n\tfemale = {char_female}')

                            if not pd.isna(char_nickname):
                                self.character_file.write(f'\n\tgive_nickname = {char_name}')
                            if not pd.isna(char_health):
                                self.character_file.write(f'\n\thealth = {char_health}')
                            if not pd.isna(char_sexuality):
                                self.character_file.write(f'\n\tsexuality = {char_sexuality}')
                            if not pd.isna(char_fertility):
                                self.character_file.write(f'\n\tfertility = {char_fertility}')
                            if not pd.isna(char_disallow_rand_traits):
                                self.character_file.write(f'\n\tdisallow_random_traits = {char_disallow_rand_traits}')

                            if not pd.isna(char_trait1):
                                self.character_file.write(f'\n\ttrait = {char_trait1}')
                            if not pd.isna(char_trait2):
                                self.character_file.write(f'\n\ttrait = {char_trait2}')
                            if not pd.isna(char_trait3):
                                self.character_file.write(f'\n\ttrait = {char_trait3}')
                            if not pd.isna(char_trait4):
                                self.character_file.write(f'\n\ttrait = {char_trait4}')
                            if not pd.isna(char_trait5):
                                self.character_file.write(f'\n\ttrait = {char_trait5}')
                            if not pd.isna(char_trait6):
                                self.character_file.write(f'\n\ttrait = {char_trait6}')
                            if not pd.isna(char_trait7):
                                self.character_file.write(f'\n\ttrait = {char_trait7}')
                            if not pd.isna(char_trait8):
                                self.character_file.write(f'\n\ttrait = {char_trait8}')
                            if not pd.isna(char_trait9):
                                self.character_file.write(f'\n\ttrait = {char_trait9}')
                            if not pd.isna(char_trait10):
                                self.character_file.write(f'\n\ttrait = {char_trait10}')
                            if not pd.isna(char_trait11):
                                self.character_file.write(f'\n\ttrait = {char_trait11}')
                            if not pd.isna(char_trait12):
                                self.character_file.write(f'\n\ttrait = {char_trait12}')
                            if not pd.isna(char_trait13):
                                self.character_file.write(f'\n\ttrait = {char_trait13}')
                            if not pd.isna(char_trait14):
                                self.character_file.write(f'\n\ttrait = {char_trait14}')
                            if not pd.isna(char_trait15):
                                self.character_file.write(f'\n\ttrait = {char_trait15}')
                            if not pd.isna(char_trait16):
                                self.character_file.write(f'\n\ttrait = {char_trait16}')
                            if not pd.isna(char_trait17):
                                self.character_file.write(f'\n\ttrait = {char_trait17}')
                            if not pd.isna(char_trait18):
                                self.character_file.write(f'\n\ttrait = {char_trait18}')
                            if not pd.isna(char_trait19):
                                self.character_file.write(f'\n\ttrait = {char_trait19}')
                            if not pd.isna(char_trait20):
                                self.character_file.write(f'\n\ttrait = {char_trait20}')
                            if not pd.isna(char_trait21):
                                self.character_file.write(f'\n\ttrait = {char_trait21}')
                            if not pd.isna(char_trait22):
                                self.character_file.write(f'\n\ttrait = {char_trait22}')
                            if not pd.isna(char_trait23):
                                self.character_file.write(f'\n\ttrait = {char_trait23}')
                            if not pd.isna(char_trait24):
                                self.character_file.write(f'\n\ttrait = {char_trait24}')
                            if not pd.isna(char_trait25):
                                self.character_file.write(f'\n\ttrait = {char_trait25}')
                            if not pd.isna(char_trait26):
                                self.character_file.write(f'\n\ttrait = {char_trait26}')
                            if not pd.isna(char_trait27):
                                self.character_file.write(f'\n\ttrait = {char_trait27}')
                            if not pd.isna(char_trait28):
                                self.character_file.write(f'\n\ttrait = {char_trait28}')
                            if not pd.isna(char_trait29):
                                self.character_file.write(f'\n\ttrait = {char_trait29}')
                            if not pd.isna(char_trait30):
                                self.character_file.write(f'\n\ttrait = {char_trait30}')


                            self.character_file.write(f'\n\t{char_birthdate} = {{'
                                                      f'\n\t\tbirth = "{char_birthdate}"'
                                                      f'\n\t}}'
                                                      f'\n\t{char_deathdate} = {{'
                                                      f'\n\t\tdeath = "{char_deathdate}"'
                                                      f'\n\t}}'
                                                      f'\n')
                            if not pd.isna(primary_title):
                                self.character_file.write(f'\n\t1443.1.1 = {{'
                                                          f'\n\t\tset_primary_title_to = title:{primary_title}'
                                                          f'\n\t}}\n')
                            self.character_file.write(f'}}\n')
                            print(f"Character Written = {char_name}")
                    # else:
                        # print("No Character Assigned")
                except:
                    print(f"Problem Province = {province}")
                holder = self.prov_characters_list[idx]
                # if i2 == 0:
                #     self.title_history_file_ck3.write(f'd_{self.area_names[self.area_prov_assign.index(area)]} = {{'
                #                                       f'\n\t980.1.1 = {{'
                #                                       f'\n\t\tholder = {i1}'
                #                                       f'\n\t}}'
                #                                       f'\n}}\n')
                #     self.title_history_file_ck3.write(f'c_{self.prov_names[idx]} = {{'
                #                                       f'\n\t980.1.1 = {{'
                #                                       f'\n\t\tholder = {i1}'
                #                                       f'\n\t}}'
                #                                       f'\n}}\n')
                # else:
                # holder = str((i1 + 1000)**2) + str(i2)
                dynasty = holder
                self.dynasty_file_ck3.write(f'\n{dynasty} = {{'
                                            f'\n\tname = "TestDynasty_{dynasty}"'
                                            f'\n\tculture = "test_faith"'
                                            f'\n}}')
                # self.character_file.write(f'{holder} = {{'
                #                           f'\n\tname = "Test_{holder}"'
                #                           f'\n\tdynasty = {holder}'
                #                           f'\n\treligion = "test_faith"'
                #                           f'\n\tculture = "test_culture"'
                #                           f'\n\t980.1.1 = {{'
                #                           f'\n\t\tbirth = yes'
                #                           f'\n\t}}'
                #                           f'\n}}\n')
                try:
                    county_gov = self.all_prov_names_df.loc[self.all_prov_names_df["Name_barony"] == self.prov_names[idx]]["government"].values[0]
                except:
                    county_gov = "feudal_government"

                self.title_history_file_ck3.write(f'c_{self.prov_names[idx]} = {{'
                                                  f'\n\t1443.1.1 = {{'
                                                  f'\n\t\tchange_development_level = {int(self.development_list[idx])}'
                                                  f'\n\t\tgovernment = {county_gov}'
                                                  f'\n\t\tholder = {holder}')
                try:
                    if not pd.isna(np.array(((self.characters_df.loc[self.characters_df["ID"] == holder])["Liege Title"]))):
                        try:
                            self.title_history_file_ck3.write(
                                                      f'\n\t\tliege = {np.array(((self.characters_df.loc[self.characters_df["ID"] == holder])["Liege Title"]))[0]}'
                                                      f'\n\t}}'
                                                      f'\n}}\n')
                        except:
                            print(f"Could not write liege for {holder}")
                            self.title_history_file_ck3.write(
                                                      f'\n\t}}'
                                                      f'\n}}\n')
                    else:
                        self.title_history_file_ck3.write(
                                                  f'\n\t}}'
                                                  f'\n}}\n')
                except:
                    print(f'Problem with ID = {holder}\n'
                          f'{holder} Liege Title = {(self.characters_df.loc[self.characters_df["ID"] == holder])["Liege Title"]}'
                          f'self.characters_df.loc[self.characters_df["ID"] == holder] = {self.characters_df.loc[self.characters_df["ID"] == holder]}')



    def write_province_history_files_ck3(self):
        prov_history_file = open(self.history_dir_ck3 + "gem_earth.txt", "w")
        for i in range(len(self.prov_list)):
            if len(self.culture_list[i]) == 0:
                prov_history_file.write(f"{i+1} = {{\t#BLACK"
                                    f"\n\tculture = test_culture"
                                    f"\n\treligion = test_faith"
                                    f"\n\tholding = tribal_holding"
                                    f"\n}}\n")
            else:
                prov_history_file.write(f"{i+1} = {{\t#{self.prov_names[i]}"
                                    f"\n\tculture = {self.culture_list[i]}"
                                    f"\n\treligion = {self.religion_list[i]}"
                                    f"\n\tholding = tribal_holding"
                                    f"\n}}\n")

    def write_area_file(self):
        """
        Creates areas.txt
        :param map_dir:
        :param area_prov_assign:
        :param area_names:
        :return:
        """
        area_file = open(self.map_dir + "areas.txt", "w")
        area_file.write("# Administrative areas.\n\n")
        ar = 0
        while ar < len(self.area_prov_assign):
            if len(self.area_prov_assign[ar]) != 0:
                area_file.write("{0} = {{ #{1}\n\tprovinces = {{ ".format(self.area_names[ar], len(self.area_prov_assign[ar])))
                ar2 = 0
                while ar2 < len(self.area_prov_assign[ar]):
                    area_file.write("%d " % self.area_prov_assign[ar][ar2])
                    ar2 += 1

                area_file.write("}\n}\n\n")
            ar += 1
        print("Finished Writing Area File --- %s seconds ---" % (time.time() - start_time))

    def write_region_file(self):
        """
        Creates regions.txt
        :param map_dir:
        :param region_area_assign:
        :param area_names:
        :return:
        """
        region_file = open(self.map_dir + "regions.txt", "w")
        region_file.write("## Regions ##\n")
        re = 0
        while re < len(self.region_area_assign):
            if self.region_area_assign[re]:
                region_file.write("{0} = {{\t\t#{1} areas\n\t".format(self.region_names[re], len(self.region_area_assign[re])))
                region_file.write("areas = {\n\t\t")
                re2 = 0
                while re2 < len(self.region_area_assign[re]):
                    region_file.write("%s\n\t\t" % self.area_names[(self.region_area_assign[re][re2])])
                    re2 += 1
                region_file.write("\n\t}\n}\n\n")
            re += 1
        print("Finished Writing Region File --- %s seconds ---" % (time.time() - start_time))

    def write_country_files(self):
        """
        Creates countries_l_english.yml, country_setup_provinces.txt, countries.txt
        :param map_dir:
        :param country_params:
        :param country_list:
        :return:
        """
        for i in range(len(self.prov_list)):
            self.prov_list[i] = str(self.prov_list[i])
        countries_local_file = open(OUTPUT_FILES_DIR + "countries_l_english.yml", "w")
        countries_local_file.write("l_english:\n")
        countries_local_file.write(
            ' #####COUNTRIES##### REB:0 "Rebels"\n REB_ADJ:0 "Rebel"\n BAR:0 "Barbarians"\n BAR_ADJ:0 "Barbarian"\n MER:0 "Mercenaries"\n MER_ADJ:0 "Mercenary"\n\n')
        country_file = open(self.map_dir + "country_setup_provinces.txt", "w")
        country_file.write("## Countries ##\n")
        countries_local_file.write(' #####Atlantian Countries#####\n')
        country_tags_file = open(self.map_dir + "countries.txt", "w")
        country_tags_file.write("## Generic ##\n")
        country_tags_file.write(
            'REB = "countries/rebels.txt"\nPIR = "countries/pirates.txt"\nBAR = "countries/barbarians.txt"\nMER = "countries/mercenaries.txt"\n\n')

        ct = 0
        name_col = self.country_params[:][0].index('Name')
        folder_col = self.country_params[:][0].index('Folder')
        adj_col = self.country_params[:][0].index('ADJ')
        tag_col = self.country_params[:][0].index('TAG')
        rgb_col = self.country_params[:][0].index('RGB')
        gov_col = self.country_params[:][0].index('Government')
        culture_col = self.country_params[:][0].index('Primary Culture')
        religion_col = self.country_params[:][0].index('Religion')
        capital_rgb_col = self.country_params[:][0].index('Capital RGB')

        country_file.write("\ncountry = {\n\tcountries = {")
        self.prov_arr = np.array(self.prov_list).astype(int)
        self.unhash_pixel_v = np.vectorize(self.unhash_pixel)
        while ct < len(self.countries_list):
            if len(self.country_prov_assign[ct]) != 0:
                for i in range(0, len(self.country_params)):
                    rgb_cp = ''.join(self.country_params[i][rgb_col])
                    rgb_country = str(self.unhash_pixel(self.countries_list[ct]))

                    if rgb_country == rgb_cp:
                        country_file.write("\n\n\t\t{0} = {{ #{1}\n\t\t\t".format(self.country_params[i][tag_col],
                                                                                  self.country_params[i][name_col]))
                        country_file.write("\n\t\t\tgovernment = {0}".format(self.country_params[i][gov_col]))
                        country_file.write("\n\t\t\tprimary_culture = {0}".format(self.country_params[i][culture_col]))
                        country_file.write("\n\t\t\treligion = {0}".format(self.country_params[i][religion_col]))
                        hashed_capital_rgb = self.hash_pixel(tuple(map(int, self.country_params[i][capital_rgb_col].strip("(").strip(")").split(","))))
                        capital_prov_num = np.where(self.prov_arr == hashed_capital_rgb)[0][0] + 1
                        if capital_prov_num in self.country_prov_assign[ct]:
                            country_file.write("\n\t\t\tcapital = {0}".format(capital_prov_num))
                        else:
                            country_file.write("\n\t\t\tcapital = {0}".format(self.country_prov_assign[ct][0]))
                        country_file.write("\n\t\t\town_control_core = {\n\t\t\t\t")

                        ct2 = 0
                        country_tags_file.write(
                            '{0} = "countries/'.format(self.country_params[i][tag_col]) + self.country_params[i][
                                folder_col] + '/{0}.txt"\n'.format(self.country_params[i][name_col]))

                        countries_local_file.write(' {0}:1 "{1}"\n'' {2}_ADJ:0 "{3}"\n'.format(
                            self.country_params[i][tag_col], self.country_params[i][name_col], self.country_params[i][tag_col],
                            self.country_params[i][adj_col]))
                        while ct2 < len(self.country_prov_assign[ct]):
                            country_file.write("%d " % self.country_prov_assign[ct][ct2])
                            ct2 += 1
                        country_file.write(" #%d\n\t\t\t}\n\t\t}" % len(self.country_prov_assign[ct]))
            ct += 1
        country_file.write("\n\t}\n}")
        print("Finished Writing Country File --- %s seconds ---" % (time.time() - start_time))

    def hash_pixel(self, unhashed_pixel):
        return unhashed_pixel[0]*256*256 + unhashed_pixel[1]*256 + unhashed_pixel[2]

    def unhash_pixel(self, hashed_pixel):
        r = (hashed_pixel >> 16) & 0xFF
        g = (hashed_pixel >> 8) & 0xFF
        b = hashed_pixel & 0xFF
        return tuple((r, g, b))

    def remove_waste_sea(self, aset):
        if self.sea_level_pixel in aset:
            aset.remove(self.sea_level_pixel)
        if self.impassable_pixel in aset:
            aset.remove(self.impassable_pixel)

    def write_terrain_file(self):
        self.terrain_dir = self.directory_setup(os.getcwd() + "\\Output_Files\\CK3\\common\\province_terrain\\")
        terrain_file = open(self.terrain_dir + "gem_province_terrain.txt", "w")
        terrain_file.write("default=plains\n")
        for idx, prov_terrain in enumerate(self.terrain_list):
            terrain_file.write(f"{idx+1}={prov_terrain}\n")
        x=0




def main():
    world = Map()

if __name__ == "__main__":
    main()
    # pr = cProfile.Profile()
    # pr.enable()
    # # cProfile.run('main()')
    # main()
    # pr.disable()
    # s = io.StringIO()
    # sortby = 'tottime'
    # ps = pstats.Stats(pr, stream=s).sort_stats(sortby)
    # ps.print_stats()
    # print(s.getvalue())