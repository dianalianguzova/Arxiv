from typing import Type
import uvicorn
from fastapi import FastAPI, HTTPException, Request, Query
from bs4 import BeautifulSoup
from fastapi import Path
from requests import get
from starlette import status
from fastapi.templating import Jinja2Templates
from translate import Translator

from server.model.article import Article

app = FastAPI()
APP_HOST = "localhost"
APP_PORT = 8000
_translator = Translator(to_lang="ru")
templates = Jinja2Templates(directory="client/")

@app.get("/")
async def welcome(request: Request):
    return templates.TemplateResponse("arxiv.html", {
        "request": request,
        "titleSearch": False,
        "articleSearch": False
    })

@app.get("/Titles")
async def titles(request: Request, keyWords: str = Query(..., title="Ключевое слово для поиска статей")):
    url = "https://arxiv.org/search/cs?query=" + keyWords + "&searchtype=all&abstracts=show&order=-announced_date_first&size=200"
    response = get(url)
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    items = soup.select('li.arxiv-result p.title')
    names = []
    for item in items:
        names.append(item.text.strip())
    if not names:
        return templates.TemplateResponse("arxiv.html", {
            "request": request,
            "titleSearch": True,
            "articleSearch": False,
            "titles": None
        })
    return templates.TemplateResponse("arxiv.html", {
        "request": request,
        "titleSearch": True,
        "articleSearch": False,
        "titles": names
    })

def getArticleInfo(soup: BeautifulSoup) -> Type[Article]:
    art = Article
    span = soup.select_one('h1.title span')
    if span: span.decompose()
    art.name = soup.select_one('h1.title').text.strip() #название

    authors = soup.select('div.authors a')
    authorsRes = []
    for author in authors:
        authorsRes.append(author.text.strip())
    art.authors = authorsRes #авторы

    desc = soup.select_one('blockquote.abstract').text.strip()  #аннотация
    if len(desc) > 9: desc = desc[9:]  #убрать текст из span
    art.description = desc
    return art


@app.get("/Article")
async def article(request: Request, id: str = Query(..., title="ID статьи")):
    url = "https://arxiv.org/abs/" + id
    response = get(url)
    if response.status_code == 404:
        return templates.TemplateResponse("arxiv.html", {
            "request": request,
            "titleSearch": False,
            "articleSearch": True,
            "article": None
        })
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    art = getArticleInfo(soup)
    return templates.TemplateResponse("arxiv.html", {
        "request": request,
        "titleSearch": False,
        "articleSearch": True,
        "article": {
            "id": id,
            "name": art.name,
            "authors": art.authors,
            "description": art.description
        }
    })

def splitDesc(text: str) -> list[str]:
    maxLen = 500
    parts = []
    while len(text) > maxLen:
        part = text[:maxLen]
        parts.append(part)
        text = text[maxLen:]
    parts.append(text)
    return parts

@app.get("/Article/translate")
async def articleTranslate(request: Request, id: str):
    url = "https://arxiv.org/abs/" + id
    response = get(url)
    if response.status_code==404:
        return templates.TemplateResponse("arxiv.html", {
            "request": request,
            "titleSearch": False,
            "articleSearch": True,
            "translated": False
        })
    html_content = response.text
    soup = BeautifulSoup(html_content, 'html.parser')
    art = getArticleInfo(soup)

    descParts = splitDesc(art.description)
    translatedParts = []
    for part in descParts:
        translatedPart = _translator.translate(part)
        translatedParts.append(translatedPart)
    translatedText = " ".join(translatedParts)
    return templates.TemplateResponse("arxiv.html", {
        "request": request,
        "titleSearch": False,
        "articleSearch": True,
        "translated": True,
        "translate": translatedText,
        "article": {
            "id": id,
            "name": art.name,
            "authors": art.authors,
            "description": art.description
        }
    })


if __name__ == "__main__":
    uvicorn.run("arxivAPI:app", host=APP_HOST, port=APP_PORT, workers=1)