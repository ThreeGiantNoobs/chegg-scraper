import json
import logging
import os
import random
import re
import string
import unicodedata
from importlib.resources import read_text

import requests
from requests import Response
from bs4 import BeautifulSoup
from bs4.element import Tag
from jinja2 import Environment, BaseLoader

from .Exceptions import *

logging.basicConfig(filename='scraper.log', filemode='w', level=logging.DEBUG)

main_template = Environment(loader=BaseLoader).from_string(read_text('cheggscraper', 'template.html'))
chapter_type_template = Environment(loader=BaseLoader).from_string(read_text('cheggscraper', 'chapter_type_frame.html'))


class CheggScraper:
    """
    Scrape html from chegg.com and store them in a way so you don't need cookie to view the file
    """

    def __init__(self, cookie: str = None, cookie_path: str = None, user_agent: str = None, base_path: str = None,
                 save_file_format: str = None, config: dict = None, template_path: str = None,
                 extra_header_tag: str = None):

        self.base_path = base_path

        self.save_file_format = save_file_format

        if self.base_path:
            if not os.path.exists(self.base_path):
                os.makedirs(self.base_path)

        if not self.base_path:
            self.base_path = ''

        self.extra_header_tag = extra_header_tag

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

        logging.debug(msg=f'user_agent: {user_agent}')

        self.user_agent = user_agent

        self.headers = {
            'authority': 'www.chegg.com',
            # 'cache-control': 'max-age=0',
            "Accept-Encoding": "gzip, deflate, br",
            'accept-language': 'en-US,en;q=0.9',
            'cookie': self.cookie,
            'sec-ch-ua': '" Not;A Brand";v="99", "Google Chrome";v="91", "Chromium";v="91"',
            'sec-ch-ua-mobile': '?0',
            'upgrade-insecure-requests': '1',
            'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
            'sec-fetch-site': 'cross-site',
            'sec-fetch-mode': 'navigate',
            'sec-fetch-user': '?1',
            'sec-fetch-dest': 'document',
            'user-agent': self.user_agent,
        }

        self.ajax_url = 'https://www.chegg.com/study/_ajax/enhancedcontent?token={token}&questionUuid={question_uuid}&showOnboarding=&templateName=ENHANCED_CONTENT_V2&deviceFingerPrintId={deviceFingerPrintId}'

        logging.debug(f'self.cookie = {self.cookie}')

        self.deviceFingerPrintId = self.cookie_dict.get('DFID')

    @staticmethod
    def slugify(value: str, allow_unicode: bool = False) -> str:
        """
        slugify the names of files

        :param value: string to be slugify
        :type value: str
        :param allow_unicode: allow unicode
        :type allow_unicode: bool
        :return: string after slugify
        :rtype: str
        """
        value = str(value)
        if allow_unicode:
            value = unicodedata.normalize('NFKC', value)
        else:
            value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('ascii')
        value = re.sub(r'[^\w\s-]', '', value.lower())
        return re.sub(r'[-\s]+', '-', value).strip('-_')

    @staticmethod
    def render_chapter_type_html(data: dict) -> str:
        """
        Render chapter type answers using data

        :param data: response from graphql url
        :type data: dict
        :return: rendered html code
        :rtype: str
        """
        chapter_d = data['data']['textbook_solution']['chapter'][0]
        problem_d = chapter_d['problems'][0]
        solutionV2 = problem_d['solutionV2'][0]

        _data = {
            'chapterName': chapter_d['chapterName'],
            'problemName': problem_d['problemName'],
            'problemHtml': problem_d['problemHtml'],
            'totalSteps': solutionV2['totalSteps'],
            'steps': solutionV2['steps'],
        }

        return chapter_type_template.render(**_data)

    @staticmethod
    def replace_src_links(html_text: str) -> str:
        """
        Replace relative links from page, so even you are opening file without any host, still can see all contents,
        still some css and js won't load

        :param html_text: html code of page
        :type html_text: str
        :return: html code after modify all relative links
        :rtype: str
        """
        return re.sub(r'src=\s*?"//(.*)?"', r'src="https://\1"', html_text)

    @staticmethod
    def cookie_str_to_dict(cookie_str: str) -> dict:
        """
        Convert cookie str to dict of key, value pairs

        :param cookie_str: cookie in format of string [key=value; key=value]
        :type cookie_str: str
        :return: dictionary of key value pairs of key value pairs
        :rtype: dict
        """
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
        """
        just parse json

        :param json_string: json data in format of string
        :type json_string: str
        :return: tuple of isJson, dictionary form of json
        :rtype:
        """
        try:
            data = json.loads(json_string)
            return True, data
        except Exception as e:
            logging.debug(msg=f'::while parsing json: {e}')
            return False, None

    @staticmethod
    def dict_to_cookie_str(cookie_dict: dict) -> str:
        """
        Convert dict to cookie string

        :param cookie_dict: dictionary of cookie, key value pairs
        :type cookie_dict: dict
        :return: cookie in string format
        :rtype: str
        """
        cookie_str = ''
        first_flag = True
        for cookie in cookie_dict:
            if not first_flag:
                cookie_str += '; '
            cookie_str += '{name}={value}'.format(**cookie)
            first_flag = False
        return cookie_str

    @staticmethod
    def parse_cookie(cookie_path: str) -> str:
        """
        Parse cookie from cookie_path

        :param cookie_path: path of cookie file
        :type cookie_path: str
        :return: string cookie
        :rtype: str
        """
        if os.path.exists(cookie_path):
            if os.path.isfile(cookie_path):
                with open(cookie_path, 'r') as f:
                    cookie_text = f.read()
                    json_result = CheggScraper.parse_json(cookie_text)
                    if json_result[0]:
                        return CheggScraper.dict_to_cookie_str(json_result[1]).strip()
                    return cookie_text.strip()
            else:
                logging.error(msg=f"{cookie_path} is not a file")
        else:
            logging.error(msg=f"{cookie_path} don't exist")
        raise CookieFileDoesNotExist(cookie_path)

    @staticmethod
    def clean_url(url: str) -> (bool, str):
        """
        Cleans the url, So no track id goes to url

        @param url: url of chegg webpage
        @type url: str
        @return: Url removed with trackId
        @rtype: (bool, str)
        """
        chapter_type = False
        match = re.search(r'chegg\.com/homework-help/questions-and-answers/([^?/]+)', url)
        if not match:
            chapter_type = True
            match = re.search(r'chegg\.com/homework-help/[^?/]+', url)
            if not match:
                logging.error(f'THIS URL NOT SUPPORTED\nurl: {url}')
                raise UrlNotSupported(url)

        return chapter_type, 'https://www.' + match.group(0)

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

    def _web_response(self, url: str, headers: dict = None, expected_status: tuple = (200,), note: str = None,
                      error_note: str = "Error in request", post: bool = False, data: dict = None,
                      _json=None) -> Response:
        """
        Returns response

        :return: return response from web
        :rtype: Response
        """

        if not headers:
            headers = self.headers
        if post:
            response = requests.post(
                url=url,
                headers=headers,
                json=_json,
                data=data
            )
        else:
            response = requests.get(
                url=url,
                headers=headers)

        if response.status_code not in expected_status:
            logging.error(msg=f'Expected status code {expected_status} but got {response.status_code}\n{error_note}')
            return response
        if note:
            logging.info(msg=note)
        return response

    def _get_response_text(self, url: str, headers: dict = None, expected_status: tuple = (200,),
                           note: str = None, error_note: str = "Error in request") -> str:
        """
        text response from web

        :return: Text response from web
        :rtype: str
        """
        response = self._web_response(url, headers, expected_status, note, error_note)
        return response.text

    def _get_response_dict(self, url: str, headers: dict = None, expected_status: tuple = (200,), note: str = None,
                           error_note: str = "Error in request", post: bool = False, data: dict = None,
                           _json=None) -> dict:
        """
        dict response from web

        :return: json response from web
        :rtype: dict
        """
        response = self._web_response(url, headers, expected_status, note, error_note, post=post, data=data,
                                      _json=_json)
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

        return soup.find('div', {'class': 'question-body-text'})

    def _parse_answer(self, soup: BeautifulSoup, question_uuid: str, html_text: str, url: str,
                      chapter_type: bool = False) -> str:
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

        if chapter_type:
            chapter_id = str(re.search(r'\?id=(\d+).*?isbn', html_text).group(1))
            isbn13 = str(re.search(r'"isbn13":"(\d+)"', html_text).group(1))
            problemId = str(re.search(r'"problemId":"(\d+)"', html_text).group(1))

            query = {
                "query": {
                    "operationName": "getSolutionDetails",
                    "variables": {
                        "isbn13": isbn13,
                        "chapterId": chapter_id,
                        "problemId": problemId
                    }
                },
                "token": token
            }
            graphql_url = 'https://www.chegg.com/study/_ajax/persistquerygraphql'

            res_data = self._get_response_dict(url=graphql_url, post=True, _json=query)
            return self.render_chapter_type_html(res_data)

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
            content_request_url = self.ajax_url.format(question_uuid=question_uuid, token=token,
                                                       deviceFingerPrintId=self.deviceFingerPrintId)
            answers__ = '<div id="enhanced-content"><hr>' + self._get_response_dict(url=content_request_url)[
                'enhancedContentMarkup'] + "</div>"
        else:
            raise FailedToParseAnswer

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
            title = soup.find('title')
            if title:
                heading = title.text

        if not heading:
            logging.error(msg="can't able to get heading")
        else:
            logging.info(msg=f"Heading: {heading}")
        return str(heading)

    def _parse(self, html_text: str, url: str, chapter_type: bool = None) -> (str, str):
        html_text = self.replace_src_links(html_text)
        soup = BeautifulSoup(html_text, 'lxml')
        logging.debug("HTML\n\n" + html_text + "HTML\n\n")

        if soup.find('div', id='px-captcha'):
            raise BotFlagError

        """Parse headers"""
        headers = soup.find('head')

        """Parse heading"""
        heading = self._parse_heading(soup)

        """Parse Question"""
        if not chapter_type:
            _, question_data = self.parse_json(
                re.search(r'C\.page\.homeworkhelp_question\((.*)?\);', html_text).group(1))
        else:
            _ = True
            question_data = None
        logging.debug(msg=str(question_data))
        questionUuid = None
        if _:
            if not chapter_type:
                questionUuid = question_data['question']['questionUuid']
        else:
            raise UnableToParseUUID

        if chapter_type:
            question_div = '<div></div>'
        else:
            question_div = self._parse_question(soup)

        """Parse Answer"""
        answers_div = self._parse_answer(soup, questionUuid, html_text, url, chapter_type=chapter_type)

        return headers, heading, question_div, answers_div, questionUuid

    def _save_html_file(self, rendered_html: str, heading: str = None, question_uuid: str = None,
                        file_name_format: str = None):
        heading = self.slugify(heading.strip('.').strip())
        if not file_name_format:
            file_name_format = self.save_file_format
        if not file_name_format:
            file_name_format = heading + '.html'

        file_path = os.path.join(
            self.base_path,
            file_name_format)

        file_path = file_path.format(**{
            'random_u_str_int': ''.join(random.choices(string.ascii_uppercase + string.digits, k=10)),
            'random_u_str': ''.join(random.choices(string.ascii_uppercase, k=10)),
            'random_str': ''.join(random.choices(string.ascii_letters, k=10)),
            'random_int': ''.join(random.choices(string.digits, k=10)),
            'heading': heading,
            'title': heading,
            'question_uuid': question_uuid
        })

        # if self.save_file_format:
        #     file_path = os.path.join(
        #         file_path,
        #         self.save_file_format)

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(rendered_html)

        return file_path

    def _render_html(self, url, headers, heading, question_div, answers__):
        html_rendered_text = main_template.render(
            url=url,
            headers=headers,
            title=heading,
            heading=heading,
            question_body=question_div,
            answers_wrap=answers__,
            extra_header_tag=self.extra_header_tag,
        )

        return self.final_touch(html_text=html_rendered_text)

    def url_to_html(self, url: str, file_name_format: str = None, get_dict_info: bool = False):
        """
        Chegg url to html file, saves the file and return file path

        @param url: chegg url
        @type url: str
        @param get_dict_info:
        @type get_dict_info:
        @param file_name_format: File path to save file
        @type file_name_format: str
        @return: file_path
        @rtype:
        """
        chapter_type, url = self.clean_url(url)

        html_res_text = self._get_response_text(url=url)

        headers, heading, question_div, answers__, question_uuid = self._parse(html_text=html_res_text,
                                                                               chapter_type=chapter_type, url=url)

        rendered_html = self._render_html(url, headers, heading, question_div, answers__)

        file_path = self._save_html_file(rendered_html, heading, question_uuid, file_name_format)

        if get_dict_info:
            return file_path, url, headers, heading, question_div, answers__
        return file_path
