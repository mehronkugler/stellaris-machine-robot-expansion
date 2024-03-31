import argparse
from datetime import datetime
import os
from typing import List
import time
import sys
from json import load as json_load

from generate_trait_tooltips import create_tooltip_for_leader
from mre_common_vars import (
    BUILD_FOLDER,
    INPUT_FILES_FOR_CODEGEN,
    LEADER_MAKING,
    CORE_MODIFYING,
    LEADER_SUBCLASSES,
    LEADER_CLASSES,
    OUTPUT_FILES_DESTINATIONS,
    LOCALISATION_HEADER,
    LEADER_SUBCLASSES_NAMES,
    EXCLUDE_SUBCLASSES_FROM_CORE_MODIFYING,
    MACHINE_LOCALISATIONS_MAPFILE,
    EXCLUDE_TRAITS_FROM_CORE_MODIFYING,
    TRAITS_REQUIRING_DLC,
    AUTOGENERATED_HEADER,
    RARITIES,
    FILE_NUM_PREFIXES,
)


"""
   _____  _____ _____  _____ _____ _______ ______ _____      ________   __
  / ____|/ ____|  __ \|_   _|  __ \__   __|  ____|  __ \    |  ____\ \ / /
 | (___ | |    | |__) | | | | |__) | | |  | |__  | |  | |   | |__   \ V / 
  \___ \| |    |  _  /  | | |  ___/  | |  |  __| | |  | |   |  __|   > <  
  ____) | |____| | \ \ _| |_| |      | |  | |____| |__| |   | |     / . \ 
 |_____/ \_____|_|  \_\_____|_|      |_|  |______|_____/    |_|    /_/ \_\
                                                                          
"""

def gen_core_modifying_deduct_trait_pts_for_each_trait() -> List[str]:
    """ scripted effect to deduct points and picks from the ruler
    for each trait that already exists on the ruler """
    unsorted_traits = {
        "common": [],
        "veteran": [],
        "paragon": []
    }
    scripted_trigger_header = """
# Check what traits are already on the ruler, and deduct from total available trait picks + points
oxr_mdlc_core_modifying_check_existing_traits_on_gui_open_effect = {
    optimize_memory
"""
    scripted_trigger_footer = """
}
"""
    trait_limit_trigger = """	if = {{
		limit = {{
			ruler = {{ has_trait = {trait_name} }}
			check_variable = {{ which = xvcv_mdlc_core_modifying_max_traits_number value > 0 }}
		}}
		oxr_mdlc_core_modifying_deduct_trait_pick = yes
		oxr_mdlc_core_modifying_deduct_trait_points_{rarity} = yes
	}}"""
    trait_limit_lines = []
    for processed_traits_file in INPUT_FILES_FOR_CODEGEN:
        with open(
            os.path.join(BUILD_FOLDER, processed_traits_file)
        ) as organized_traits_dict_data:
            organized_traits_dict = json_load(organized_traits_dict_data)
            for rarity in RARITIES:
                for leader_trait in organized_traits_dict["core_modifying_traits"][rarity]:
                    trait_name = [*leader_trait][0]
                    unsorted_traits[rarity].append(trait_name)
    # Sort them all
    for rarity in RARITIES:
        for trait_name in sorted(set(unsorted_traits[rarity])):
            # if "subclass" not in trait_name:
            trait_limit_lines.append(
                trait_limit_trigger.format(
                    trait_name=trait_name, rarity=rarity
                )
            )
    return f"""{scripted_trigger_header}
{"\n".join(trait_limit_lines)}
{scripted_trigger_footer}"""

if __name__ == "__main__":
    print("0xRetro Magic COde creat0r")
    print("Making oxr_mdlc_core_modifying_check_existing_traits_on_gui_open_effect ...")
    scripted_trigger = gen_core_modifying_deduct_trait_pts_for_each_trait()
    with open(
        os.path.join(
            BUILD_FOLDER,
            f"{FILE_NUM_PREFIXES["effects"]}_oxr_mdlc_core_modifying_check_existing_traits_on_gui_open_effect.txt"
        ), 'wb'
    ) as outfile:
        outfile.write(scripted_trigger.encode('utf-8'))
        print(f"Done. Check {outfile.name}")