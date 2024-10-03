# https://jinja.palletsprojects.com/en/3.1.x/templates/#line-statements
# from precontexts.gov4_precontext import gov4_precontext as precontext
from src.template_factory import adjustLogo
from copy import deepcopy
import pathlib as pl
from src.airtable_api import getPrecontextForCurriculum
import json
from src.template_factory import makeIDFromTitle
from pypdf import PdfWriter
from src.add_footer2pdf import add_footer_to_pdf
import os
from src.DocumentGenerator import (
    CoverGenerator,
    FurtherGenerator,
    GuideGenerator,
    DeviceReadingGenerator,
    logger,
)
import subprocess


config = json.load(open("config.json", "r"))


def check_permissions(path):
    if not os.access(path, os.R_OK | os.W_OK):
        logger.error(f"Insufficient permissions for {path}")
        return False
    return True

# In the main function, before generating the cover:
if not check_permissions(config["output_dir"]):
    raise PermissionError(f"Insufficient permissions for output directory: {config["output_dir"]}")

# def convertToPdf(path: pl.Path) -> pl.Path:
#     assert isinstance(path, pl.Path)
#     docx2pdf.convert(
#         str(path),
#         str(path.with_suffix(".pdf"))
#     )
#     return path.with_suffix(".pdf")


def mergePdfs(
    pdf_paths: list, output_path: pl.Path, merge_on_odd: bool = True
) -> pl.Path:
    assert isinstance(pdf_paths, list)
    assert all([isinstance(path, pl.Path) for path in pdf_paths])
    assert isinstance(output_path, pl.Path)
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


def getPrecontext(curriculum_id, output_dir, option_num: int = 1) -> dict:
    if option_num == 1:
        precontext = getPrecontextForCurriculum(
            curriculum_id, output_dir / pl.Path("precontext")
        )
        return precontext
    elif option_num == 2:
        raise NotImplementedError("Option 2 not implemented")
        # precontext_path = "/Users/hugz/Library/CloudStorage/OneDrive-Personal/Desktop/7x Work-Projects/71 MS Word Automation/precontexts/test1/aisf_ml_meeting_5__model_internals/precontext.json"
        # with open(precontext_path, "r") as f:
        #     precontext = json.load(f)
        # return precontext


def main(curriculum_id: str, output_dir: pl.Path = pl.Path("./output/")) -> None:
    assert isinstance(curriculum_id, str)
    assert isinstance(output_dir, pl.Path)
    output_dir.mkdir(parents=True, exist_ok=True)

    print("\n")
    logger.info("Getting precontext...")
    precontext = getPrecontext(curriculum_id, output_dir, option_num=1)
    logger.info("[SUCCESS] precontext collected.")

    ## Fix Logo
    print("\n")
    logger.info("Fixing logo...")
    precontext = deepcopy(precontext)
    logo_path = pl.Path(precontext["logo_path"])
    precontext["logo_path"] = str(adjustLogo(logo_path, output_path=output_dir))
    logger.info(f"[SUCCESS] logo fixed. {precontext['logo_path']}")

    # Generate Cover
    cover_pdf_path = None
    if config["generate"]["cover"]:
        cover = CoverGenerator(
            pl.Path(config["templates"]["cover"]),
            output_dir / pl.Path("Cover"),
            precontext,
            overwrite=True,
        )
        cover_pdf_path = cover.pdf_path

    # TODO: Fix this, word is giving an error
    # 2024-02-11 16:52:33,198 - MopMan - ERROR - [ERROR] output/aisst_intro_fellowship_spring_2024_meeting_0__introduction_to_machine_learning_optional/Device Readings/but_what_is_a_neural_network/but_what_is_a_neural_network.docx could not be converted to pdf at output/aisst_intro_fellowship_spring_2024_meeting_0__introduction_to_machine_learning_optional/Device Readings/but_what_is_a_neural_network/but_what_is_a_neural_network.pdf (DocumentGenerator.py:156)
    # 2024-02-11 16:52:33,199 - MopMan - ERROR - 1 (DocumentGenerator.py:157)
    # Very odd, error only seems to occur for AISST readings
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
                pl.Path(config["templates"]["device_reading"]),
                output_dir
                / pl.Path(f"Device Readings/{makeIDFromTitle(reading['title'])}"),
                precontext,
                overwrite=True,
            )
            reading["trimmed_pdf"] = device_reading.pdf_path
            logger.info(f"[SUCCESS] Device reading generated. {reading['trimmed_pdf']}")

    ## Generate Further Readings
    further_pdf_path = None
    if precontext["further_readings"] and config["generate"]["further_readings"]:
        further = FurtherGenerator(
            pl.Path(config["templates"]["further_reading"]),
            output_dir / pl.Path("Further"),
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
            pl.Path(reading["trimmed_pdf"]) for reading in precontext["core_readings"]
        ]
        packet_path = mergePdfs(
            ([cover_pdf_path] if cover_pdf_path else [])
            + reading_pdf_paths
            + ([further_pdf_path] if further_pdf_path else []),
            output_path=output_dir
            / pl.Path(makeIDFromTitle(precontext["curriculum_name"]) + ".pdf"),
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
        guide_template_path = pl.Path(config["templates"]["tas_guide"])
        ta_guide_output_dir = output_dir / pl.Path("TA Guides")
        for cohort in precontext["cohorts"]:
            logger.info(f"Making {cohort['name']}")
            precontext["cohort"] = cohort
            guide_name = f'{makeIDFromTitle(precontext["cohort"]["name"])} n{precontext["cohort"]["num_members"]}'
            guide_dir = ta_guide_output_dir / pl.Path(guide_name)
            guide = GuideGenerator(
                guide_template_path, guide_dir, precontext, overwrite=True
            )
            meeting_ta_guide_pdf = (
                [pl.Path(precontext["meeting_ta_guide_pdf"])]
                if precontext["meeting_ta_guide_pdf"]
                else []
            )
            guide_pdfs = (
                [guide.pdf_path]
                + meeting_ta_guide_pdf
                + [pl.Path(precontext["base_ta_guide_pdf"])]
            )
            guide_path = mergePdfs(
                guide_pdfs,
                output_path=ta_guide_output_dir / pl.Path(guide_name + ".pdf"),
            )
            logger.info(f"[SUCCESS] {guide_path}")
        logger.info("[SUCCESS] All TA guides generated.")


if __name__ == "__main__":
    for curriculum, details in config["curriculum"].items():
        if details["make_packet"]:
            curriculum_id = details["record_id"]
            output_dir = pl.Path(config["output_dir"]) / pl.Path(
                makeIDFromTitle(curriculum)
            )
            main(curriculum_id, output_dir=output_dir)
            subprocess.call(["open", "-R", str(output_dir)])
