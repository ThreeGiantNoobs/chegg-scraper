import argparse
import re

from CheggScraper import CheggScraper

ap = argparse.ArgumentParser()
ap.add_argument('-c', '--cookie', default='cookie.txt',
                help='path of cookie life', dest='cookie_file')
ap.add_argument('-u', '--url', help='url of chegg homework-help, put inside " "',
                type=str, dest='url')
args = vars(ap.parse_args())


if __name__ == '__main__':
    if not args.get('url'):
        args.update({'url': input('Enter url of the homework-help: ')})

    Chegg = CheggScraper(cookie_path=args['cookie_file'])
    # print(Chegg.download_to_pdf2(url=args['url']))
    print(Chegg.url_to_html(args['url']))
