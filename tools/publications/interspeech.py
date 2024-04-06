import argparse
from tqdm import tqdm
from bs4 import BeautifulSoup
from pathlib import Path
import datetime
import logging
import requests
from utils import parse_bibstring

def collect(workspace: Path):
    year_from, year_to = 2019, datetime.datetime.now().year
    for year in range(year_from, year_to + 1):
        url_prefix = f"https://www.isca-archive.org/interspeech_{year}/"
        response = requests.get(f"{url_prefix}/index.html")

        if response.status_code != 200:
            logging.error(f"failed to fetch interspeech website for year {year}")
            continue

        soup = BeautifulSoup(response.text, "lxml")
        links = [link['href'] for link in soup.find_all('a') if 'Yanmin Qian' in link.get_text()]

        logging.info(f"found {len(links)} papers for year {year}")
        for link in tqdm(links):
            response = requests.get(f"{url_prefix}/{link}")
            soup = BeautifulSoup(response.text, "lxml")

            bibstring = soup.find('pre').get_text()
            citation = parse_bibstring(bibstring)[0]
            this_workspace = workspace / str(citation.year) / citation.uid
            done_flag_path = this_workspace / '.interspeech'
            if done_flag_path.exists():
                continue

            logging.info(f"downloading {citation.title}...")
            this_workspace.mkdir(exist_ok=True, parents=True)
            pdf_path = this_workspace / 'paper.pdf'
            pdf_link = soup.find(class_="fa-file-pdf-o").parent['href']
            pdf_content = requests.get(f"{url_prefix}/{pdf_link}").content
            with open(pdf_path, 'wb') as f:
                f.write(pdf_content)
            (this_workspace / "default.md").write_text(citation.frontmatter)
            done_flag_path.touch()

if __name__ == '__main__':
    format_ = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=format_)

    parser = argparse.ArgumentParser()
    parser.add_argument('--workspace', type=Path, default="workspace")
    args = parser.parse_args()
    collect(args.workspace)


