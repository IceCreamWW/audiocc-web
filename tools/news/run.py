import argparse
import logging
from pathlib import Path

from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from fetch_article import fetch_article

CHROME_DRIVER_PATH = "./chromedriver"
EC_WAIT_TIMEOUT = 60


def fetch_all_articles_in_album(url, workspace, force_update=False):
    # Setting up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize WebDriver
    service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    logging.info(f"fetching album from {url}")
    driver.get(url)

    article_btns = WebDriverWait(driver, EC_WAIT_TIMEOUT).until(
        EC.presence_of_all_elements_located((By.CLASS_NAME, "album__item-title-wrp"))
    )
    for article_btn in article_btns:
        if len(article_btn.text) != 0:
            article_btn.click()
            driver.switch_to.window(driver.window_handles[-1])
            break
    url = driver.current_url
    driver.quit()

    # create random folder for fetch article
    while url is not None:
        _, (url, _) = fetch_article(url, workspace, overwrite=force_update)


if __name__ == "__main__":

    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    parser = argparse.ArgumentParser(description="Get article content from URL")
    parser.add_argument("--url", type=str, help="URL of the album", default="https://mp.weixin.qq.com/mp/appmsgalbum?__biz=MzkyNjYyOTk2OA==&action=getalbum&album_id=3354438011224211464&scene=173&subscene=&sessionid=svr_872f447ee9e&enterid=1709534258&from_msgid=2247483736&from_itemidx=1&count=3&nolastread=1#wechat_redirect")
    parser.add_argument(
        "--force-update",
        type=lambda x: (str(x).lower() == "true"),
        default=False,
        help="Force update the article content",
    )
    parser.add_argument("--workspace", type=str, default="./workspace")

    args = parser.parse_args()
    workspace = Path(args.workspace)
    workspace.mkdir(exist_ok=True)

    fetch_all_articles_in_album(args.url, workspace)
