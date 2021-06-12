import argparse
import json

from CheggScraper import CheggScraper

with open('conf.json', 'r') as f:
    conf = json.load(f)

default_save_file_path = conf.get('default_save_file_path')
default_cookie_file_path = conf.get('default_cookie_file_path')

ap = argparse.ArgumentParser()
ap.add_argument('-c', '--cookie', default=default_cookie_file_path,
                help='path of cookie life', dest='cookie_file')
ap.add_argument('-u', '--url', help='url of chegg homework-help, put inside " "',
                type=str, dest='url')
ap.add_argument('-s', '--save', help='file path, where you want to save, put inside " " eg: test.html or D:\\myFolder\\test.html or /home/test.html',
                type=str, default=default_save_file_path, dest='file_path')
args = vars(ap.parse_args())


if __name__ == '__main__':
    if not args.get('url'):
        args.update({'url': input('Enter url of the homework-help: ')})

    Chegg = CheggScraper(cookie_path=args['cookie_file'])
    print(Chegg.url_to_html(args['url'], file_path=args['file_path']))
