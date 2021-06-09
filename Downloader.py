import argparse
from CheggScraper import CheggScraper

ap = argparse.ArgumentParser()
ap.add_argument('-c', '--cookie', default='cookie.txt',
                help='path of cookie life', dest='cookie_file')
ap.add_argument('-u', '--url', help='url of chegg homework-help, put inside " "',
                type=str, dest='url')
args = vars(ap.parse_args())


if __name__ == '__main__':
    # if args.get('cookie_file') == 'cookie.txt':
    #     print('Cookie file as cookie.txt')
    if not args.get('url'):
        args.update({'url': input('Enter url of the homework-help: ')})

    Chegg = CheggScraper(cookie_path=args['cookie_file'])
    # print(Chegg.download_to_pdf2(url=args['url']))
    Chegg._parse(Chegg.get_response_text(args['url']))
