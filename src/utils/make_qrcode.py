from pathlib import Path

import qrcode

def make_qrcode(url: str, title: str, output_path: Path = Path("./")) -> Path:
    assert isinstance(output_path, Path)

    qr = qrcode.QRCode(
        version=5,
        box_size=20,
        border=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,
    )
    qr.add_data(url)
    qr.make(fit=True)

    img = qr.make_image(fill_color="black", back_color="white")
    path = output_path / Path(f"{title} QRCode.png")
    img.save(str(path))
    return path