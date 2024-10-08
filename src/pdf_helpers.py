from pathlib import Path

from pypdf import PdfWriter


def mergePdfs(pdf_paths: list[Path], output_path: Path, merge_on_odd: bool = True) -> Path:
    assert isinstance(pdf_paths, list)
    assert all([isinstance(path, Path) for path in pdf_paths])
    assert isinstance(output_path, Path)
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