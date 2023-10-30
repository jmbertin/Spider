import os
import sys
from urllib.parse import urljoin
from bs4 import BeautifulSoup, MarkupResemblesLocatorWarning
import requests
from urllib.parse import urlparse
import argparse
from tqdm import tqdm
import warnings

warnings.filterwarnings("ignore", category=MarkupResemblesLocatorWarning)

visited_urls = set()
downloaded_images = set()

def fetch_image_urls(url, max_depth, current_depth=0, image_count=0, link_count=0):
    """
    Recursively fetches image URLs from a given webpage and its linked webpages up to the specified depth.
    Parameters: url (str):                     The URL of the webpage to scrape image URLs from.
                max_depth (int):               The maximum depth to scrape. A depth of 0 will only scrape the specified URL.
                current_depth (int, optional): The current depth of the scraping. Default is 0.
                image_count (int, optional):   The current count of found images. Used for recursive calls. Default is 0.
                link_count (int, optional):    The current count of found links. Used for recursive calls. Default is 0.
    Returns:    list of str: A list of image URLs found.
                int:         The total count of images found.
                int:         The total count of links found.
    Raises:     requests.exceptions.RequestException: If there is a problem with the HTTP request, such as a 404 error.
    """
    if current_depth > max_depth:
        return [], image_count, link_count

    if url in visited_urls:
        return [], image_count, link_count

    visited_urls.add(url)

    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        return [], image_count, link_count

    content = response.content.decode(response.encoding)
    soup = BeautifulSoup(content, 'html.parser')

    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp'}
    image_urls = []

    for img in soup.find_all('img'):
        if any(img.get('src', '').endswith(ext) for ext in image_extensions) and \
                urlparse(img.get('src', '')).hostname in {None, urlparse(url).hostname}:
            image_url = urljoin(url, img['src'])
            image_urls.append(image_url)
            image_count += 1

    link_urls = []

    if current_depth < max_depth:
        for a in soup.find_all('a', href=True):
            if urlparse(a.get('href', '')).hostname in {None, urlparse(url).hostname}:
                link_url = urljoin(url, a['href'])
                if link_url not in visited_urls:
                    link_urls.append(link_url)
                    link_count += 1

        for link_url in link_urls:
            new_image_urls, image_count, link_count = fetch_image_urls(link_url, max_depth, current_depth+1, image_count, link_count)
            image_urls.extend(new_image_urls)

    print(f"\rAnalysing source at depth {current_depth}: Found images: {image_count}, Found links: {link_count}", end='', flush=True)

    return image_urls, image_count, link_count

def download_images(image_urls, path):
    """
    Downloads images from a list of URLs and saves them to a specified directory.
    Parameters: image_urls (list of str): A list of URLs to download images from.
    path (str): The directory where the images should be saved.
    Returns:    None
    Raises:     requests.exceptions.RequestException: If there is a problem with the HTTP request, such as a 404 error.
    """
    os.makedirs(path, exist_ok=True)
    unique_image_urls = set(image_urls)

    print()
    print(f"Found {len(unique_image_urls)} unique images.")
    print("Downloading images...")
    for image_url in tqdm(unique_image_urls, unit="file"):
        if image_url in downloaded_images:
            continue
        image_name = os.path.basename(image_url)
        image_path = os.path.join(path, image_name)

        try:
            response = requests.get(image_url)
            response.raise_for_status()

            with open(image_path, 'wb') as f:
                f.write(response.content)
        except requests.exceptions.RequestException as e:
            print(f"Failed to download {image_url}: {e}")

def verify_path(path):
    """
    Verifies that a specified path exists and is writable. Creates the directory if it does not exist.
    Parameters: path (str): The path to verify.
    Returns:    None
    Raises:     PermissionError: If the script does not have permission to write to the specified directory.
    SystemExit: If there is a problem with the path, the script will exit.
    """
    if not os.path.exists(path):
        try:
            os.makedirs(path)
        except PermissionError:
            print(f"Permission denied: Cannot create directory '{path}'.")
            sys.exit(1)
    else:
        if not os.access(path, os.W_OK):
            print(f"Permission denied: Cannot write to directory '{path}'.")
            sys.exit(1)

def main():
    """
    Parses command-line arguments and initiates the image scraping and downloading process.
    Returns: None
    """
    parser = argparse.ArgumentParser(description="A spider program to download images from a website recursively.")
    parser.add_argument("URL", help="The URL of the website to scrape images from.")
    parser.add_argument("-r", "--recursive", action="store_true", help="Recursively download images from the URL.")
    parser.add_argument("-l", "--level", type=int, default=5, help="The maximum depth level for recursive download. Default is 5.")
    parser.add_argument("-p", "--path", default="./data/", help="The path where the downloaded files will be saved. Default is './data/'.")
    args = parser.parse_args()

    verify_path(args.path)
    image_urls, image_count, link_count = fetch_image_urls(args.URL, args.level if args.recursive else 0)
    download_images(image_urls, args.path)

if __name__ == "__main__":
    main()
