"""
Once the base trait files have been crunched,
we have 3 files with the three classes' traits,
nicely organized and sorted alphabetically.

Traits will need to be filtered for whether they'll work 
in the leader-making feature, and the core-modifying feature.
Not all traits can be used by both features,
so in this script we further filter and sort traits
for those two features.

We also need some functionality to pick the highest rank of a 
given trait, and give that to players, to avoid overwhelming the
UI with dozens of traits.
Thankfully, in pre-processing, traits are sorted alphabetically and
it'll be easy to get the highest rank of that trait series.
"""
from copy import copy
import logging
import os
import sys
import time
from json import load as json_load, dump as json_dump
import argparse

from mre_common_vars import (
    BUILD_FOLDER,
    LEADER_CLASSES,
    MISSING,
    PIPELINE_OUTPUT_FILES,
    PLACEHOLDER,
    SKIP_TRAIT_FOR_SUBCLASS_LIST,
    TRAIT_MODIFIER_KEYS,
    TRAITS_TO_EXCLUDE,
    EXCLUDE_TRAITS_FROM_CORE_MODIFYING,
    EXCLUDE_TRAITS_FROM_COUNCILOR_EDITOR,
    EXCLUDE_TRAITS_FROM_PARAGON_DLC,
)

MODIFIER_VALUES_SUBSTITUTIONS = {
    "var_trait_surveyor_amt": 0.5,
    "var_trait_surveyor_sector_amt": 0.25
}

""" Apply these changes to the traits after we have crunched them. Some of these traits 
have duplicate keys in base stellaris and we lose the correct tooltip information.
Others should be locked by certain DLCs"""
TRAIT_PATCHES = {
    "leader_trait_emotional_support_pet": {
        "has_paragon_dlc": True
    },
    "leader_trait_enlister_2": {
        "triggered_sector_modifier": {
            "job_soldier_add": 1
        },
        "triggered_planet_modifier": {
            "job_soldier_add": 1
        }
    },
    "leader_trait_scrapper": {
        "triggered_planet_modifier": {
            "job_alloy_drone_add": 1
        }
    },
}

logger = logging.getLogger(__name__)

def trait_qualifies_for_leader_making(trait_dict: dict) -> bool:
    is_leader_making_trait = False
    if not any(
        [
            trait_dict.get('councilor_modifier'),
            trait_dict.get('triggered_councilor_modifier'),
            "ruler" in trait_dict['trait_name'],
            # trait_dict.get('is_councilor_trait'),
        ]
    ):
        is_leader_making_trait = True
    return is_leader_making_trait

def trait_qualifies_for_core_modifying(trait_dict: dict) -> bool:
    is_core_modifying_trait = False
    # Ruler is a type of councilor, so these modifiers will work
    if any(
        [
            "ruler" in trait_dict['trait_name'],
            trait_dict.get('self_modifier'),
            trait_dict.get('triggered_self_modifier'),
            trait_dict.get('councilor_modifier'),
            trait_dict.get('triggered_councilor_modifier'),
            trait_dict.get('allow_for_ruler'),
            trait_dict.get('is_councilor_trait'),
        ]
    ):
        is_core_modifying_trait = True
    # breakpoint()
    return is_core_modifying_trait

def trait_qualifies_for_councilor_editor(trait_dict: dict) -> bool:
    is_councilor_trait = False
    # Ruler is a type of councilor, so these modifiers will work
    # ruler should not be in trait name
    if all([
        not trait_dict.get('allow_for_ruler'),
    ]) and any(
        [
            "ruler" in trait_dict['trait_name'],
            # trait_dict.get('self_modifier'),  # cant use traits that boost self stuff
            # trait_dict.get('triggered_self_modifier'),  # no self traits
            trait_dict.get('councilor_modifier'),
            trait_dict.get('triggered_councilor_modifier'),
            trait_dict.get('is_councilor_trait'),
        ]
    ):
        is_councilor_trait = True
    # breakpoint()
    return is_councilor_trait


def pick_highest_tier_of_trait(list_of_traits):
    # Drop traits that have a higher tier of trait
    # Thankfully all our data is alphabetically sorted so "this will be simple" (Famous Last Words)
    tier_tracker = {}
    list_of_traits_copy = copy(list_of_traits)
    position_in_list = 0
    for trait in list_of_traits:
        trait_level = 1
        current_trait_name = [*trait][0]
        if current_trait_name[-1].isdigit():
            current_trait_name_series, trait_level = current_trait_name.rsplit('_', 1)
            trait_level = int(trait_level)
        else:
            current_trait_name_series = current_trait_name
        # logger.info(f"Evaluating {current_trait_name} in series {current_trait_name_series}")
        # Is the next trait in the same series? If so, pop it off the copy
        # If there is no next trait (end of list) we have evaluated the highest in the series
        if position_in_list+1 == len(list_of_traits):
            # Nothing to do
            continue
        else:
            next_trait = list_of_traits[position_in_list+1]
            next_trait_name = [*next_trait][0]
            # If the next trait in the list doesn't have a number at the end, it's a new series
            # And this trait we were looking at is the highest in its series
            # print(f"Comparing it to {next_trait_name}")
            if current_trait_name_series == get_trait_series_name(next_trait_name):
                # print(f"Next trait is in the same series, so drop current trait")
                list_of_traits_copy.remove(trait)
        position_in_list = position_in_list + 1
    return list_of_traits_copy

def get_trait_series_name(trait_name: str) -> str:
    name_series = trait_name
    if trait_name[-1].isdigit():
        name_series = trait_name.rsplit('_',1)[0]
    return name_series


def filter_traits_by_mod_feature(traits_list: list) -> dict:
    """ Organize traits by whether it should go to the leader-making feature or core-modifying
    Also take the opportunity to drop traits if they are in our exclusion list """

    leader_making_traits = []
    core_modifying_traits = []
    councilor_editor_traits = []
    outliers = []
    for trait in traits_list:
        trait_name = [*trait][0]
        if TRAITS_TO_EXCLUDE.get(trait_name):
            sys.stdout.write(f"Skipped {trait_name} because it is on our exclusion list..\n")
            continue
        root = trait[trait_name]
        if trait_qualifies_for_core_modifying(root):
            if EXCLUDE_TRAITS_FROM_CORE_MODIFYING.get(trait_name):
                print(f"Skipped adding {trait_name} to the core-modifying traits because the game wont let us add it. :(")
            else:
                core_modifying_traits.append(trait)
        if trait_qualifies_for_leader_making(root):
            leader_making_traits.append(trait)
        if trait_qualifies_for_councilor_editor(root):
            if {**EXCLUDE_TRAITS_FROM_COUNCILOR_EDITOR, **EXCLUDE_TRAITS_FROM_PARAGON_DLC}.get(trait_name):
                print(f"Skipped adding {trait_name} to the councilor editor traits because the game wont let us add it to councilors. :(")
            else:
                councilor_editor_traits.append(trait)
        if all([
            not trait_qualifies_for_core_modifying,
            not trait_qualifies_for_leader_making,
            not trait_qualifies_for_councilor_editor,
        ]):
            # No idea how this could happen.. but
            outliers.append(trait)
    return {
        "leader_making_traits": leader_making_traits,
        "core_modifying_traits": core_modifying_traits,
        "councilor_editor_traits": councilor_editor_traits,
        "outliers": outliers
    }

def filter_traits_by_rarity(traits_list):
    """ Sort by rarity after having sorted for highest tier
        Once they are sorted this way, we can start to create game code from them
    """
    rarities = (
        "common", "free_or_veteran", "veteran", "paragon"
    )
    traits_by_rarity = {
        "common": [],
        "veteran": [],
        "paragon": []
    }
    for trait in traits_list:
        trait_name = [*trait][0]
        root = trait[trait_name]
        rarity = root.get('rarity', "MISSING_RARITY")
        if rarity == "common":
            traits_by_rarity['common'].append(trait)
        elif rarity == "veteran" or rarity == "free_or_veteran":
            traits_by_rarity['veteran'].append(trait)
        elif rarity == "paragon":
            traits_by_rarity["paragon"].append(trait)
        else:
            sys.exit(
                f"This trait has no rarity assigned: {trait}. That's an error."
            )
    return traits_by_rarity

def do_qa_on_pipeline_files(traits_list):
    """ Quick QA check to find potential missing data """
    rogue_trait_names = []
    sys.stdout.write("** Checking for any issues with trait data ... **\n")
    for trait in traits_list:
        issues = []
        trait_key = [*trait][0]
        root = trait[trait_key]
        missing_modifiers = not any([bool(root.get(modifier)) for modifier in TRAIT_MODIFIER_KEYS])
        if missing_modifiers and not root.get("custom_tooltip"):
            issues.append(
                f"Trait has no modifiers, and is !!missing!! custom_tooltip (BAD)"
            )
        if root.get('councilor_modifier') or root.get('triggered_councilor_modifier'):
            if root.get("is_councilor_trait") != True:
                issues.append(
                    "Trait has councilor modifiers but is_councilor_trait is NOT set"
                )
        if MISSING in str(trait) or PLACEHOLDER in str(trait):
            issues.append(
                "Trait has placeholder values/missing values"
            )
        if len(issues):
            rogue_trait_names.append(
                f"{trait_key} ... {','.join(issues)}"
            )
    if len(rogue_trait_names):
        sys.stdout.write(f"** Found {len(rogue_trait_names)} traits needing review:\n")
        for trait_name in rogue_trait_names:
            sys.stdout.write(f"{trait_name}\n")

def sort_and_filter_pipeline_files() -> dict:
    """ separate traits by feature and then organize by rarity """
    data_to_be_written = {
        "commander": {},
        "official": {},
        "scientist": {}
    }
    for leader_class in LEADER_CLASSES:
        pipeline_source_file = f"00_mre_{leader_class}_traits.json"
        buffer = ''
        input_filename = os.path.join('build', pipeline_source_file)
        with open(input_filename, "r") as input_file:
            buffer = json_load(input_file)
        # Subclasses are trickled up in the run_mre_trait_pipeline script
        # traits_with_populated_subclasses = trickle_up_subclass_requirements(
        #     buffer, for_class=leader_class)
        highest_tier_traits = pick_highest_tier_of_trait(buffer)
        traits_sorted_by_feature = filter_traits_by_mod_feature(highest_tier_traits)
        # has leader_making and core_modifying keys
        traits_filtered_by_rarity = {
            "leader_making_traits": [],
            "core_modifying_traits": [],
            "councilor_editor_traits": [],
        }
        # Go into leader_making_traits and core_modifying_traits, filter by rarity
        traits_filtered_by_rarity["leader_making_traits"] = filter_traits_by_rarity(
            traits_sorted_by_feature["leader_making_traits"]
        )
        traits_filtered_by_rarity["core_modifying_traits"] = filter_traits_by_rarity(
            traits_sorted_by_feature["core_modifying_traits"]
        )
        traits_filtered_by_rarity["councilor_editor_traits"] = filter_traits_by_rarity(
            traits_sorted_by_feature["councilor_editor_traits"]
        )
        data_to_be_written[leader_class] = traits_filtered_by_rarity

    return data_to_be_written

def trickle_up_subclass_requirements(sorted_not_filtered_traits_json, for_class):
    # Typically the tier 1 trait will have the subclass req and its 2/3 replacement wont
    trait_to_subclass_map = {}
    collected_traits = []
    for trait in sorted_not_filtered_traits_json:
        trait_name = [*trait][0]
        base_trait_name = trait_name
        root = trait[trait_name]
        if trait_name in SKIP_TRAIT_FOR_SUBCLASS_LIST:
            if SKIP_TRAIT_FOR_SUBCLASS_LIST[trait_name] == for_class:
                # This trait is a serious exception and shall be skipped
                logger.warn(
                    f"** Skipped {trait_name} as it was in the skip list for {for_class} traits."
                )
                continue
        trait_is_first_of_series = not trait_name[-1].isdigit()
        if trait_name[-1].isdigit():
            base_trait_name = trait_name.rsplit('_',1)[0]
        if trait_is_first_of_series:
            if root.get('required_subclass'):
                trait_to_subclass_map[base_trait_name] = root['required_subclass']
            else:
                trait_to_subclass_map[base_trait_name] = "skip"
        else:
            potential_subclass = trait_to_subclass_map.get(base_trait_name, MISSING)
            if potential_subclass == "skip":
                1
            elif potential_subclass == MISSING:
                sys.exit(
                    f"We expected a subclass but didnt have one for {trait}"
                )
            else:
                trait[trait_name]['required_subclass'] = potential_subclass
                logger.debug(
                    f"We updated {trait_name} with subclass requirement {potential_subclass}"
                )
        collected_traits.append(trait)
    return collected_traits


def write_sorted_filtered_data_to_json_files(input_data: dict):
    """ Take data from sort_and_filter_pipeline_files and write to 3 files """
    output_filenames = []
    for leader_class in input_data:
        root = input_data[leader_class]
        output_filename = f"99_mre_{leader_class}_traits_for_codegen.json"
        output_filepath = os.path.join('build', output_filename)
        sys.stdout.write(f"** Writing code-ready traits for {leader_class} to {output_filename}...\n")
        with open(output_filepath, "w") as leader_traits_dest:
            json_dump(root, leader_traits_dest, indent=4)
            output_filenames.append(output_filepath)
    sys.stdout.write(
        f"Check the output files to see they're in good shape:\n"
    )
    for filename in output_filenames:
        sys.stdout.write(f"+ {filename}\n")

def qa_pipeline_files():
    if not os.path.exists(BUILD_FOLDER):
        sys.exit(
            'Couldnt find the build folder. Run this from within the mre_code_tools folder, '
            'and make sure that "run_mre_trait_pipeline" was run.'
        )
    for filename in PIPELINE_OUTPUT_FILES:
        input_file = os.path.join('build', filename)
        with open(input_file, "r") as input_file:
            sys.stdout.write(
                f"Results for {input_file.name}:\n"
            )
            buffer = json_load(input_file)
            do_qa_on_pipeline_files(buffer)

if __name__ == "__main__":
    start_time = time.time()
    parser = argparse.ArgumentParser(
        prog="0xRetro Machine & Robot Expansion Data Tools",
        description="Do operations on filtered data crunched from base trait files"
    )
    parser.add_argument(
        '--infile',
        help='A traits JSON file that we processed, like 00_mre_commander_traits.json, created from the pipeline script.',
        required=False
    )
    parser.add_argument(
        '--qa', required=False,
        help="Put together a list of trait names where the trait data doesn't have any known modifiers.",
        action="store_true"
    )
    parser.add_argument(
        '--qa_all',
        action="store_true",
        help="Checks traits for issues, in all 3 files produced by run_me_trait_pipeline.py",
        required=False
    )
    parser.add_argument(
        '--sort_filter_all',
        action="store_true",
        help="Load the traits pipeline files, sort and filter them further, and write them to JSON for us to use in code gen.",
        required=False
    )
    args = parser.parse_args()
    if args.infile and args.qa:
        with open(args.infile, "r") as input_file:
            buffer = json_load(input_file)
            do_qa_on_pipeline_files(buffer)
    elif args.qa_all:
        qa_pipeline_files()
    elif args.sort_filter_all:
        all_traits_processed_data = sort_and_filter_pipeline_files()
        write_sorted_filtered_data_to_json_files(all_traits_processed_data)
    execution_time = time.time() - start_time
    sys.stdout.write(
        f"\nDone in {str(execution_time)[:5]} seconds"
    )