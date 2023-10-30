# Spider

This program fetches image URLs from a given webpage. If the recursive mode is activated, it will also scrape images from linked pages within the primary webpage, up to the specified depth. Found images are downloaded and saved to the specified directory.

----

## Requirements

- Python3
- Some dependencies :
  ``pip install -r requirements.txt``

----

## Usage

``python3 spider.py URL [-r] [-l LEVEL] [-p PATH]``

**Arguments:**

- URL: The URL of the website to scrape images from.
- -r, --recursive: Enable recursive download of images from the URL.
- -l, --level: The maximum depth level for recursive download (Default: 5).
- -p, --path: The path where the downloaded files will be saved (Default: ./data/).

----

## Tips and Notes

- Ensure you have the necessary permissions to read from or write to directories.
- If you face any issues with the HTTP request (e.g., 404 error) during image scraping, please verify the provided URL.
- For efficient web scraping, always adhere to the website's robots.txt rules and be mindful of not overloading servers with numerous requests in a short time. You can test the scrapper on this site : https://books.toscrape.com/

----

## Contribute
Feel free to submit pull requests or issues if you find any mistakes or have suggestions for improvements.

----

**Note: Ensure that you follow ethical hacking guidelines. Do not use the knowledge gained here for malicious intentions. Always seek permission before attempting to exploit vulnerabilities in any system.**
