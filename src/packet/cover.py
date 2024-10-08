from typing import Any
from pathlib import Path
from src.DocumentGenerator import CoverGenerator

def generate_cover(precontext: dict[str, Any], output_dir: Path, config: dict[str, Any]) -> Path | None:
    if config["generate"]["cover"]:
        cover = CoverGenerator(
            Path(config["templates"]["cover"]),
            output_dir / Path("Cover"),
            precontext,
            overwrite=True,
        )
        return cover.pdf_path