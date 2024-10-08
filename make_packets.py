# https://jinja.palletsprojects.com/en/3.1.x/templates/#line-statements
# from precontexts.gov4_precontext import gov4_precontext as precontext
import json
import subprocess
from copy import deepcopy
from pathlib import Path

from pypdf import PdfWriter

from src.add_footer2pdf import add_footer_to_pdf
from src.airtable_api import getPrecontextForCurriculum
from src.DocumentGenerator import (
    CoverGenerator,
    DeviceReadingGenerator,
    FurtherGenerator,
    GuideGenerator,
    logger,
)
from src.template_factory import adjustLogo, makeIDFromTitle

with open("config.json", "r") as config_file:
    config = json.load(config_file)


# def convertToPdf(path: Path) -> Path:
#     assert isinstance(path, Path)
#     docx2pdf.convert(
#         str(path),
#         str(path.with_suffix(".pdf"))
#     )
#     return path.with_suffix(".pdf")


def mergePdfs(pdf_paths: list, output_path: Path, merge_on_odd: bool = True) -> Path:
    assert isinstance(pdf_paths, list)
    assert all([isinstance(path, Path) for path in pdf_paths])
    assert isinstance(output_path, Path)
    pdf_writer = PdfWriter()
    for pdf in pdf_paths:
        if not pdf:
            continue
        pdf_writer.append(str(pdf))
        if merge_on_odd and len(pdf_writer.pages) % 2 == 1:
            pdf_writer.add_blank_page()
    pdf_writer.write(str(output_path))
    pdf_writer.close()
    return output_path


def getPrecontext(curriculum_id: str, output_dir: Path, option_num: int = 1) -> dict:
    if option_num == 1:
        precontext = getPrecontextForCurriculum(
            curriculum_id, output_dir / Path("precontext")
        )
        return precontext
    elif option_num == 2:
        precontext_path = "/Users/hugz/Library/CloudStorage/OneDrive-Personal/Desktop/7x Work-Projects/71 MS Word Automation/precontexts/test1/aisf_ml_meeting_5__model_internals/precontext.json"
        with open(precontext_path, "r") as f:
            precontext = json.load(f)
        return precontext


def make_packet(curriculum_id: str, output_dir: Path = Path("./output/")) -> None:
    assert isinstance(curriculum_id, str)
    assert isinstance(output_dir, Path)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n")
    logger.info("Getting precontext...")
    precontext = getPrecontext(curriculum_id, output_dir, option_num=1)
    logger.info("[SUCCESS] precontext collected.")

    ## Fix Logo
    print("\n")
    logger.info("Fixing logo...")
    precontext = deepcopy(precontext)
    logo_path = Path(precontext["logo_path"])
    precontext["logo_path"] = str(adjustLogo(logo_path, output_path=output_dir))
    logger.info(f"[SUCCESS] logo fixed. {precontext['logo_path']}")

    # Generate Cover
    cover_pdf_path = None
    if config["generate"]["cover"]:
        cover = CoverGenerator(
            Path(config["templates"]["cover"]),
            output_dir / Path("Cover"),
            precontext,
            overwrite=True,
        )
        cover_pdf_path = cover.pdf_path

    ## Generate Device Readings QR Code pages if needed
    if config["generate"]["device_readings"]:
        for reading in precontext["core_readings"]:
            if not reading["trimmed_pdf"] and not reading["read_on_device"]:
                raise ValueError(
                    f"Reading {reading['title']} has no trimmed pdf and is not labeled as read_on_device."
                )
            if not reading["read_on_device"]:
                continue
            logger.info(f"Generating device reading for {reading['title']}...")
            precontext["device_reading"] = reading
            device_reading = DeviceReadingGenerator(
                Path(config["templates"]["device_reading"]),
                output_dir
                / Path(f"Device Readings/{makeIDFromTitle(reading['title'])}"),
                precontext,
                overwrite=True,
            )
            reading["trimmed_pdf"] = device_reading.pdf_path
            logger.info(f"[SUCCESS] Device reading generated. {reading['trimmed_pdf']}")

    ## Generate Further Readings
    further_pdf_path = None
    if precontext["further_readings"] and config["generate"]["further_readings"]:
        further = FurtherGenerator(
            Path(config["templates"]["further_reading"]),
            output_dir / Path("Further"),
            precontext,
            overwrite=True,
        )
        further_pdf_path = further.pdf_path

    ## Merge Cover + Readings + Further
    if config["generate"]["packet"]:
        print("\n")
        logger.info(
            "Merging cover, core readings, and further reading page into packet..."
        )
        reading_pdf_paths = [
            Path(reading["trimmed_pdf"]) for reading in precontext["core_readings"]
        ]
        packet_path = mergePdfs(
            ([cover_pdf_path] if cover_pdf_path else [])
            + reading_pdf_paths
            + ([further_pdf_path] if further_pdf_path else []),
            output_path=output_dir
            / Path(makeIDFromTitle(precontext["curriculum_name"]) + ".pdf"),
        )
        packet_path = add_footer_to_pdf(
            packet_path,
            packet_path,
            footer_text=precontext["program_name"] + " Readings — Page {i} of {n}",
        )
        logger.info(f"[SUCCESS] Packet created. {packet_path}")

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


def make_packets_from_config(config: dict) -> None:
    for curriculum in config["curriculum"]:
        if config["curriculum"][curriculum]["make_packet"]:
            curriculum_id = config["curriculum"][curriculum]["record_id"]
            output_dir = Path(config["output_dir"]) / Path(makeIDFromTitle(curriculum))
            make_packet(curriculum_id, output_dir=output_dir)
            subprocess.call(["open", "-R", str(output_dir)])


if __name__ == "__main__":
    make_packets_from_config(config)
