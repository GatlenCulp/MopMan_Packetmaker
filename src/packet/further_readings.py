from typing import Any
from pathlib import Path
from src.DocumentGenerator import FurtherGenerator

def generate_further_readings(
    precontext: dict[str, Any], output_dir: Path, config: dict[str, Any]
) -> Path | None:
    if precontext["further_readings"] and config["generate"]["further_readings"]:
        further = FurtherGenerator(
            Path(config["templates"]["further_reading"]),
            output_dir / Path("Further"),
            precontext,
            overwrite=True,
        )
        return further.pdf_path
