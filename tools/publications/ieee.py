import argparse
from pathlib import Path
import datetime
import logging
import json
import time
import requests
from utils import parse_bibstring

from fake_useragent import UserAgent

MAX_RETRY = 3
UA = UserAgent()


def search(search_params):
    response = requests.post('https://ieeexplore.ieee.org/rest/search', data=json.dumps(search_params), headers={'Content-Type': 'application/json', 'Referer': 'https://ieeexplore.ieee.org/search/searchresult.jsp', 'User-Agent': UA.random})
    return response.json()

def get_bibstring_by_article_number(article_number: str):
    bibtex = requests.get(f'https://ieeexplore.ieee.org/rest/search/citation/format?recordIds={article_number}&download-format=download-bibtex&lite=true', headers={'Referer': 'https://ieeexplore.ieee.org/document/10438838', 'User-Agent': UA.random}).text
    bibtex = json.loads(bibtex)['data'].replace('\r', '')
    return bibtex

def get_pdf_by_article_number(article_number: str, pdf_path: Path):
    response = None
    for _ in range(MAX_RETRY):
        try:
            response = requests.get(f'https://ieeexplore.ieee.org/stampPDF/getPDF.jsp?tp=&arnumber={article_number}&ref=', headers={'User-Agent': UA.random}, stream=True)
            with open(pdf_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=1024):
                    f.write(chunk)
            return True
        except Exception as e:
            time.sleep(1)
            continue
    logging.error(f"faild to save {pdf_path} (article number: {article_number})")
    return False


def collect(workspace: Path):
    year_from, year_to = 2019, datetime.datetime.now().year
    params = {
        'highlight': True,
        'returnType': 'SEARCH',
        'matchPubs': False,
        'matchAuthors': True,
        'sortType': 'newest',
        'pageNumber': 1,
        'searchWithin': ['"First Name":Yanmin', '"Last Name":Qian'],
        'ranges': [f'{year_from}_{year_to}_Year'],
        'returnFacets': ['ALL']
    }
    response = search(params)
    total_records, total_pages = response['totalRecords'], response['totalPages']
    num_records = len(list(workspace.glob('*/*/.ieee')))
    assert total_records >= num_records

    if total_records == num_records:
        logging.info(f"no new records found ({num_records} records), done.")
        return
    logging.info(f"expected {total_records} records, found {num_records} records, start downloading...")

    for page_num in range(1, total_pages+1):
        params['pageNumber'] = page_num
        response = search(params)
        article_numbers = [article['articleNumber'] for article in response['records']]
        for article_number in article_numbers:
            bibstring = get_bibstring_by_article_number(article_number)
            citation = parse_bibstring(bibstring)[0]
            this_workspace = workspace / str(citation.year) / citation.directory
            done_flag_path = this_workspace / '.ieee'
            if done_flag_path.exists():
                continue

            logging.info(f"downloading {num_records+1} / {total_records}, (article number: {article_number})...")
            this_workspace.mkdir(exist_ok=True, parents=True)
            pdf_path = this_workspace / 'paper.pdf'
            if not get_pdf_by_article_number(article_number, pdf_path):
                continue
            (this_workspace / "default.md").write_text(citation.frontmatter)
            done_flag_path.touch()
            num_records += 1

            if num_records >= total_records:
                logging.info(f"downloaded {num_records} records, done.")
                break

if __name__ == '__main__':
    format_ = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=format_)

    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, default="workspace")
    args = parser.parse_args()
    collect(args.workspace)


