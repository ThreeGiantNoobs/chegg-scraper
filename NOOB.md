# Chegg-Scraper

This scrapper can scrape through [Chegg.com](https://www.chegg.com) and create an html file to save the content locally.
###How To Use ??
First of all, download the latest release from [here](https://github.com/ThreeGiantNoobs/chegg-scraper/releases/latest)

After unzipping, install the requirements by using

    pip install -r requirements.txt 
or

    pip3 install -r requirements.txt

which-ever works depending on your System

The above step is a one time process. Once done move onto the next step.

Now in order to run the file, use

    python Downloader.py 

There are 2 optional arguments

    -url or -u --> To enter the page url
    -cookie or -c --> To enter the cookies file path

Cookies are supported in 2 formats, ``cookie.txt`` or ``cookie.json``
For .txt format, cop