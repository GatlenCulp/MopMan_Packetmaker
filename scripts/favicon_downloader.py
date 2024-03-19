import requests
from bs4 import BeautifulSoup
import urllib.parse
from PIL import Image
import pathlib as pl

def get_favicon_url(base_url, soup):
    # Find the favicon link in the HTML
    favicon_url = None

    # Look for a favicon link with rel="icon"
    icon_link = soup.find("link", rel="icon")
    if icon_link:
        favicon_url = icon_link.get("href")

    # If not found, look for a favicon link with rel="shortcut icon"
    if not favicon_url:
        icon_link = soup.find("link", rel="shortcut icon")
        if icon_link:
            favicon_url = icon_link.get("href")

    # If still not found, return a default favicon URL
    if not favicon_url:
        favicon_url = "/favicon.ico"

    # Make sure the favicon URL is absolute
    favicon_url = urllib.parse.urljoin(base_url, favicon_url)

    return favicon_url

def download_favicon(favicon_url, output_path):
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

def get_favicon_from_website(url, output_path:pl.Path=pl.Path("./")) -> pl.Path:
    assert isinstance(output_path, pl.Path)
    output_path = pl.Path(output_path) # todo: use pl.Path instead lol
    try:
        # Send a GET request to the website
        response = requests.get(url)

        # Check if the request was successful
        if response.status_code == 200:
            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")

            # Get the base URL
            base_url = urllib.parse.urlparse(url).scheme + "://" + urllib.parse.urlparse(url).hostname

            # Get the favicon URL
            favicon_url = get_favicon_url(base_url, soup)

            # Download the favicon
            download_favicon(favicon_url, output_path)
            return f"{output_path}.png"
        else:
            print("Failed to retrieve website. Status code:", response.status_code)
            return None
    except Exception as e:
        print("An error occurred:", str(e))

# Example usage:
if __name__ == "__main__":
    website_url = "https://support.apple.com/guide/mac-help/use-your-ipad-as-a-second-display-mchlf3c6f7ae/mac"
    output_path = "./favicon_output/test.ico"
    get_favicon_from_website(website_url, output_path)
