# Chegg-Scraper

This scrapper can scrape through [Chegg.com](https://www.chegg.com) and create an html file to save the content locally.
The repository can be used in Chegg-Scraping Bots or for downloading the webpage.

### How To Use ??
First, download the latest release from [here](https://github.com/ThreeGiantNoobs/chegg-scraper/releases/latest)

After unzipping, install the requirements by using

    pip install -r requirements.txt 
or

    pip3 install -r requirements.txt

whatever works depending on your System

The above step is a one time process, once done move onto the next step.

Now in order to run the file, use-

    python Downloader.py 

There are 2 optional arguments

    --url or -u --> To enter the page url
    --cookie or -c --> To enter the cookies file path

Cookies are supported in ``cookie.txt`` format.
Copy the cookie from `document.cookies` from the Browser console or you may use a browser extension like [EditThisCookie](https://chrome.google.com/webstore/detail/editthiscookie/fngmhnnpilhplaeedifhccceomclgfbg)

Once the cookie file is made, You need to add the cookie file in the project folder to save yourself from the `-c` argument or use `-c` argument to provide cookie path to the downloader before each run.

#### Example for Usage

    python Downloader.py -c path/to/the/cookie/file.txt -u "https://chegg.com/using-chegg-scraper"
If the cookie is saved as cookie.txt or cookie.json in the project folder you can run the following as:

    python Downloader.py -u "https://chegg.com/using-chegg-scraper"

For Help, use:

    python Downloader.py -h
