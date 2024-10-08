from pathlib import Path

from PIL import Image, ImageChops


def adjust_logo(logo_path: Path, output_path: Path = Path("./")) -> Path:
    assert isinstance(logo_path, Path)
    assert isinstance(output_path, Path)

    def trim(im):
        bg = Image.new(im.mode, im.size, im.getpixel((0, 0)))
        diff = ImageChops.difference(im, bg)
        diff = ImageChops.add(diff, diff, 2.0, -100)
        bbox = diff.getbbox()
        if bbox:
            return im.crop(bbox)

    if "cropped" in logo_path.stem:
        return logo_path
    else:
        im = Image.open(str(logo_path))
        im = trim(im)
        cropped_logo_path = output_path / Path(
            f"{logo_path.stem}_cropped{logo_path.suffix}"
        )
        assert im is not None
        im.save(str(cropped_logo_path))
        return cropped_logo_path



