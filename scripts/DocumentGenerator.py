# from docx import Document
from docxtpl import DocxTemplate, InlineImage, RichText
from docx.shared import Cm
from copy import deepcopy
import pathlib as pl
import logging
from typing import Callable, Dict
# Word must be installed for this to work!!
import docx2pdf
from scripts.template_factory import makeIDFromTitle, makeQRCode, get_favicon_from_website
import urllib
import json
with open('config.json', 'r') as config_file:
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
        format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s (%(filename)s:%(lineno)d)"

        FORMATS = {
            logging.DEBUG: grey + format + reset,
            logging.INFO: grey + format + reset,
            logging.WARNING: yellow + format + reset,
            logging.ERROR: red + format + reset,
            logging.CRITICAL: bold_red + format + reset
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


if __name__ == '__main__':
    pass

class DocumentGenerator(object):
    """
    A class used to render a DocxTemplate with a given context and output path.

    Attributes:
    -----------
    template_path : Path
        The path to the DocxTemplate file.
    processContext : function, optional
        A function to process the context before rendering the template.

    Methods:
    --------
    defaultProcessContext(precontext: dict) -> dict:
        A default function to process the context. It returns a deepcopy of the precontext.
    generateDocx(output_path: Path) -> Path:
        Renders the template with the context and saves it to the output_path.
    """
    def __init__(self, template_path:pl.Path, output_dir:pl.Path, precontext: dict, overwrite:bool=False) -> None:
        logger.info(f"template_path: {template_path}, output_dir: {output_dir}")
        assert isinstance(template_path, pl.Path)
        assert isinstance(output_dir, pl.Path)
        self.template_path = template_path
        output_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir = output_dir
        self.template = DocxTemplate(str(template_path))
        self.docx_path = self.generateDocx(output_dir/pl.Path(output_dir.stem+".docx"), precontext, overwrite)
        self.pdf_path = self.generatePdf(output_dir/pl.Path(output_dir.stem+".pdf"), precontext, overwrite)

    def processContext(self, precontext: dict) -> dict:
         assert isinstance(precontext, dict)
         return deepcopy(precontext)

    def generateDocx(self, output_path: pl.Path, precontext: dict, overwrite:bool=False) -> pl.Path:
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
            raise FileExistsError(f"{output_path} exists, please set 'overwrite' to True.")
        output_path.parent.mkdir(parents=True, exist_ok=True)

        self.context = deepcopy(precontext)
        print("\n")
        logger.info("Rendering docx...")
        self.context = self.processContext(self.context)
        # Hopefully this works when called multiple times
        self.template.render(self.context)
        self.template.save(str(output_path))
        self.docx_path = output_path
        logger.info(f"[SUCCESS] {self.template_path} rendered to {self.docx_path}")

        return self.docx_path
    
    # TODO: Fix, not working
    def generatePdf(self, output_path: pl.Path=None, precontext: dict=None, overwrite: bool=True) -> pl.Path:
        # Make sure there is some kind of docx to work with or generate
        assert self.docx_path or precontext, "Please provide a precontext or generate a docx first."
        assert isinstance(precontext, dict) or precontext is None, f"Please provide a valid precontext. Received {precontext}."
        assert (isinstance(output_path, pl.Path) and output_path.suffix == ".pdf") or output_path is None, f"Please provide a valid output_path. Received {output_path}."
        assert isinstance(overwrite, bool)
        # precontext given, generate a new docx regardless of whether one exists or not.
        # if precontext:
        #     if output_path:
        #         self.generateDocx( output_path.with_suffix(".docx"), overwrite)
        #     # Else, overwrite
        #     else:
        #         self.generateDocx(precontext, self.docx_path, overwrite)
        # if not output_path:
        #     output_path = self.docx_path.with_suffix(".pdf")

        print("\n")
        logger.info("Converting docx to pdf...")
        try:
            docx2pdf.convert(
                str(self.docx_path),
                str(output_path)
            )
            self.pdf_path = output_path
        except SystemExit as e:
            logger.error(f"[ERROR] {self.docx_path} could not be converted to pdf at {output_path}")
            logger.error(e)
            return pl.Path(config["error_pdf"])
        logger.info(f"[SUCCESS] {self.template_path} converted to {self.pdf_path}")
        return self.pdf_path
    
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self.template_path}, {self.output_dir}, {self.context})"

class CoverGenerator(DocumentGenerator):
    def processContext(self, context:dict) -> dict:
        assert isinstance(context, dict)
        context['logo'] = InlineImage(self.template, context['logo_path'], Cm(10))
        color_keys = ["title", "subsection", "author", "year"]
        for reading in context["core_readings"]:
            reading["title"] = RichText(reading["title"], color=context["color_primary_faded"])
            reading["subsection"] = RichText(f"\n({reading['subsection']})" if reading['subsection'] else "", color=context["color_primary_faded"])
            reading["author_year"] = RichText(f"({reading['author']}, {reading['year']})", color=context["color_primary_faded"])
        return context

class FurtherGenerator(DocumentGenerator):
    def processContext(self, context: dict) -> dict:
        ## Logo
        context['logo'] = InlineImage(self.template, context['logo_path'], Cm(2))

        ## Id, Truncate links, QR codes, and thumbnails to context
        for reading in context['further_readings']:
            url = reading['url']
            id = reading['id'] = makeIDFromTitle(reading['title']) # necessary bc special characters forbidden as file names.
            if url:
                ## Truncate
                scheme = urllib.parse.urlparse(url).scheme
                reading['truncated_url'] = url.replace(scheme + "://", "").replace("www.", "")
                ## Add QR codes
                qr_code_dir = self.output_dir / pl.Path("qr_codes/")
                qr_code_dir.mkdir(parents=True, exist_ok=True)
                qr_code_path = makeQRCode(url, id, output_path=qr_code_dir)
                reading['qr_code'] = InlineImage(self.template, str(qr_code_path), Cm(3))
                ## Add thumbnails if needed
                if not reading["thumbnail_path"]:
                    thumbnail_dir = self.output_dir / pl.Path("thumbnails/") 
                    thumbnail_dir.mkdir(parents=True, exist_ok=True)
                    thumbnail_path = thumbnail_dir / pl.Path(f"{id} thumbnail")
                    thumbnail_path = get_favicon_from_website(url, thumbnail_path)
                    reading["thumbnail_path"] = str(thumbnail_path)
                # reading['thumbnail'] = InlineImage(template, reading["thumbnail_path"], Cm(3), Cm(3)) 
                if reading["thumbnail_path"] and pl.Path(reading["thumbnail_path"]).exists():
                    reading['thumbnail'] = InlineImage(self.template, reading["thumbnail_path"], Cm(3), Cm(3))
        
        return context
    
class GuideGenerator(DocumentGenerator):
    def processContext(self, context: dict) -> dict:
        assert isinstance(context, dict)
        context['logo'] = InlineImage(self.template, context['logo_path'], Cm(10))
        return context
    
#TODO: Make this work
class DeviceReadingGenerator(DocumentGenerator):
    def processContext(self, context: dict) -> dict:
        assert isinstance(context, dict)
        ## Logo
        context['logo'] = InlineImage(self.template, context['logo_path'], Cm(2))

        ## Id, Truncate links, QR codes, and thumbnails to context
        reading = context["device_reading"]
        url = reading['url']
        id = reading['id'] = makeIDFromTitle(reading['title']) # necessary bc special characters forbidden as file names.
        if url:
            ## Truncate
            scheme = urllib.parse.urlparse(url).scheme
            reading['truncated_url'] = url.replace(scheme + "://", "").replace("www.", "")
            ## Add QR codes
            qr_code_dir = self.output_dir / pl.Path("qr_codes/")
            qr_code_dir.mkdir(parents=True, exist_ok=True)
            qr_code_path = makeQRCode(url, id, output_path=qr_code_dir)
            reading['qr_code'] = InlineImage(self.template, str(qr_code_path), Cm(3))
            ## Add thumbnails if needed
            if not reading["thumbnail_path"]:
                thumbnail_dir = self.output_dir / pl.Path("thumbnails/") 
                thumbnail_dir.mkdir(parents=True, exist_ok=True)
                thumbnail_path = thumbnail_dir / pl.Path(f"{id} thumbnail")
                thumbnail_path = get_favicon_from_website(url, thumbnail_path)
                reading["thumbnail_path"] = str(thumbnail_path)
            # reading['thumbnail'] = InlineImage(template, reading["thumbnail_path"], Cm(3), Cm(3)) 
            if reading["thumbnail_path"] and pl.Path(reading["thumbnail_path"]).exists():
                reading['thumbnail'] = InlineImage(self.template, reading["thumbnail_path"], Cm(3), Cm(3))
        
        return context

    