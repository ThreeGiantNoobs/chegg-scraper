import os
import re
import json
from contextlib import redirect_stderr

import requests
import logging
import unicodedata
from importlib.resources import read_text

from bs4 import BeautifulSoup
from bs4.element import Tag

logging.basicConfig(filename='scraper.log', filemode='w', level=logging.DEBUG)


class CheggScraper(object):
    def __init__(self, cookie: str = None, cookie_path: str = None, user_agent: str = None, base_path: str = None,
                 save_file_path: str = None, config: dict = None, template_path: str = None):
        if cookie:
            self.cookie = cookie
        else:
            self.cookie = self.parse_cookie(cookie_path)

        self.cookie_dict = self.cookie_str_to_dict(self.cookie)

        self.template_path = template_path

        if not config:
            config = json.loads(read_text('cheggscraper', 'conf.json'))

        if not user_agent:
            user_agent = config.get('user_agent')
        if not user_agent:
            raise Exception('user_agent not defined')

        if not base_path:
            self.base_path = config.get('base_path')

        if not self.base_path:
            self.base_path = ''

        logging.debug(msg=f'user_agent: {user_agent}')
        if not user_agent:
            raise Exception('user_agent is None')

        self.headers = {
            'authority': 'www.chegg.com',
            'cache-control': 'max-age=0',
            'sec-ch-ua': '\\',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'user-agent': user_agent,
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'none',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'accept-language': 'en-US,en;q=0.9',
            'cookie': self.cookie,
        }

        self.ajax_url = 'https://www.chegg.com/study/_ajax/enhancedcontent?token={token}&questionUuid={question_uuid}&showOnboarding=&templateName=ENHANCED_CONTENT_V2&deviceFingerPrintId={deviceFingerPrintId}'

        logging.debug(f'self.cookie = {self.cookie}')

        self.deviceFingerPrintId = self.cookie_dict.get('DFID')

    @staticmethod
    def slugify(value, allow_unicode=False):
        value = str(value)
        if allow_unicode:
            value = unicodedata.normalize('NFKC', value)
        else:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value.lower())
        return re.sub(r'[-\s]+', '-', value).strip('-_')

    def render_html(self, **kwargs):

        template_path = kwargs.get('template_path')
        html_template = None
        if not template_path:
            template_path = self.template_path

        if not template_path:
            html_template = read_text('cheggscraper', 'template.html')

        if not html_template:
            with open(template_path, 'r') as f:
                html_template = f.read()


        variables = re.findall(r'\{\{([a-zA-Z_]+)}}', html_template)
        for variable in variables:
            html_template = html_template.replace('{{' + variable + '}}', str(kwargs.get(variable)))
        return html_template

    @staticmethod
    def replace_src_links(html_text: str):
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
            logging.critical(msg=f'while parsing json: {e}')
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
    def parse_cookie(cookie_path: str):
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

    @staticmethod
    def clean_url(url: str) -> str:
        """
        Cleans the url, So no track id goes to url

        @param url: url of chegg webpage
        @type url: str
        @return: Url removed with trackId
        @rtype: str
        """
        match = re.search(r'chegg\.com/homework-help/questions-and-answers/[^?/]+', url)
        if not match:
            logging.error(f'THIS URL NOT SUPPORTED\nurl: {url}')
            raise Exception(f'THIS URL NOT SUPPORTED\nurl: {url}')
        return 'https://www.' + match.group(0)

    @staticmethod
    def final_touch(html_text: str) -> str:
        """
        Final changes to final html code, like changing class of some divs

        @param html_text: html text
        @type html_text: str
        @return: modified FINAL html Text
        @rtype: str
        """

        soup = BeautifulSoup(html_text, 'lxml')
        if soup.find('div', {'id': 'show-more'}):
            soup.find('div', {'id': 'show-more'}).decompose()
        if soup.find('section', {'id': 'general-guidance'}):
            soup.find('section', {'id': 'general-guidance'})['class'] = 'viewable visible'

        return str(soup)

    def _web_response(self, url: str, headers: dict = None, expected_status: tuple = (200,),
                      note: str = None, error_note: str = "Error in request"):
        if not headers:
            headers = self.headers
        response = requests.get(
            url=url,
            headers=headers)

        if response.status_code not in expected_status:
            logging.error(msg=f'Expected status code {expected_status} but got {response.status_code}\n{error_note}')
            return response
        else:
            if note:
                logging.info(msg=note)
            return response

    def _get_response_text(self, url: str, headers: dict = None, expected_status: tuple = (200,),
                           note: str = None, error_note: str = "Error in request"):
        response = self._web_response(url, headers, expected_status, note, error_note)
        return response.text

    def _get_response_dict(self, url: str, headers: dict = None, expected_status: tuple = (200,),
                           note: str = None, error_note: str = "Error in request"):
        response = self._web_response(url, headers, expected_status, note, error_note)
        return response.json()

    @staticmethod
    def _parse_question(soup: BeautifulSoup) -> Tag:
        """
        Simply parse question

        @param soup: BeautifulSoup from chegg_html
        @type soup: BeautifulSoup
        @return: div containing question
        @rtype: Tag
        """
        # # This Parse Question If not Login
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

        return soup.find('div', {'class': 'question-body-text'})

    def _parse_answer(self, soup: BeautifulSoup, question_uuid: str, html_text: str) -> str:
        """
        Parse Answers as a div from soup

        @param soup: BeautifulSoup from chegg_html
        @type soup: BeautifulSoup
        @param question_uuid: unique question id
        @type question_uuid: str
        @param html_text: chegg response text
        @type html_text: str
        @return: Div Containing div
        @rtype: str
        """
        token = re.search(r'"token":"(.+?)"', html_text).group(1)

        to_load_enhanced_content = False
        enhanced_content_div = soup.find('div', {'id': 'enhanced-content'})
        if enhanced_content_div:
            if enhanced_content_div.find('div', {'class': 'chg-load'}):
                to_load_enhanced_content = True

        answers_list_li = soup.findAll('div', {'class': 'answer-given-body'})
        if answers_list_li:
            _s_ = [str(x) for x in answers_list_li]
            answers__ = '<ul class="answers-list">' + "".join(_s_) + "</ul>"
        elif to_load_enhanced_content:
            content_request_url = self.ajax_url.format(question_uuid=question_uuid, token=token, deviceFingerPrintId=self.deviceFingerPrintId)
            answers__ = '<div id="enhanced-content"><hr>' + self._get_response_dict(url=content_request_url)['enhancedContentMarkup'] + "</div>"
        else:
            raise Exception

        return answers__

    @staticmethod
    def _parse_heading(soup: BeautifulSoup) -> str:
        """
        Parse heading from html

        @param soup: BeautifulSoup from chegg_html
        @type soup: BeautifulSoup
        @return: heading of the question page
        @rtype: str
        """
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
        return str(heading)

    def _parse(self, html_text: str) -> (str, str):
        html_text = self.replace_src_links(html_text)
        soup = BeautifulSoup(html_text, 'lxml')
        logging.debug("HTML\n\n" + html_text + "HTML\n\n")

        """Parse headers"""
        headers = soup.find('head')

        """Parse heading"""
        heading = self._parse_heading(soup)

        """Parse Question"""
        _, question_data = self.parse_json(re.search(r'C\.page\.homeworkhelp_question\((.*)?\);', html_text).group(1))
        logging.debug(msg=str(question_data))
        if _:
            questionUuid = question_data['question']['questionUuid']
        else:
            raise Exception('Unable to get question uuid')
        
        question_div = self._parse_question(soup)

        """Parse Answer"""
        answers_div = self._parse_answer(soup, questionUuid, html_text)

        return headers, heading, question_div, answers_div, questionUuid

    def url_to_html(self, url: str, file_path: str = None) -> str:
        """
        Chegg url to html file, saves the file and return file path

        @param url: chegg url
        @type url: str
        @param file_path: File path to save file
        @type file_path: str
        @return: file_path
        @rtype: str
        """
        url = self.clean_url(url)

        html_res_text = self._get_response_text(url=url)

        headers, heading, question_div, answers__, question_uuid = self._parse(html_text=html_res_text)

        html_rendered_text = self.render_html(
            headers=headers,
            title=heading,
            heading=heading,
            question_body=question_div,
            answers_wrap=answers__
        )

        final_html = self.final_touch(html_text=html_rendered_text)

        heading = self.slugify(heading.strip('.').strip())
        if not file_path:
            file_path = heading + '.html'

        file_path = os.path.join(
            self.base_path,
            file_path)

        file_path = file_path.format(**{
            'heading': heading,
            'title': heading,
            'question_uuid': question_uuid
        })

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(final_html)

        return file_path


if __name__ == '__main__':
    pass
