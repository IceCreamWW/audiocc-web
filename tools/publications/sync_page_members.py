from pathlib import Path
import logging
import argparse
from tqdm import tqdm
from utils import read_frontmatter, write_frontmatter
import os

def get_relative_path(path1, path2):
    common_prefix = os.path.commonprefix([path1, path2])
    common_path = os.path.dirname(common_prefix)
    relative_path = os.path.relpath(path2, common_path)
    backward = os.path.relpath(common_path, path1.parent)
    return backward + '/' + relative_path

def has_author(paper, author):
    authors = [author.replace(",", "").replace(" ","").lower() for author in paper['author'].split(" and ")]
    if "INTERSPEECH" in paper.get('booktitle', ''):
        author = "".join(author.split(".")).lower()
    else:
        author = "".join(author.split(".")[::-1]).lower()
    return author in authors


if __name__ == "__main__":
    format_ = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=format_)
    parser = argparse.ArgumentParser()
    parser.add_argument("--papers", type=Path, default=Path("../../user/pages/03.research/02.publications/"))
    parser.add_argument("--members", type=Path, default=Path("../../user/pages/04.members/"))
    args = parser.parse_args()

    papers = []

    for path in tqdm(list(args.papers.glob("*/*"))):
        frontmatter = read_frontmatter((path / "default.md"))
        papers.append((frontmatter, path))

    for path in tqdm(list(args.members.glob("*"))):
        if path.is_file():
            continue
        name = path.name
        (path / "publications").mkdir(parents=True, exist_ok=True)
        for paper in papers:
            if has_author(paper[0], name):
                link = path / "publications" / paper[1].name
                link.unlink(missing_ok=True)
                # link to path relative to the members directory
                link.symlink_to(get_relative_path(link, paper[1]), target_is_directory=True)

