import argparse
import logging
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from time import sleep
from openai import OpenAI
import wget
import yaml

CHROME_DRIVER_PATH = './chromedriver'
EC_WAIT_TIMEOUT = 30

COVER_IMAGE_MIN_WIDTH = 300
COVER_IMAGE_MIN_HEIGHT = 300
COVER_IMAGE_MIN_ASPECT_RATIO = 1
COVER_IMAGE_MAX_ASPECT_RATIO = 3
SUMMARY_MIN_LENGTH = 50

OPENAI_BASE_URL = "http://118.195.211.214:30012/v1/"


@dataclass
class Article:
    url: str
    title: str
    publish_date: str
    summary: str
    category: str

    @property
    def uid(self):
        return self.url.split("/")[-1]

    @property
    def page(self):
        fields = {
            "title": self.title,
            "date": self.publish_date,
            "thumbnail": "thumbnail.jpg",
            "taxonomy": { "category": [self.category] },
            "url": self.url,
        }
        content = "---\n" + yaml.dump(fields, default_flow_style=False, allow_unicode=True) + "---\n" + self.summary
        return content


def scroll_to_bottom(driver):
    for _ in range(10):
        driver.execute_script("window.scrollBy(0, window.innerHeight);")
        sleep(1)
        end_of_scroll = driver.execute_script(
            "return document.documentElement.scrollHeight <= document.documentElement.scrollTop + window.innerHeight;")
        if end_of_scroll:
            break

def generate_folder_name(title, max_length=255):
    allowed_chars = "-'`~!@#$%^&+="
    sanitized_title = "".join(c if c.isalnum() or c in allowed_chars else "@" for c in title)
    folder_name = sanitized_title[: max_length - 1]
    return folder_name


def get_thumbnail_images(imgs):
    def can_image_be_thumbnail(img):
        try:
            height, width = img.size['height'], img.size['width']
            if height < COVER_IMAGE_MIN_HEIGHT or width < COVER_IMAGE_MIN_WIDTH:
                return False
            if not (COVER_IMAGE_MIN_ASPECT_RATIO < width / height < COVER_IMAGE_MAX_ASPECT_RATIO):
                return False
            return True
        except:
            return False

    img_urls = []
    for img in imgs:
        if can_image_be_thumbnail(img):
            src = img.get_attribute("src")
            if not src.startswith("http"):
                continue
            img_urls.append(src)
    return img_urls


def get_summary(driver):
    client = OpenAI(api_key="EMPTY", base_url=OPENAI_BASE_URL)
    paragraphs = WebDriverWait(driver, EC_WAIT_TIMEOUT).until(EC.presence_of_all_elements_located((By.TAG_NAME, "p")))
    text = "".join([p.text for p in paragraphs])[:1000]
    messages = [
        {
            "role": "system",
            "content": "You are ChatGLM3, a large language model trained by Zhipu.AI. Follow the user's "
                       "instructions carefully. Respond using markdown.",
        },
        {
            "role": "user",
            "content": "如下是一段从网页爬取的文本内容，请写一个100字左右的摘要，注意不要缩写英文：" + text,
            }
    ]
    response = client.chat.completions.create(
        model="chatglm3-6b",
        messages=messages,
        stream=False,
        max_tokens=256,
        temperature=0.8,
        presence_penalty=1.1,
        top_p=0.8)

    if response:
        return response.choices[0].message.content
    else:
        raise Exception("Failed to get summary")


def fetch_article(url, workspace, overwrite=False):

    # Setting up Chrome options
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Run in background
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # Initialize WebDriver
    service = Service(executable_path=CHROME_DRIVER_PATH)
    driver = webdriver.Chrome(service=service, options=chrome_options)

    logging.info(f"fetching article from {url}")
    driver.get(url)


    title = WebDriverWait(driver, EC_WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, "activity-name"))).text
    article_folder = workspace / generate_folder_name(title)
    article_folder.mkdir(exist_ok=True)

    if not overwrite and (article_folder / "thumbnail.jpg").exists():
        logging.info(f"Article {title} already exists, skipping...")
        article = None
    else:
        logging.info("scrolling to bottom")
        scroll_to_bottom(driver)

        # Example: Extract the title of the page
        logging.info(f"the article title is: {title}")

        if title.startswith("【论文速递】"):
            category = "research"
        else:
            category = "general"

        publish_time = WebDriverWait(driver, EC_WAIT_TIMEOUT).until(EC.presence_of_element_located((By.ID, "publish_time"))).text

        logging.info("getting thumbnail image")
        imgs = WebDriverWait(driver, EC_WAIT_TIMEOUT).until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, "img")))

        logging.info("summairzing")
        img_urls = get_thumbnail_images(imgs)
        assert len(img_urls) > 0, "No valid thumbnail image found"
        img_url = img_urls[1] if category == "research" and len(img_urls) > 1  else img_urls[0]
        wget.download(img_url, (article_folder / "thumbnail.jpg").as_posix())

        summary = get_summary(driver)

        article = Article(
            url=url,
            title=title,
            publish_date=datetime.strptime(publish_time, "%Y-%m-%d  %H:%M").strftime("%m/%d/%Y %H:%M"),
            summary=summary,
            category=category
        )

        with open(article_folder / "item.zh-hans.md", "w") as f:
            f.write(article.page)
            
        with open(article_folder / "item.en.md", "w") as f:
            f.write(article.page)

    next_url = prev_url = None
    num_page_nav_btns = len(WebDriverWait(driver, EC_WAIT_TIMEOUT).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "album_read_nav_btn"))))
    for i in range(num_page_nav_btns):
        btns = WebDriverWait(driver, EC_WAIT_TIMEOUT).until(EC.presence_of_all_elements_located((By.CLASS_NAME, "album_read_nav_btn")))
        btn_text = btns[i].text
        btns[i].click()
        if btn_text == "下一篇":
            next_url = driver.current_url
        else:
            prev_url = driver.current_url
        driver.back()
    driver.quit()

    return article, (prev_url, next_url)

if __name__ == '__main__':
    format = "%(asctime)s: %(message)s"
    logging.basicConfig(format=format, level=logging.INFO, datefmt="%H:%M:%S")

    parser = argparse.ArgumentParser(description='Get article content from URL')
    parser.add_argument('--url', type=str, help='URL of the article')
    parser.add_argument('--force-update', type=lambda x: (str(x).lower() == 'true'), default=False, help='Force update the article content')
    parser.add_argument('--workspace', type=str, default="./workspace")

    args = parser.parse_args()
    uid = args.url.split("/")[-1]
    workspace = Path(args.workspace)
    workspace.mkdir(exist_ok=True)

    if (workspace / uid / "thumbnail.jpg").exists() and not args.force_update:
        print(f"Article {uid} already exists, skipping...")
    else:
        fetch_article(args.url, workspace / uid)

