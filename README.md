🌐 ArXiv Explorer API
REST API для поиска научных статей из arXiv.org (область Computer Science) с возможностью перевода аннотаций.

# API endpoints
| Method | Endpoint | Description | 
|--------|----------|-------------|
| GET | `/` | Главная страница | 
| GET | `/Titles` | Поиск статей из области Computer Science по ключевому слову |
| GET | `/Article` | Поиск статьи по ID | 
| GET | `/Article/translate` | Перевод аннотации найденной статьи | 
