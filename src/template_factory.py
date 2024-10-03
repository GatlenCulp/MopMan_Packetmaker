from PIL import Image, ImageChops
import qrcode
from src.favicon_downloader import get_favicon_from_website
import pathlib as pl


def adjustLogo(logo_path: pl.Path, output_path: pl.Path = pl.Path("./")) -> pl.Path:
    assert isinstance(logo_path, pl.Path)
    assert isinstance(output_path, pl.Path)

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
        cropped_logo_path = output_path / pl.Path(
            f"{logo_path.stem}_cropped{logo_path.suffix}"
        )
        im.save(str(cropped_logo_path))
        return cropped_logo_path


## Make QRCode
def makeQRCode(url: str, title: str, output_path: pl.Path = pl.Path("./")) -> pl.Path:
    assert isinstance(output_path, pl.Path)

    qr = qrcode.QRCode(
        version=5,
        box_size=20,
        border=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    path = output_path / pl.Path(f"{title} QRCode.png")
    img.save(str(path))
    return path


def makeIDFromTitle(title):
    title = title.replace("§", "section")
    return "".join(
        char.lower() for char in title if char.isalnum() or char == " "
    ).replace(" ", "_")


if __name__ == "__main__":
    pass
