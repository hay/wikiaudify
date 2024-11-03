from loguru import logger
import requests

class Wikipedia:
    def __init__(self, language):
        self.language = language
        self.endpoint = f"https://{language}.wikipedia.org/w/api.php"

    def get_article(self, title) -> str:
        logger.debug(f"Trying to get the wikitext for article {title}")
        # https://en.wikipedia.org/w/api.php?action=query&prop=extracts&titles=Dom_Tower_of_Utrecht&formatversion=2&explaintext=1
        req = requests.get(self.endpoint, params = {
            "action" : "query",
            "prop" : "extracts",
            "titles" : title,
            "explaintext" : "1",
            "formatversion" : "2",
            "format" : "json"
        })

        data = req.json()

        if "query" not in data:
            raise Exception("No results found")

        revision = data["query"]["pages"][0]["extract"]

        logger.debug(f"Revision text: {revision}")

        return revision

if __name__ == "__main__":
    wp = Wikipedia("en")
    text = wp.get_article("Dom_Tower_of_Utrecht")
    print(text)