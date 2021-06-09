import requests
import traceback
import pdfkit
from bs4 import BeautifulSoup as soup

with open("cookie.txt", 'r') as f:
    headers = {
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
        'cookie': f.read(),
    }

url = "https://www.chegg.com/homework-help/questions-and-answers/question--choose-random-questions-answer-possible-least-5-questions--thank-q8125333"
url = "https://www.chegg.com/homework-help/questions-and-answers/linearlistjava-import-javautilarrays-public-class-linearlist-implements-linearlistadt--ins-q45798409"
url = "https://www.chegg.com/homework-help/questions-and-answers/random-variable-x-known-uniformly-distributed-10-15-following-graphs-accurately-represents-q7574073"
res = requests.get(url=url, headers=headers)

print(res)
breaked = res.text.split("\n")
try:
    del breaked[
        breaked.index('<div class="chgg-hdr force-desktop kit-kat-search  type-study subtype- ">'):breaked.index(
            '    <div class="chgg-hdr-kitkat-screenblocker"></div> ') + 2]
except ValueError:
    pass
try:
    del breaked[breaked.index('	<div class="comment-entry-wrap">'): breaked.index(
        '		<button class="btn-secondary-mini" type="button" href="#">Post comment</button>') + 2]
except ValueError:
    pass
try:
    del breaked[breaked.index('    <div class="chg-footer"  >'): breaked.index(
        '            <p>&#169; 2003-2021 Chegg Inc. All rights reserved.</p>') + 4]
except ValueError:
    pass
for i in range(len(breaked)):
    try:
        boom = breaked[i]
        if boom.__contains__("<script"):
            while not (boom.__contains__("</script>")):
                breaked.pop(i)
                boom = breaked[i]
            breaked.pop(i)
        if boom.__contains__('<nav class="chgg-menu split-nav hidden ">'):
            while not (boom.__contains__("</nav>")):
                breaked.pop(i)
                boom = breaked[i]
            breaked.pop(i)
        if boom.__contains__("<a"):
            while not (boom.__contains__("</a>")):
                breaked.pop(i)
                boom = breaked[i]
            breaked.pop(i)
        if boom.__contains__("js"):
            breaked.pop(i)
    except:
        traceback.print_exc()
        break

with open("test31.html", 'w') as f:
    breaked = list(
        "\n".join(breaked).replace('"//', '"https://').replace("<script", "<!--").replace("</script>", "-->"))
    for i in breaked:
        try:
            f.write(i)
        except UnicodeEncodeError:
            pass

print("yeet")

sp = soup(res.text, 'html.parser')
answer = sp.find("ul", {"class": "answers-list"})
# options = {
#          'margin-top': '0.25in',
#          'margin-right': '0.25in',
#          'margin-bottom': '0.25in',
#          'margin-left': '0.25in',
#     }

pdfkit.from_file('test31.html', 'out.pdf')
print(answer)
