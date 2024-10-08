from pathlib import Path
import urllib.parse

import requests
from bs4 import BeautifulSoup, Tag
from PIL import Image

def _get_favicon_url(base_url: str, soup: BeautifulSoup) -> str | None:
    """
    Extracts the favicon URL from a BeautifulSoup object.

    This function searches for favicon links in the HTML, first looking for
    a link with rel="icon", then rel="shortcut icon". If no favicon is found,
    it defaults to "/favicon.ico".

    :param str base_url: The base URL of the website being scraped.
    :param BeautifulSoup soup: A BeautifulSoup object representing the parsed HTML.
    :return str | None: The absolute URL of the favicon, or None if not found.
    """
    # Find the favicon link in the HTML
    favicon_url = None

    # Look for a favicon link with rel="icon"
    icon_link = soup.find("link", rel="icon")
    if icon_link and isinstance(icon_link, Tag):
        favicon_url = icon_link.get("href")

    # If not found, look for a favicon link with rel="shortcut icon"
    if not favicon_url:
        icon_link = soup.find("link", rel="shortcut icon")
        if icon_link and isinstance(icon_link, Tag):
            favicon_url = icon_link.get("href")

    # If still not found, return a default favicon URL
    if not favicon_url:
        favicon_url = "/favicon.ico"
    # Make sure the favicon URL is absolute
    favicon_url = urllib.parse.urljoin(base_url, str(favicon_url))

    return favicon_url

def _download_favicon(favicon_url: str, output_path: Path) -> Path | None:
    try:
        # Send a GET request to the favicon URL
        response = requests.get(favicon_url)

        # Check if the request was successful
        if response.status_code == 200:
            # Save the favicon as a .ico file and png
            ico_path = f"{output_path}.ico"
            with open(ico_path, "wb") as f:
                f.write(response.content)
            Image.open(ico_path).save(f"{output_path}.png")
        else:
            print("Failed to retrieve favicon. Status code:", response.status_code)
    except Exception as e:
        print("An error occurred:", str(e))


def get_favicon_from_website(url, output_path: Path = Path("./")) -> Path | None:
    assert isinstance(output_path, Path)
    output_path = Path(output_path)  # todo: use Path instead lol
    try:
        # Send a GET request to the website
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Get the base URL
            base_url = (
                urllib.parse.urlparse(url).scheme
                + "://"
                + urllib.parse.urlparse(url).hostname
            )

            # Get the favicon URL
            favicon_url = _get_favicon_url(base_url, soup)
            # Download the favicon
            if favicon_url:
                _download_favicon(favicon_url, output_path)
                return output_path.with_suffix(".png")
            else:
                print("No favicon URL found.")
                return None
        else:
            print("Failed to retrieve website. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))


# Example usage:
if __name__ == "__main__":
    website_url = "https://support.apple.com/guide/mac-help/use-your-ipad-as-a-second-display-mchlf3c6f7ae/mac"
    output_path = Path("./favicon_output/test.ico")
    get_favicon_from_website(website_url, output_path)