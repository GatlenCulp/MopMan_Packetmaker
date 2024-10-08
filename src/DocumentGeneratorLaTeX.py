from jinja2 import Environment, FileSystemLoader, select_autoescape
import subprocess
from copy import deepcopy
import pathlib as pl
import logging
import json
import urllib
import shutil


def latex_escape(text):
    """
    Escapes LaTeX special characters in the given text.
    """
    if text is None:
        return ""
    special_chars = {
        "&": r"\&",
        "%": r"\%",
        "$": r"\$",
        "#": r"\#",
        "_": r"\_",
        "{": r"\{",
        "}": r"\}",
        "~": r"\textasciitilde{}",
        "^": r"\textasciicircum{}",
        "\\": r"\textbackslash{}",
    }
    for char, escape in special_chars.items():
        text = text.replace(char, escape)
    return text


def makeIDFromTitle(title):
    # Dummy implementation for illustration
    return title.replace(" ", "_")


def makeQRCode(url, id, output_path):
    # Dummy implementation for illustration
    qr_code_path = output_path / f"{id}_qrcode.png"
    # Generate QR code and save to qr_code_path
    return qr_code_path


def get_favicon_from_website(url, output_path):
    # Dummy implementation for illustration
    favicon_path = output_path / "favicon.png"
    # Download favicon and save to favicon_path
    return favicon_path


with open("config.json", "r") as config_file:
    config = json.load(config_file)


def initLogger() -> logging.Logger:
    """
    Initializes the logger.

    Returns:
    --------
    logging.Logger
        The initialized logger.
    """

    class CustomFormatter(logging.Formatter):
        grey = "\x1b[38;20m"
        yellow = "\x1b[33;20m"
        red = "\x1b[31;20m"
        bold_red = "\x1b[31;1m"
        reset = "\x1b[0m"
        format_str = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

        FORMATS = {
            logging.DEBUG: f"{grey}{format_str}{reset}",
            logging.INFO: f"{grey}{format_str}{reset}",
            logging.WARNING: f"{yellow}{format_str}{reset}",
            logging.ERROR: f"{red}{format_str}{reset}",
            logging.CRITICAL: f"{bold_red}{format_str}{reset}",
        }

        def format(self, record):
            log_fmt = self.FORMATS.get(record.levelno)
            formatter = logging.Formatter(log_fmt)
            return formatter.format(record)

    # create logger with 'spam_application'
    logger = logging.getLogger("MopMan")
    logger.setLevel(logging.DEBUG)

    # create console handler with a higher log level
    ch = logging.StreamHandler()
    ch.setLevel(logging.DEBUG)

    ch.setFormatter(CustomFormatter())

    logger.addHandler(ch)

    return logger


logger = initLogger()


class DocumentGenerator(object):
    """
    A class used to render a LaTeX template with a given context and output path.

    Attributes:
    -----------
    template_path : Path
        The path to the LaTeX template file.
    processContext : function, optional
        A function to process the context before rendering the template.

    Methods:
    --------
    defaultProcessContext(precontext: dict) -> dict:
        A default function to process the context. It returns a deepcopy of the precontext.
    generateTex(output_path: Path) -> Path:
        Renders the template with the context and saves it to the output_path.
    """

    def __init__(
        self,
        template_path: pl.Path,
        output_dir: pl.Path,
        precontext: dict,
        overwrite: bool = False,
    ) -> None:
        logger.info(f"template_path: {template_path}, output_dir: {output_dir}")
        assert isinstance(template_path, pl.Path)
        assert isinstance(output_dir, pl.Path)
        self.template_path = template_path
        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir
        # Set up the Jinja2 environment
        self.env = Environment(
            loader=FileSystemLoader(str(template_path.parent)),
            autoescape=select_autoescape(["tex"]),
        )
        self.env.filters["latex_escape"] = latex_escape
        # Load the template
        self.template = self.env.get_template(template_path.name)
        # Generate .tex file
        self.tex_path = self.generateTex(
            output_dir / pl.Path(output_dir.stem + ".tex"), precontext, overwrite
        )
        # Generate PDF
        self.pdf_path = self.generatePdf(
            output_dir / pl.Path(output_dir.stem + ".pdf"), precontext, overwrite
        )

    def processContext(self, precontext: dict) -> dict:
        assert isinstance(precontext, dict)
        return deepcopy(precontext)

    def generateTex(
        self, output_path: pl.Path, precontext: dict, overwrite: bool = False
    ) -> pl.Path:
        """
        Renders the template with the context and saves it to the output_path.

        Parameters:
        -----------
        output_path : Path
            The path to save the rendered template.

        Returns:
        --------
        Path
            The path to the saved rendered template.
        """
        assert isinstance(precontext, dict)
        assert isinstance(output_path, pl.Path)
        assert isinstance(overwrite, bool)
        if output_path.exists() and not overwrite:
            raise FileExistsError(
                f"{output_path} exists, please set 'overwrite' to True."
            )
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.context = deepcopy(precontext)
        print("\n")
        logger.info("Rendering LaTeX template...")
        self.context = self.processContext(self.context)
        # Render the template
        rendered_tex = self.template.render(self.context)
        # Save the rendered template to output_path
        with open(output_path, "w", encoding="utf-8") as f:
            f.write(rendered_tex)
        self.tex_path = output_path
        logger.info(f"[SUCCESS] {self.template_path} rendered to {self.tex_path}")

        return self.tex_path

    def generatePdf(
        self,
        output_path: pl.Path = None,
        precontext: dict = None,
        overwrite: bool = True,
    ) -> pl.Path:
        """
        Compiles the LaTeX document to PDF.

        Parameters:
        -----------
        output_path : Path
            The path to save the compiled PDF.

        Returns:
        --------
        Path
            The path to the compiled PDF.
        """
        assert (
            self.tex_path or precontext
        ), "Please provide a precontext or generate a tex file first."
        assert (
            isinstance(precontext, dict) or precontext is None
        ), f"Please provide a valid precontext. Received {precontext}."
        assert (
            (isinstance(output_path, pl.Path) and output_path.suffix == ".pdf")
            or output_path is None
        ), f"Please provide a valid output_path. Received {output_path}."
        assert isinstance(overwrite, bool)

        if not output_path:
            output_path = self.tex_path.with_suffix(".pdf")

        print("\n")
        logger.info("Compiling LaTeX to PDF...")
        try:
            # Use pdflatex to compile the .tex file
            # We'll use subprocess to call pdflatex
            # For safety, we should run pdflatex in the output directory
            compile_dir = self.output_dir
            tex_filename = self.tex_path.name
            command = ["pdflatex", "-interaction=nonstopmode", tex_filename]
            # Run the command in the compile_dir
            result = subprocess.run(
                command,
                cwd=str(compile_dir),
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            )
            if result.returncode != 0:
                logger.error("[ERROR] pdflatex compilation failed.")
                logger.error(result.stderr.decode())
                return pl.Path(config.get("error_pdf", "error.pdf"))
            self.pdf_path = output_path
        except Exception as e:
            logger.error(
                f"[ERROR] {self.tex_path} could not be compiled to pdf at {output_path}"
            )
            logger.error(e)
            return pl.Path(config.get("error_pdf", "error.pdf"))
        logger.info(f"[SUCCESS] {self.template_path} compiled to {self.pdf_path}")
        return self.pdf_path

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.template_path}, {self.output_dir}, {self.context})"


class CoverGenerator(DocumentGenerator):
    def processContext(self, context: dict) -> dict:
        assert isinstance(context, dict)
        # Ensure that image paths are correct and accessible to LaTeX
        logo_src = pl.Path(context["logo_path"])
        logo_dst = self.output_dir / logo_src.name
        shutil.copy(logo_src, logo_dst)
        context["logo_path"] = logo_dst.name  # Relative to output_dir

        # For readings, prepare the text and colors
        for reading in context.get("core_readings", []):
            reading["title_text"] = reading["title"]
            reading["title_color"] = context.get("color_primary_faded", "black")
            reading["subsection_text"] = (
                f"({reading['subsection']})" if reading.get("subsection") else ""
            )
            reading["subsection_color"] = context.get("color_primary_faded", "black")
            reading["author_year_text"] = f"({reading['author']}, {reading['year']})"
            reading["author_year_color"] = context.get("color_primary_faded", "black")
        return context


class FurtherGenerator(DocumentGenerator):
    def processContext(self, context: dict) -> dict:
        ## Logo
        logo_src = pl.Path(context["logo_path"])
        logo_dst = self.output_dir / logo_src.name
        shutil.copy(logo_src, logo_dst)
        context["logo_path"] = logo_dst.name  # Relative to output_dir

        ## Id, Truncate links, QR codes, and thumbnails to context
        for reading in context["further_readings"]:
            url = reading["url"]
            id = reading["id"] = makeIDFromTitle(
                reading["title"]
            )  # necessary because special characters are forbidden in file names.
            if url:
                ## Truncate
                scheme = urllib.parse.urlparse(url).scheme
                reading["truncated_url"] = url.replace(scheme + "://", "").replace(
                    "www.", ""
                )
                ## Add QR codes
                qr_code_dir = self.output_dir / pl.Path("qr_codes/")
                qr_code_dir.mkdir(parents=True, exist_ok=True)
                qr_code_path = makeQRCode(url, id, output_path=qr_code_dir)
                qr_code_dst = self.output_dir / qr_code_path.name
                shutil.copy(qr_code_path, qr_code_dst)
                reading["qr_code_path"] = qr_code_dst.name  # Relative to output_dir

                ## Add thumbnails if needed
                if not reading.get("thumbnail_path"):
                    thumbnail_dir = self.output_dir / pl.Path("thumbnails/")
                    thumbnail_dir.mkdir(parents=True, exist_ok=True)
                    thumbnail_path = thumbnail_dir / pl.Path(f"{id}_thumbnail.png")
                    thumbnail_path = get_favicon_from_website(url, thumbnail_path)
                    reading["thumbnail_path"] = str(thumbnail_path)
                else:
                    reading["thumbnail_path"] = str(reading["thumbnail_path"])
                if (
                    reading["thumbnail_path"]
                    and pl.Path(reading["thumbnail_path"]).exists()
                ):
                    thumbnail_src = pl.Path(reading["thumbnail_path"])
                    thumbnail_dst = self.output_dir / thumbnail_src.name
                    shutil.copy(thumbnail_src, thumbnail_dst)
                    reading["thumbnail_path"] = (
                        thumbnail_dst.name
                    )  # Relative to output_dir
            else:
                reading["truncated_url"] = ""
                reading["qr_code_path"] = ""
                reading["thumbnail_path"] = ""

        return context


class GuideGenerator(DocumentGenerator):
    def processContext(self, context: dict) -> dict:
        assert isinstance(context, dict)
        logo_src = pl.Path(context["logo_path"])
        logo_dst = self.output_dir / logo_src.name
        shutil.copy(logo_src, logo_dst)
        context["logo_path"] = logo_dst.name  # Relative to output_dir
        return context


class DeviceReadingGenerator(DocumentGenerator):
    def processContext(self, context: dict) -> dict:
        assert isinstance(context, dict)
        ## Logo
        logo_src = pl.Path(context["logo_path"])
        logo_dst = self.output_dir / logo_src.name
        shutil.copy(logo_src, logo_dst)
        context["logo_path"] = logo_dst.name  # Relative to output_dir

        ## Id, Truncate links, QR codes, and thumbnails to context
        reading = context["device_reading"]
        url = reading["url"]
        id = reading["id"] = makeIDFromTitle(
            reading["title"]
        )  # necessary because special characters are forbidden in file names.
        if url:
            ## Truncate
            scheme = urllib.parse.urlparse(url).scheme
            reading["truncated_url"] = url.replace(scheme + "://", "").replace(
                "www.", ""
            )
            ## Add QR codes
            qr_code_dir = self.output_dir / pl.Path("qr_codes/")
            qr_code_dir.mkdir(parents=True, exist_ok=True)
            qr_code_path = makeQRCode(url, id, output_path=qr_code_dir)
            qr_code_dst = self.output_dir / qr_code_path.name
            shutil.copy(qr_code_path, qr_code_dst)
            reading["qr_code_path"] = qr_code_dst.name  # Relative to output_dir

            ## Add thumbnails if needed
            if not reading.get("thumbnail_path"):
                thumbnail_dir = self.output_dir / pl.Path("thumbnails/")
                thumbnail_dir.mkdir(parents=True, exist_ok=True)
                thumbnail_path = thumbnail_dir / pl.Path(f"{id}_thumbnail.png")
                thumbnail_path = get_favicon_from_website(url, thumbnail_path)
                reading["thumbnail_path"] = str(thumbnail_path)
            else:
                reading["thumbnail_path"] = str(reading["thumbnail_path"])
            if (
                reading["thumbnail_path"]
                and pl.Path(reading["thumbnail_path"]).exists()
            ):
                thumbnail_src = pl.Path(reading["thumbnail_path"])
                thumbnail_dst = self.output_dir / thumbnail_src.name
                shutil.copy(thumbnail_src, thumbnail_dst)
                reading["thumbnail_path"] = thumbnail_dst.name  # Relative to output_dir
        else:
            reading["truncated_url"] = ""
            reading["qr_code_path"] = ""
            reading["thumbnail_path"] = ""

        return context


if __name__ == "__main__":
    # Example usage
    template_path = pl.Path("templates") / "cover_template.tex"
    output_dir = pl.Path("output") / "cover"
    precontext = {
        "logo_path": "path/to/logo.png",
        "color_primary_faded": "gray",
        "core_readings": [
            {
                "title": "Understanding LaTeX",
                "subsection": "An Introduction",
                "author": "John Doe",
                "year": "2021",
            },
            # Add more readings as needed
        ],
    }
    generator = CoverGenerator(template_path, output_dir, precontext)
