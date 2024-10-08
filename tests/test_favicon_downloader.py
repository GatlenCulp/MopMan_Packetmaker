import pytest
from pathlib import Path
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup

from src.favicon_downloader import get_favicon_url, download_favicon, get_favicon_from_website

@pytest.fixture
def mock_soup():
    html = """
    <html>
    <head>
        <link rel="icon" href="/favicon.ico">
    </head>
    </html>
    """
    return BeautifulSoup(html, 'html.parser')

def test_get_favicon_url(mock_soup):
    base_url = "https://example.com"
    favicon_url = get_favicon_url(base_url, mock_soup)
    assert favicon_url == "https://example.com/favicon.ico"

@patch('requests.get')
def test_download_favicon(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.content = b'fake_image_content'
    mock_get.return_value = mock_response

    with patch('builtins.open', create=True) as mock_open, \
         patch('PIL.Image.open') as mock_image_open:
        mock_image = MagicMock()
        mock_image_open.return_value = mock_image

        output_path = Path("./test_favicon")
        download_favicon("https://example.com/favicon.ico", output_path)

        mock_open.assert_called_with(f"{output_path}.ico", "wb")
        mock_image.save.assert_called_with(f"{output_path}.png")

@patch('requests.get')
@patch('src.favicon_downloader.BeautifulSoup')
@patch('src.favicon_downloader.download_favicon')
def test_get_favicon_from_website(mock_download_favicon, mock_bs, mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = "<html></html>"
    mock_get.return_value = mock_response

    mock_soup = MagicMock()
    mock_bs.return_value = mock_soup

    with patch('src.favicon_downloader.get_favicon_url') as mock_get_favicon_url:
        mock_get_favicon_url.return_value = "https://example.com/favicon.ico"
        
        url = "https://example.com"
        output_path = Path("./test_favicon")
        result = get_favicon_from_website(url, output_path)

        assert result == output_path.with_suffix(".png")
        mock_download_favicon.assert_called_once_with("https://example.com/favicon.ico", output_path)

if __name__ == "__main__":
    pytest.main()