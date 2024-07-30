import argparse
from tqdm import tqdm
from distutils.dir_util import copy_tree
from pathlib import Path
import logging
from utils import read_frontmatter, get_directory

if __name__ == "__main__":
    format_ = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=format_)
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=Path, default=Path("workspace"))
    parser.add_argument("--dst", type=Path, default=Path("../../user/pages/03.research/02.publications"))
    args = parser.parse_args()

    logging.info("normalizing directories names...")
    for path in tqdm(list(args.dst.glob("*/*"))):
        frontmatter = read_frontmatter((path / "default.md"))
        directory = get_directory(frontmatter["title"])
        if directory != path.name:
            logging.info(f"renaming {path.name} to {directory}")
            if (path.parent / directory).exists():
                logging.error(f"{path.parent / directory} already exists")
                exit(1)
            path.rename(path.parent / directory)

    logging.info("adding new papers...")
    for src_path in tqdm(list(args.src.glob("*/*"))):
        relative_path = src_path.relative_to(args.src)
        dst_path = args.dst / relative_path
        if not dst_path.exists():
            logging.info("linking {relative_path}")
            dst_path.symlink_to(src_path, target_is_directory=True)
            # copy_tree(src_path.as_posix(), dst_path.as_posix())

