import json
import requests
from flask import Flask
from bs4 import BeautifulSoup

app = Flask(__name__)
linux_url = "https://www.linux.org.ru"


class Article(object):
    title = None
    author = None
    date = None
    text = None
    tags = None
    url = None
    source = None
    mini_text = None
    comments = None

    def __init__(self, title, author, date, text, mini_text, tags, url, source, comments):
        self.title = title
        self.author = author
        self.date = date
        self.text = text
        self.tags = tags
        self.url = url
        self.source = source
        self.mini_text = mini_text
        self.comments = comments


class Comment(object):
    author = None
    date = None
    title = None
    text = None
    article_title = None

    def __init__(self, author, date, title, text, article_title):
        self.title = title
        self.author = author
        self.date = date
        self.text = text
        self.article_title = article_title


@app.route('/article/<section>/<id>')
def article(section, id):
    html = get_html(linux_url + "/news/" + str(section) + "/" + str(id))
    articlu = html.select_one(".messages")

    article_title = articlu.select_one("h1").select_one("a").get_text()

    article_tags = ";".join([tag.get_text() for tag in articlu.select_one(".tags").select("a")])

    article_source = \
        [value for value in articlu.select_one('div[itemprop="articleBody"]').contents if value != "\n"][-1].select_one(
            "a")["href"]
    article_url = "/news/" + str(section) + "/" + str(id)

    article_text = "".join(
        [str(value) for value in articlu.select_one('div[itemprop="articleBody"]').contents if value != "\n"][:-1])
    article_mini_text = "".join(
        [value.get_text() for value in articlu.select_one('div[itemprop="articleBody"]').contents if value != "\n"][
        :-1])
    if "читать дальше..." in article_text and (
            len(article_text) < 210 or article_text.find("читать дальше...") < 210):
        article_text_length = article_text.find("читать дальше...") - 4
    else:
        if len(article_text) < 210:
            article_text_length = len(article_text) - 11
        else:
            article_text_length = 180
    article_mini_text = article_mini_text[:article_text_length] + "..."

    article_author = articlu.select_one('a[itemprop="creator"]').get_text()

    article_date = articlu.select_one('time[itemprop="datePublished"]').get_text() if len(
        articlu.select('time[itemprop="datePublished"]')) > 0 else articlu.select_one(
        'time[itemprop="dateCreated"]').get_text()

    article_comments_urls = [linux_url + "/news/" + str(section) + "/" + str(id) + "/page0#comments"] \
                            + [linux_url + url["href"] for url in
                               articlu.select_one(".comment").select_one(".page-number").find_next_siblings("a")[:-1]] \
        if articlu.select_one(".comment").select_one(".page-number") != None \
        else [linux_url + "/news/" + str(section) + "/" + str(id) + "/page0#comments"]

    article_comments = []
    for comments_url in article_comments_urls:
        comments_from_page = get_html(comments_url).select('article[itemprop="comment"]')

        for comment_from_page in comments_from_page:
            comment_article_title = article_title

            comment_title = comment_from_page.select_one(".title").get_text()

            comment_author = comment_from_page.select_one(".sign").select_one("a").get_text() if len(
                comment_from_page.select_one(".sign").select("a")) != 0 else "anonymous"

            comment_date = comment_from_page.select_one('time[itemprop="commentTime"]').get_text()

            comment_text = [str(value).replace("\n", "") for value in
                            comment_from_page.select_one(".msg_body.message-w-userpic").contents[:-2] if
                            value != "\n"]
            for i in range(len(comment_text)):
                comment_text[i] = comment_text[i].replace("<code", "<p")
                comment_text[i] = comment_text[i].replace("<pre", "<i")
                comment_text[i] = comment_text[i][:comment_text[i].find("<blockquote>")] \
                                  + "<i>" \
                                  + comment_text[i][comment_text[i].find(
                    "<blockquote>"):comment_text[i].find(
                    "</blockquote>") + 13] \
                                  + "</i>" \
                                  + comment_text[i][
                                    comment_text[i].find(
                                        "</blockquote>") + 13:] \
                    if comment_text[i].find("<blockquote>") != -1 else comment_text[i]

            comment_text = "".join(comment_text)

            article_comments.append(
                Comment(comment_author, comment_date, comment_title, comment_text, comment_article_title).__dict__)

    article = Article(article_title, article_author, article_date, article_text, article_mini_text, article_tags,
                      article_url, article_source, article_comments)

    return json.dumps(article.__dict__)


@app.route('/articles/<offset>')
def articles(offset=0):
    html = get_html(linux_url + "/news/" + f"?offset={offset}")
    news = html.find_all(attrs={"class": "news"})
    articles = []
    for articlu in news:
        article_url = articlu.find("h1").find("a")["href"]

        article_title = articlu.select_one("h1").select_one("a").get_text()

        article_author = articlu.select_one(".sign").select_one("a").get_text() if len(
            articlu.select_one(".sign").select("a")) != 0 else "anonymous"

        article_date = articlu.select_one(".sign").select_one("time").get_text()

        article_text = articlu.select_one(".msg").get_text().replace("\n", "")
        if "читать дальше..." in article_text and (
                len(article_text) < 210 or article_text.find("читать дальше...") < 210):
            article_text_length = article_text.find("читать дальше...") - 4
        else:
            if len(article_text) < 210:
                article_text_length = len(article_text) - 11
            else:
                article_text_length = 180
        article_mini_text = article_text[:article_text_length] + "..."

        article_source = articlu.select_one("div.msg").contents[-1].select_one("a")["href"]

        article_tags = ";".join([tag.get_text() for tag in articlu.select_one(".tags").select("a")])

        articles.append(
            Article(article_title, article_author, article_date, article_text, article_mini_text, article_tags,
                    article_url, article_source, []).__dict__)

    return json.dumps(articles)


def get_html(url, parser="html.parser"):
    return BeautifulSoup(requests.get(url).text, parser)


if __name__ == '__main__':
    app.run()
