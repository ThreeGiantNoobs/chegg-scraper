import argparse
from CheggScraper import CheggScraper

ap = argparse.ArgumentParser()
ap.add_argument('-c', '--cookie', default='cookie.txt',
                help='path of cookie life', dest='cookie_file')
ap.add_argument('-u', '--url', required=True, help='url of chegg homework-help, put inside " "',
                type=str, dest='url')
args = vars(ap.parse_args())


if __name__ == '__main__':
    Chegg = CheggScraper(cookie_path=args['cookie_file'])