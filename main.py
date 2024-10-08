"""
main.py
Main module for generating curriculum packets and TA guides.

This module provides functionality to:
1. Generate curriculum packets including cover pages, core readings, and further readings.
2. Create TA guides for different cohorts.
3. Merge PDFs and add footers to the final documents.

The module uses configuration from a JSON file and interacts with Airtable API
to fetch curriculum data. It also utilizes various helper modules for document
generation, PDF manipulation, and file management.

Usage:
    Run this script directly to generate packets for curricula specified in the config file.

Configuration:
    The script uses a 'config.json' file for various settings including curriculum details,
    output directories, and generation options.
"""

import json
import os
import subprocess
from copy import deepcopy
from pathlib import Path
from typing import Any

from src.packet.cover import generate_cover
from src.packet.packet import generate_packet
from src.packet.further_readings import generate_further_readings
from src.packet.device_readings import generate_device_readings
from src.airtable_api import getPrecontextForCurriculum
from src.DocumentGenerator import (
    GuideGenerator,
    logger,
)
from src.pdf_helpers import mergePdfs
from src.template_factory import adjustLogo, makeIDFromTitle

config = json.load(open("config.json", "r"))


def check_permissions(path: Path) -> bool:
    if not os.access(path, os.R_OK | os.W_OK):
        logger.error(f"Insufficient permissions for {path}")
        return False
    return True


def getPrecontext(
    curriculum_id: str, output_dir: Path, option_num: int = 1
) -> dict[str, Any] | None:
    """
    Retrieves precontext data for a given curriculum.

    This function fetches the necessary precontext information for a curriculum,
    which includes details about the program, readings, and other relevant data.
    It supports multiple options for retrieving this data, though currently only
    option 1 is implemented.

    :param str curriculum_id: ID of the curriculum to fetch precontext for.
    :param Path output_dir: Directory to save the precontext data.
    :param int option_num: Option number for fetching precontext, defaults to 1.
    :raises NotImplementedError: If the option number is not implemented.
    :return dict[str, Any]: Precontext data.
    """
    if option_num == 1:
        precontext = getPrecontextForCurriculum(
            curriculum_id, output_dir / Path("precontext")
        )
        return precontext
    elif option_num == 2:
        raise NotImplementedError("Option 2 not implemented")


def _generate_ta_guides(precontext: dict[str, Any], output_dir: Path) -> None:
    if config["generate"]["tas_guides"]:
        print("\n")
        logger.info("Generating TA guides. This may take a while...")
        guide_template_path = Path(config["templates"]["tas_guide"])
        ta_guide_output_dir = output_dir / Path("TA Guides")

        for cohort in precontext["cohorts"]:
            logger.info(f"Making {cohort['name']}")
            cohort_context = deepcopy(precontext)
            cohort_context["cohort"] = cohort
            guide_name = f'{makeIDFromTitle(cohort["name"])} n{cohort["num_members"]}'
            guide_dir = ta_guide_output_dir / Path(guide_name)

            guide = GuideGenerator(
                guide_template_path, guide_dir, cohort_context, overwrite=True
            )

            meeting_ta_guide_pdf = (
                [Path(precontext["meeting_ta_guide_pdf"])]
                if precontext["meeting_ta_guide_pdf"]
                else []
            )

            guide_pdfs = (
                [guide.pdf_path]
                + meeting_ta_guide_pdf
                + [Path(precontext["base_ta_guide_pdf"])]
            )

            guide_path = mergePdfs(
                guide_pdfs,
                output_path=ta_guide_output_dir / Path(guide_name + ".pdf"),
            )

            logger.info(f"[SUCCESS] {guide_path}")

        logger.info("[SUCCESS] All TA guides generated.")


def main(curriculum_id: str, output_dir: Path = Path("./output/")) -> None:
    """
    Main function to generate curriculum packets and TA guides.

    This function orchestrates the entire process of generating curriculum packets
    and TA guides, including fetching precontext data, adjusting the logo, generating
    cover pages, device readings, further readings, merging PDFs, and creating TA guides.

    :param str curriculum_id: ID of the curriculum to generate for.
    :param Path output_dir: Directory to save the generated files, defaults to "./output/".
    """
    assert isinstance(curriculum_id, str)
    assert isinstance(output_dir, Path)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n")
    logger.info("Getting precontext...")
    precontext = getPrecontext(curriculum_id, output_dir, option_num=1)
    assert precontext is not None
    logger.info("[SUCCESS] precontext collected.")

    ## Fix Logo
    print("\n")
    logger.info("Fixing logo...")
    precontext = deepcopy(precontext)
    logo_path = Path(precontext["logo_path"])
    precontext["logo_path"] = str(adjustLogo(logo_path, output_path=output_dir))
    logger.info(f"[SUCCESS] logo fixed. {precontext['logo_path']}")

    cover_pdf_path = generate_cover(precontext, output_dir, config)
    device_reading_paths = generate_device_readings(precontext, output_dir, config)
    further_pdf_path = generate_further_readings(precontext, output_dir, config)

    _ = generate_packet(
        precontext, output_dir, cover_pdf_path, device_reading_paths, further_pdf_path, config, logger
    )

    _generate_ta_guides(precontext, output_dir)


def check_output_permissions(output_dir: Path) -> None:
    if not check_permissions(output_dir):
        raise PermissionError(
            f"Insufficient permissions for output directory: {output_dir}"
        )


def process_curriculum(curriculum: str, details: dict, base_output_dir: Path) -> None:
    if details["make_packet"]:
        curriculum_id = details["record_id"]
        output_dir = base_output_dir / Path(makeIDFromTitle(curriculum))
        main(curriculum_id, output_dir=output_dir)
        open_output_directory(output_dir)


def open_output_directory(output_dir: Path) -> None:
    subprocess.call(["open", "-R", str(output_dir)])


def run_curriculum_generation() -> None:
    base_output_dir = Path(config["output_dir"])
    check_output_permissions(base_output_dir)

    for curriculum, details in config["curriculum"].items():
        process_curriculum(curriculum, details, base_output_dir)


if __name__ == "__main__":
    run_curriculum_generation()
