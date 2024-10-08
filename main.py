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
from typing import Any
from pathlib import Path

from src.add_footer2pdf import add_footer_to_pdf
from src.airtable_api import getPrecontextForCurriculum
from src.pdf_helpers import mergePdfs
from src.DocumentGenerator import (
    CoverGenerator,
    DeviceReadingGenerator,
    FurtherGenerator,
    GuideGenerator,
    logger,
)
from src.template_factory import adjustLogo, makeIDFromTitle

config = json.load(open("config.json", "r"))


def check_permissions(path: Path) -> bool:
    if not os.access(path, os.R_OK | os.W_OK):
        logger.error(f"Insufficient permissions for {path}")
        return False
    return True


def getPrecontext(curriculum_id: str, output_dir: Path, option_num: int = 1) -> dict[str, Any] | None:
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

def _generate_cover(precontext: dict[str, Any], output_dir: Path) -> Path | None:
    if config["generate"]["cover"]:
        cover = CoverGenerator(
            Path(config["templates"]["cover"]),
            output_dir / Path("Cover"),
            precontext,
            overwrite=True,
        )
        return cover.pdf_path

def _generate_device_readings(precontext: dict[str, Any], output_dir: Path) -> list[Path] | None:
    device_reading_paths = []
    if config["generate"]["device_readings"]:
        for reading in precontext["core_readings"]:
            if not reading["trimmed_pdf"] and not reading["read_on_device"]:
                raise ValueError(
                    f"Reading {reading['title']} has no trimmed pdf and is not labeled as read_on_device."
                )
            if not reading["read_on_device"]:
                continue
            
            # Create a new context for each device reading
            device_reading_context = deepcopy(precontext)
            device_reading_context["device_reading"] = reading
            
            device_reading = DeviceReadingGenerator(
                Path(config["templates"]["device_reading"]),
                output_dir / Path(f"Device Readings/{makeIDFromTitle(reading['title'])}"),
                device_reading_context,
                overwrite=True,
            )
            reading["trimmed_pdf"] = device_reading.pdf_path
            device_reading_paths.append(device_reading.pdf_path)
        
        return device_reading_paths
    return None


def _generate_further_readings(precontext: dict[str, Any], output_dir: Path) -> Path | None:
    if precontext["further_readings"] and config["generate"]["further_readings"]:
        further = FurtherGenerator(
            Path(config["templates"]["further_reading"]),
            output_dir / Path("Further"),
            precontext,
            overwrite=True,
        )
        return further.pdf_path

def _generate_packet(precontext: dict[str, Any], output_dir: Path, cover_pdf_path: Path | None, device_reading_paths: list[Path] | None, further_pdf_path: Path | None) -> Path | None:
    if config["generate"]["packet"]:
        print("\n")
        logger.info("Merging cover, core readings, device readings, and further reading page into packet...")
        reading_pdf_paths = [Path(reading["trimmed_pdf"]) for reading in precontext["core_readings"]]
        
        packet_path = mergePdfs(
            ([cover_pdf_path] if cover_pdf_path else [])
            + reading_pdf_paths
            + (device_reading_paths or [])
            + ([further_pdf_path] if further_pdf_path else []),
            output_path=output_dir / Path(makeIDFromTitle(precontext["curriculum_name"]) + ".pdf"),
        )
        
        packet_path = add_footer_to_pdf(
            packet_path,
            packet_path,
            footer_text=precontext["program_name"] + " Readings — Page {i} of {n}",
        )
        
        logger.info(f"[SUCCESS] Packet created. {packet_path}")
        return packet_path
    return None

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

    cover_pdf_path = _generate_cover(precontext, output_dir)
    device_reading_paths = _generate_device_readings(precontext, output_dir)
    further_pdf_path = _generate_further_readings(precontext, output_dir)
    
    packet_path = _generate_packet(precontext, output_dir, cover_pdf_path, device_reading_paths, further_pdf_path)

    ## Generate TA Guides
    if config["generate"]["tas_guides"]:
        print("\n")
        logger.info("Generating TA guides. This may take a while...")
        guide_template_path = Path(config["templates"]["tas_guide"])
        ta_guide_output_dir = output_dir / Path("TA Guides")
        for cohort in precontext["cohorts"]:
            logger.info(f"Making {cohort['name']}")
            precontext["cohort"] = cohort
            guide_name = f'{makeIDFromTitle(precontext["cohort"]["name"])} n{precontext["cohort"]["num_members"]}'
            guide_dir = ta_guide_output_dir / Path(guide_name)
            guide = GuideGenerator(
                guide_template_path, guide_dir, precontext, overwrite=True
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


if __name__ == "__main__":
    # In the main function, before generating the cover:
    if not check_permissions(config["output_dir"]):
        raise PermissionError(
            f"Insufficient permissions for output directory: {config["output_dir"]}"
        )
    for curriculum, details in config["curriculum"].items():
        if details["make_packet"]:
            curriculum_id = details["record_id"]
            output_dir = Path(config["output_dir"]) / Path(makeIDFromTitle(curriculum))
            main(curriculum_id, output_dir=output_dir)
            subprocess.call(["open", "-R", str(output_dir)])
