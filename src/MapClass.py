import os
import time
import multiprocessing
import numpy as np
import sys

import random
import time
import numpy as np
import xlrd
from PIL import Image
import pandas as pd
from collections import Counter

import numpy.lib.recfunctions as nlr


start_time = time.time()

# INPUT_FILES_DIR = os.getcwd() + "\\Input_Files\\mu\\"
# INPUT_FILES_DIR = os.getcwd() + "\\Input_Files\\small\\"
INPUT_FILES_DIR = os.getcwd() + "\\Input_Files\\"
OUTPUT_FILES_DIR = os.getcwd() + "\\Output_Files\\"

PIXEL_CHECKER = 1

class Province():
    def __init__(self, rgb):
        self.rgb = rgb
        self.area = []
        self.region = []
        self.country = []
        self.culture = []
        self.religion = []
        self.terrain = []
        self.trade_good = []
        self.province_modifier = []
        self.num_citizens, self.num_freemen, self.num_slaves, self.num_tribesmen =[], [], [], []

    def add_all_pixels(self, prov_pix, area_pix, region_pix, country_pix, cul_pix, rel_pix, ter_pix, trade_goods_pix, prov_mod_mix, civ_pop_pix, tribe_pop_pix):
        self.add_area_pix(area_pix)
        self.add_region_pix(region_pix)
        self.add_country_pix(country_pix)
        self.add_culture_pix(cul_pix)
        self.add_religion_pix(rel_pix)
        self.add_terrain_pix(ter_pix)
        self.add_trade_good_pix(trade_goods_pix)
        self.add_province_modifier_pix(prov_mod_mix)
        self.add_pop_pix(civ_pop_pix, tribe_pop_pix)

    def add_area_pix(self, area_pix):
        self.area.append(area_pix)
        
    def add_region_pix(self, region_pix):
        self.region.append(region_pix)
    
    def add_country_pix(self, country_pix):
        self.country.append(country_pix)

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

    def get_dominant_pixels(self):
        self.dom_area = Counter(self.area).most_common(1)





class Map():
    def __init__(self):
        self.get_province_modifiers((88, 11, 17))
        self.get_country_params()  # Loads country parameters from an excel file and stores them in a list of lists
        self.initial_file_setup()
        self.load_images()  # Loading in all images used to create game files
        self.width = len(self.land_province_array)  # Width dimension of the map
        self.height = len(self.land_province_array[0])  # Height dimension of the map
        self.create_sets()  # Creates sets of all province arrays
        self.create_lists()  # Converts the appropriate sets to lists
        self.assign_provinces()  # Main loops that creates hierarchical relationships and province histories

        self.generate_random_names()  # Generates random names for provinces, areas, and regions
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
            os.mkdir(path)
        except OSError:
            print("Creation of the directory %s failed" % path)
            return path
        else:
            print("Successfully created the directory %s " % path)
            return path

    def initial_file_setup(self):
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

    def load_images(self):
        """
        Loads all images
        :return:
        """
        self.culture_array = self.image_to_array_no_hash("culture.png")
        self.religion_array = self.image_to_array_no_hash("religion.png")
        self.terrain_array = self.image_to_array_no_hash("terrain.png")
        self.trade_good_array = self.image_to_array_no_hash("trade_goods.png")
        self.province_modifier_array = self.image_to_array_no_hash("province_modifiers.png")

        self.civilized_population_array = self.image_to_array_no_hash("civilized_population.png")
        self.tribabl_population_array = self.image_to_array_no_hash("tribal_population.png")

        self.land_province_array = self.image_to_array("land_provinces.png")
        self.area_array = self.image_to_array("land_areas.png")
        self.region_array = self.image_to_array("land_regions.png")
        self.country_array = self.image_to_array("countries.png")
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
        self.areas_set = set(self.area_array.flatten())
        self.regions_set = set(self.region_array.flatten())
        self.countries_set = set(self.country_array.flatten())
        self.sea_provs_set = set(self.sea_province_array.flatten())
        self.river_prov_set = set(self.river_province_array.flatten())

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
        self.areas_list = list(self.areas_set)
        self.regions_list = list(self.regions_set)
        self.sea_prov_list = list(self.sea_provs_set)
        self.river_prov_list = list(self.river_prov_set)
        self.countries_list = list(self.countries_set)

        self.culture_list = [""] * len(self.land_provs_set)
        self.religion_list = [""] * len(self.land_provs_set)
        self.terrain_list = [""] * len(self.land_provs_set)
        self.trade_good_list = [""] * len(self.land_provs_set)
        self.province_modifier_list = [""] * len(self.land_provs_set)
        self.province_population_list = [(100,100,100,101)] * len(self.land_provs_set)

        ######################## Initializes lists of lists for storing hierarchical assignments #######################
        self.prov_obj = [None]*len(self.prov_list)

        self.area_prov_assign = [[] for x in range(0, len(self.areas_list))]
        self.region_area_assign = [set() for x in range(0, len(self.regions_list))]
        self.country_prov_assign = [[] for x in range(0, len(self.countries_list))]
        ################################################################################################################
        print("All lists created --- %s seconds ---" % (time.time() - start_time))

    def assign_provinces(self):
        """
        The main loop where the magic happens
        :return:
        """
        print("Starting Assignments --- %s seconds ---" % (time.time() - start_time))
        for x in range(int(self.width)):
            if x % 100 == 0:
                print(f"idx = {x} --- {time.time() - start_time} seconds ---")

            land_prov_array_x = self.land_province_array[x]
            areas_array_x = self.area_array[x]
            regions_array_x = self.region_array[x]
            countries_array_x = self.country_array[x]

            culture_array_x = self.culture_array[x]
            religion_array_x = self.religion_array[x]
            terrain_array_x = self.terrain_array[x]
            trade_good_array_x = self.trade_good_array[x]
            province_modifier_array_x = self.province_modifier_array[x]
            civilized_population_array_x = self.civilized_population_array[x]
            tribal_population_array_x = self.tribabl_population_array[x]


            for y in range(self.height):
                prov_pixel = land_prov_array_x[y]
                area_pixel = areas_array_x[y]
                region_pixel = regions_array_x[y]
                country_pixel = countries_array_x[y]

                culture_pixel = culture_array_x[y]
                religion_pixel = religion_array_x[y]
                terrain_pixel = terrain_array_x[y]
                trade_good_pixel = trade_good_array_x[y]
                province_modifier_pixel = province_modifier_array_x[y]
                civilized_population_pixel = civilized_population_array_x[y]
                tribal_population_pixel = tribal_population_array_x[y]
                if prov_pixel in self.used_provs:
                    self.create_prov_history(prov_pixel)
                    self.used_provs.remove(prov_pixel)
                elif x*y % PIXEL_CHECKER**2 == 0:
                    self.expand_prov_history(prov_pixel, area_pixel, region_pixel, country_pixel, culture_pixel, religion_pixel, terrain_pixel, trade_good_pixel, province_modifier_pixel, civilized_population_pixel, tribal_population_pixel)

        print(f"Length of self.used_provs = {len(self.used_provs)}")
        print("Consolidating Provinces --- %s seconds ---" % (time.time() - start_time))
        self.consolidate_prov_history()
        print("Assignments Completed --- %s seconds ---" % (time.time() - start_time))

    def expand_prov_history(self, prov_pixel, area_pixel, region_pixel, country_pixel, culture_pixel, religion_pixel, terrain_pixel, trade_good_pixel, province_modifier_pixel, civilized_population_pixel, tribal_population_pixel):
        idx = self.prov_list.index(prov_pixel)
        self.prov_obj[idx].add_all_pixels(prov_pixel, area_pixel, region_pixel, country_pixel,
                                          self.hash_pixel(culture_pixel), self.hash_pixel(religion_pixel),
                                          self.hash_pixel(terrain_pixel), self.hash_pixel(trade_good_pixel),
                                          self.hash_pixel(province_modifier_pixel), civilized_population_pixel, tribal_population_pixel)


    def create_prov_history(self, prov_pixel):

        idx = self.prov_list.index(prov_pixel)
        self.prov_obj[idx] = Province(prov_pixel)



    def consolidate_prov_history(self):
        for province in self.prov_obj:
            idx = self.prov_obj.index(province)
            if idx % 100 == 0:
                print(f"idx = {idx} --- {time.time() - start_time} seconds ---")
            try:
                area_pix = Counter(province.area).most_common()[0][0]
                region_pix = Counter(province.region).most_common()[0][0]
                country_pix = Counter(province.country).most_common()[0][0]
                culture_pix = Counter(province.culture).most_common()[0][0]
                religion_pix = Counter(province.religion).most_common()[0][0]
                terrain_pix = Counter(province.terrain).most_common()[0][0]
                trade_good_pix = Counter(province.trade_good).most_common()[0][0]
                province_modifier_pix = Counter(province.province_modifier).most_common()[0][0]
                num_citizens_pix = Counter(province.num_citizens).most_common()[0][0]
                num_freemen_pix = Counter(province.num_freemen).most_common()[0][0]
                num_slaves_pix = Counter(province.num_slaves).most_common()[0][0]
                num_tribesmen_pix = Counter(province.num_tribesmen).most_common()[0][0]
            except:
                print(f"Problem RGB = {self.unhash_pixel(province.rgb)}")



            self.area_prov_assign[self.areas_list.index(area_pix)].append(idx + 1)

            self.country_prov_assign[self.countries_list.index(country_pix)].append(idx + 1)
            # if area_pix not in self.regions_list.index(region_pix):
            self.region_area_assign[self.regions_list.index(region_pix)].add(self.areas_list.index(area_pix))


            culture = self.get_culture(culture_pix)
            religion = self.get_religion(religion_pix)
            terrain = self.get_terrain(terrain_pix)
            trade_good = self.get_trade_good(trade_good_pix)
            province_modifier = self.get_province_modifiers(province_modifier_pix)
            num_citizens, num_freemen, num_slaves, num_tribesmen = self.get_population((num_citizens_pix, num_freemen_pix, num_slaves_pix), num_tribesmen_pix)

            self.culture_list[idx] = culture
            self.religion_list[idx] = religion
            self.terrain_list[idx] = terrain
            self.trade_good_list[idx] = trade_good
            self.province_modifier_list[idx] = province_modifier
            self.province_population_list[idx] = (num_citizens, num_freemen, num_slaves, num_tribesmen)
        for i in range(len(self.region_area_assign)):
            self.region_area_assign[i] = list(self.region_area_assign[i])
        x = 0

    def get_culture(self, culture_pixel):
        """
        Returns the culture of the province
        :return:
        """
        cultures_file_location = (INPUT_FILES_DIR + "cultures.xlsx")
        c = pd.read_excel(cultures_file_location)

        try:
            cul = c['Culture'][np.where(c['RGB'] == str((culture_pixel[0], culture_pixel[1], culture_pixel[2])))[0][0]]
        except:
            cul = "barbarian"
        return cul

    def get_religion(self, religion_pixel):
        """
        Returns the religion of the province
        :return:
        """
        religions_file_location = (INPUT_FILES_DIR + "religions.xlsx")
        r = pd.read_excel(religions_file_location)
        try:
            rel = r['Religion'][np.where(r['RGB'] == str((religion_pixel[0], religion_pixel[1], religion_pixel[2])))[0][0]]
        except:
            rel = "pagan"
        return rel

    def get_terrain(self, terrain_pixel):
        """
        Returns the terrain of the province
        :return:
        """
        terrains_file_location = (INPUT_FILES_DIR + "terrains.xlsx")
        t = pd.read_excel(terrains_file_location)
        try:
            ter = t['Terrain'][np.where(t['RGB'] == str((terrain_pixel[0], terrain_pixel[1], terrain_pixel[2])))[0][0]]
        except:
            ter = "plains"
        return ter

    def get_trade_good(self, trade_good_pixel):
        """
        Returns the trade good of the province
        :return:
        """
        trade_goods_file_location = (INPUT_FILES_DIR + "trade_goods.xlsx")
        t = pd.read_excel(trade_goods_file_location)
        try:
            tg = t['Trade Good'][np.where(t['RGB'] == str((trade_good_pixel[0], trade_good_pixel[1], trade_good_pixel[2])))[0][0]]
        except:
            tg = "fur"
        return tg

    def get_province_modifiers(self, pm_pixel):
        """
        Returns the province modifier of the province
        :return:
        """
        province_modifiers_file_location = (INPUT_FILES_DIR + "province_modifiers.xlsx")
        p = pd.read_excel(province_modifiers_file_location)
        try:
            pm = p['Province Modifier'][np.where(p['RGB'] == str((pm_pixel[0], pm_pixel[1], pm_pixel[2])))[0][0]]
        except:
            pm = None
        return pm

    def get_population(self, civ_pop_pixel, tribal_pop_pixel):
        num_citizens = (civ_pop_pixel[0]-100)
        num_freemen = (civ_pop_pixel[1]-100)
        num_slaves = (civ_pop_pixel[2] - 100)
        num_tribesmen = (tribal_pop_pixel - 100)
        return num_citizens, num_freemen, num_slaves, num_tribesmen

    def write_files(self):
        self.write_province_files()
        self.write_area_file()
        self.write_region_file()
        self.write_country_files()

    def get_country_params(self):
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
        self.area_names, self.area_adj = self.random_name_generator(len(self.area_prov_assign))
        self.region_names, self.region_adj = self.random_name_generator(len(self.region_area_assign))
        self.sea_prov_names, self.sea_adj = self.random_name_generator(len(self.sea_prov_list), sea=True)
        self.river_prov_names, self.river_prov_adj = self.random_name_generator((len(self.river_prov_list)), river=True)
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

    def write_province_files(self):
        """
        Creates definitions.csv, provincenames_l_english.yml, and prov_names_adj_l_english.yml
        :return:
        """
        # prov_list[x].province_id.index(prov_list[x].rgb)
        # prov_list = prov_list[0].province_id
        # sea_prov_list = sea_prov_list[0].sea_province_id
        # river_prov_list = river_prov_list[0].river_province_id

        local_file = open(self.localisation_dir + "provincenames_l_english.yml", "w")
        local_file.write("l_english:\n")  # First line in any English localisation file
        local_file_adj = open(self.localisation_dir + "prov_names_adj_l_english.yml", "w")
        local_file_adj.write("l_english:\n")

        definitions = open(self.map_dir + "definition.csv", "w")
        definitions.write(
            "#Province id 0 is ignored\n0;0;0;0;;x;;;;;;;;;;;;;;;;;\n")  # First line in any definitions file
        prov_setup = open(self.setup_dir + "ge_provinces.txt", "w")
        x = 0
        for x in range(len(self.prov_list)):
            color = self.prov_list[x]
            ind = self.prov_list.index(color)

            out = "%d - " % (x + 1)
            out += self.prov_names[self.prov_list.index(color)]
            out2 = self.prov_adj[self.prov_list.index(color)]

            local_file.write(' PROV{0}:0 "{1}"\n'.format(x + 1, out.split(" - ")[1]))
            local_file_adj.write(' PROV{0}:0 "{1}"\n'.format(x + 1, out2))

            pixel = self.unhash_pixel(color)

            definitions.write("%d;%s;%s;%s;%s;x;;;;;;;;;;;;;;;;;;;\n" % (
                x + 1, pixel[0], pixel[1], pixel[2], self.prov_names[self.prov_list.index(color)]))

            prov_setup.write(f"""
    {x+1}={{ #{self.prov_names[ind]}
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
        while ct < len(self.countries_list):
            if len(self.country_prov_assign[ct]) != 0:
                for i in range(0, len(self.country_params)):
                    rgb_cp = ''.join(self.country_params[i][rgb_col])
                    rgb_country = str(self.countries_list[ct])

                    if rgb_country == rgb_cp:
                        country_file.write("\n\n\t\t{0} = {{ #{1}\n\t\t\t".format(self.country_params[i][tag_col],
                                                                                  self.country_params[i][name_col]))
                        country_file.write("\n\t\t\tgovernment = {0}".format(self.country_params[i][gov_col]))
                        country_file.write("\n\t\t\tprimary_culture = {0}".format(self.country_params[i][culture_col]))
                        country_file.write("\n\t\t\treligion = {0}".format(self.country_params[i][religion_col]))
                        country_file.write(
                            "\n\t\t\tcapital = {0}".format(self.prov_list.index(self.country_params[i][capital_rgb_col])))
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






def main():
    world = Map()

if __name__ == "__main__":
    main()