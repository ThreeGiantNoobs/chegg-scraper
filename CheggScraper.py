import os
import json
import re

import requests
import logging

from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)
# logging.basicConfig(level=logging.DEBUG)


class CheggScraper(object):

    def __init__(self, cookie: str = None, cookie_path: str = None):
        if cookie:
            self.cookie = cookie
        else:
            self.cookie = self.parse_cookie(cookie_path)

        self.cookie_dict = self.cookie_str_to_dict(self.cookie)

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
            'cookie': self.cookie,
        }

        logging.debug(f'self.cookie = {self.cookie}')

        self.DFID = self.cookie_dict.get('DFID')

    @staticmethod
    def render_html(**kwargs):

        template_path = kwargs.get('template_path')
        if not template_path:
            template_path = 'template.html'

        with open(template_path, 'r') as f:
            html_template = f.read()

        variables = re.findall(r'\{\{([a-zA-Z_]+)}}', html_template)
        for variable in variables:
            html_template = html_template.replace('{{' + variable + '}}', str(kwargs.get(variable)))
        return html_template

    @staticmethod
    def replace_src_links(html_text):
        return re.sub(r'src=\s*?"//(.*)?"', r'src="https://\1"', html_text)

    @staticmethod
    def cookie_str_to_dict(cookie_str: str):
        ret = {}
        cookie_pairs = cookie_str.split(';')
        for pair in cookie_pairs:
            key, value = pair.split('=', 1)
            key = key.strip()
            value = value.strip()
            ret.update({key: value})
        return ret

    @staticmethod
    def parse_json(json_string: str) -> (bool, dict):
        try:
            data = json.loads(json_string)
            return True, data
        except Exception as e:
            return False, None

    @staticmethod
    def json_to_cookie_str(cookie_dict: dict):
        cookie_str = ''
        first_flag = True
        for cookie in cookie_dict:
            if not first_flag:
                cookie_str += '; '
            cookie_str += '{name}={value}'.format(**cookie)
            first_flag = False
        return cookie_str

    @staticmethod
    def parse_cookie(cookie_path):
        if os.path.exists(cookie_path):
            if os.path.isfile(cookie_path):
                with open(cookie_path, 'r') as f:
                    cookie_text = f.read()
                    json_result = CheggScraper.parse_json(cookie_text)
                    if json_result[0]:
                        return CheggScraper.json_to_cookie_str(json_result[1]).strip()
                    else:
                        return cookie_text.strip()
            else:
                logging.error(msg=f"{cookie_path} is not a file")
                raise Exception
        else:
            logging.error(msg=f"{cookie_path} don't exist")
            raise Exception

    def final_touch(self, html_text):
        soup = BeautifulSoup(html_text, 'lxml')
        if soup.find('div', {'id': 'show-more'}):
            soup.find('div', {'id': 'show-more'}).decompose()
        if soup.find('section', {'id': 'general-guidance'}):
            soup.find('section', {'id': 'general-guidance'})['class'] = 'viewable visible'

        return str(soup)

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
            if note:
                logging.info(msg=note)
            return response

    def get_response_text(self, url: str, headers: dict = None, expected_status: tuple = (200,),
                          note: str = None, error_note: str = "Error in request"):
        response = self.web_response(url, headers, expected_status, note, error_note)
        return response.text

    def get_response_dict(self, url: str, headers: dict = None, expected_status: tuple = (200,),
                          note: str = None, error_note: str = "Error in request"):
        response = self.web_response(url, headers, expected_status, note, error_note)
        return response.json()

    def cookie_to_dict(self, c):
        ...

    def _parse(self, html_text):
        html_text = self.replace_src_links(html_text)
        soup = BeautifulSoup(html_text, 'lxml')
        token = re.search(r'"token":"(.+?)"', html_text).group(1)
        print(html_text)
        to_load_enhanced_content = False
        if soup.find('div', {'id': 'enhanced-content'}).find('div', {'class': 'chg-load'}):
            to_load_enhanced_content = True

        """Parse headers"""
        headers = soup.find('head')

        """Parse heading"""
        heading = None
        heading_tag = soup.find('span', _class='question-text')
        if heading_tag:
            heading = heading_tag.text
        if not heading:
            meta_description = soup.find('meta', {'name': 'description'})
            if meta_description:
                heading = meta_description.get('content')
        if not heading:
            logging.error(msg="can't able to get heading")
        else:
            logging.info(msg=f"Heading: {heading}")

        """Parse Question"""
        """Type1: class = ugc-base question-body-text"""

        # question_data = None
        # _question_data = None
        # __question_data = re.search(
        #     r'window.__QUESTION_DATA__ = (\{.+})?;',
        #     html_text)
        #
        # if __question_data:
        #     _question_data = __question_data.group(1)
        #
        # json_result = self.parse_json(_question_data)
        # if json_result[0]:
        #     question_data = json_result[1]
        #
        # if not question_data:
        #     logging.error(msg="can't able to get question")
        #     raise Exception("can't able to parse question, ERROR")

        question_div = soup.find('div', {'class': 'question-body-text'})
        if question_div:
            # question type 1:
            ...
        # TODO: ADD SUPPORT FOR ALL TYPES QUESTION

        """Parse Answer"""
        # answers_list_ul = soup.find('ul', {'class': 'answers-list'})
        _, question_data = self.parse_json(re.search(r'C.page.homeworkhelp_question\((.*)?\);', html_text).group(1))

        questionUuid = question_data['question']['questionUuid']
        answers_list_li = soup.findAll('div', {'class': 'answer-given-body'})
        if answers_list_li:
            _s_ = [str(x) for x in answers_list_li]
            answers__ = '<ul class="answers-list">' + "".join(_s_) + "</ul>"
        elif to_load_enhanced_content:
            content_request_url = f"https://www.chegg.com/study/_ajax/enhancedcontent?token={token}&questionUuid={questionUuid}&showOnboarding=&templateName=ENHANCED_CONTENT_V2&deviceFingerPrintId={self.DFID}"
            answers__ = '<div id="enhanced-content"><hr>' + self.get_response_dict(url=content_request_url)['enhancedContentMarkup'] + "</div>"
        else:
            raise Exception

        response = self.render_html(
            headers=headers,
            title=heading,
            heading=heading,
            question_body=question_div,
            answers_wrap=answers__
        )

        response = self.final_touch(html_text=response)

        with open(f'{heading}.html', 'w', encoding='utf-8') as f:
            f.write(response)
        return response


if __name__ == '__main__':
    pass
    # print()

