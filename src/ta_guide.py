from copy import deepcopy
from pathlib import Path
from typing import Any
import logging

from src.DocumentGenerator import GuideGenerator
from src.utils.pdf_helpers import mergePdfs
from src.utils.make_id_from_title import make_id_from_title

def generate_ta_guides(precontext: dict[str, Any], output_dir: Path, config: dict[str, Any], logger: logging.Logger) -> None:
    if config["generate"]["tas_guides"]:
        print("\n")
        logger.info("Generating TA guides. This may take a while...")
        guide_template_path = Path(config["templates"]["tas_guide"])
        ta_guide_output_dir = output_dir / Path("TA Guides")

        for cohort in precontext["cohorts"]:
            logger.info(f"Making {cohort['name']}")
            cohort_context = deepcopy(precontext)
            cohort_context["cohort"] = cohort
            guide_name = f'{make_id_from_title(cohort["name"])} n{cohort["num_members"]}'
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