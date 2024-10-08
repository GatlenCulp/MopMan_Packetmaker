from typing import Any
from pathlib import Path
import logging
from src.utils import make_id_from_title
from src.pdf_helpers import mergePdfs
from src.add_footer2pdf import add_footer_to_pdf

def generate_packet(
    precontext: dict[str, Any],
    output_dir: Path,
    cover_pdf_path: Path | None,
    device_reading_paths: list[Path] | None,
    further_pdf_path: Path | None,
    config: dict[str, Any],
    logger: logging.Logger,
) -> Path | None:
    if config["generate"]["packet"]:
        print("\n")
        logger.info(
            "Merging cover, core readings, device readings, and further reading page into packet..."
        )
        reading_pdf_paths = [
            Path(reading["trimmed_pdf"]) for reading in precontext["core_readings"]
        ]

        packet_path = mergePdfs(
            ([cover_pdf_path] if cover_pdf_path else [])
            + reading_pdf_paths
            + (device_reading_paths or [])
            + ([further_pdf_path] if further_pdf_path else []),
            output_path=output_dir
            / Path(make_id_from_title(precontext["curriculum_name"]) + ".pdf"),
        )

        packet_path = add_footer_to_pdf(
            packet_path,
            packet_path,
            footer_text=precontext["program_name"] + " Readings — Page {i} of {n}",
        )

        logger.info(f"[SUCCESS] Packet created. {packet_path}")
        return packet_path
    return None