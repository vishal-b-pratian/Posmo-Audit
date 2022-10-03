import snscrape
import requests
from bs4 import BeautifulSoup
from .patcher import scraping_request
from urllib.error import HTTPError, URLError
import snscrape.modules.twitter as sntwitter

snscrape.base.Scraper._request = scraping_request


class Scrapper:

    TWEETS_LIMIT = 1

    @staticmethod
    def __getUsername(url: str) -> str:
        username = url.split("/")[-1]
        return username

    @staticmethod
    def __validateURL(url):
        try:
            requests.get(url, verify=False)
        except IOError as e:
            print("error: ", e)
            return False

        # pattern = "http[s]?://(www.)?(.*?)[/]?$"
        if "twitter.com" in url.split("/")[-2]:
            return "twitter"

        return True

    @staticmethod
    def __fetch_data(url):
        """
        Gets data from the given url.
        """
        try:
            url_request = requests.get(url, verify=False, timeout=20)

        except (HTTPError, URLError):
            return "Server not found / Invalid URL."
        except requests.exceptions.HTTPError as error:
            return "Error: " + str(error)

        soup = BeautifulSoup(url_request.text, "html.parser")
        datas = soup.find_all("body")
        text = ""

        for data in datas:
            text += data.text

        text = [text.replace("\n", "")]

        return text

    def scrapeTwitter(self, url: str):
        username = self.__getUsername(url)
        tweets = []
        tweets_generator = sntwitter.TwitterSearchScraper(
            f"from:{username}",
        ).get_items()
        for count, tweet in enumerate(tweets_generator):
            if count > Scrapper.TWEETS_LIMIT:
                break
            tweets.append(tweet.content)

        return tweets

    def scrapeURL(self, url: str):
        # url_type = self.__validateURL(url)
        # if not url_type:
        #     raise Exception  # Write custom exception.
        # if url_type == "twitter":
        #     data = self.scrapeTwitter(url)
        # else:
        #     data = self.__fetch_data(url)
        data = self.__fetch_data(url)
        return data


if __name__ == "__main__":
    url = "https://twitter.com/SrBachchan"
    s = Scrapper()
    tweets = s.scrapeURL(url)
    print(tweets)
