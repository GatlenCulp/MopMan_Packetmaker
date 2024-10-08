# https://jinja.palletsprojects.com/en/3.1.x/templates/#line-statements
# from precontexts.gov4_precontext import gov4_precontext as precontext
import json
from copy import deepcopy
from pathlib import Path

from docxtpl import RichText

from src.airtable_api import getPrecontextForCurriculum
from src.DocumentGenerator import (
    DocumentGenerator,
    logger,
)
from src.template_factory import adjustLogo, make_id_from_title


class CoverTestGenerator(DocumentGenerator):
    def processContext(self, context: dict) -> dict:
        assert isinstance(context, dict)
        print(context["color_primary"])
        context["title"] = RichText("Test Title", color=context["color_primary_faded"])
        return context


def getPrecontext(curriculum_id, output_dir, option_num: int = 1) -> dict:
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


def main(curriculum_id: str, output_dir: Path = Path("./output/")) -> None:
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
    cover = CoverTestGenerator(
        Path("templates/Cover Page Template.docx"),
        output_dir / Path("Cover"),
        precontext,
        overwrite=True,
    )


if __name__ == "__main__":
    curriculum_ids = {
        "AISF ML Meeting 5": "reccFZa1fy2EV3qPI",
        "Orchid Meeting 5": "rec1fJFpgwmLA7V5T",
    }
    curriculum = "AISF ML Meeting 5"
    main(
        curriculum_ids[curriculum],
        output_dir=Path("./output") / Path(make_id_from_title("covertest")),
    )
