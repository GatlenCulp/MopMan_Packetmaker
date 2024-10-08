from typing import Any
from pathlib import Path
from copy import deepcopy
from src.DocumentGenerator import DeviceReadingGenerator
from src.utils import make_id_from_title

def generate_device_readings(
    precontext: dict[str, Any], output_dir: Path, config: dict[str, Any]
) -> list[Path] | None:
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
                output_dir
                / Path(f"Device Readings/{make_id_from_title(reading['title'])}"),
                device_reading_context,
                overwrite=True,
            )
            reading["trimmed_pdf"] = device_reading.pdf_path
            device_reading_paths.append(device_reading.pdf_path)

        return device_reading_paths
    return None