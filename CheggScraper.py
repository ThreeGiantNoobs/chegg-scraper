import os

import requests
import logging

logging.basicConfig(level=logging.DEBUG)


class CheggScraper(object):

    def __init__(self, cookie: str = None, cookie_path: str = None):
        if cookie:
            self.cookie = cookie
        else:
            self.cookie = self.parse_cookie(cookie_path)
        self.headers = {
            'authority': 'www.chegg.com',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '\\',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36 Edg/91.0.864.37',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': cookie,
        }
        logging.debug(f'self.cookie = {self.cookie}')

    @staticmethod
    def parse_cookie(cookie_path):
        if os.path.exists(cookie_path):
            if os.path.isfile(cookie_path):
                with open('cookie.txt', 'r') as f:
                    return f.read()
            else:
                logging.error(msg=f"{cookie_path} is not a file")
        else:
            logging.error(msg=f"{cookie_path} don't exist")

    def web_response(self, url: str, headers: dict = None, expected_status: tuple = (200,),
                     note: str = None, error_note: str = "Error in request"):
        if not headers:
            headers = self.headers
        response = requests.get(
            url=url,
            headers=headers,
        )
        if response.status_code not in expected_status:
            logging.error(msg=f'Expected status code {expected_status} but got {response.status_code}\n{error_note}')
            return response
        else:
            logging.info(msg=note)
            return response

    def get_response_text(self, url: str, headers: dict = None, expected_status: tuple = (200,),
                          note: str = None, error_note: str = "Error in request"):
        response = self.web_response(url, headers, expected_status, note, error_note)
        return response.text
