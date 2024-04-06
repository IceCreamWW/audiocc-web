import argparse
from tqdm import tqdm
from distutils.dir_util import copy_tree
from pathlib import Path
import logging

if __name__ == "__main__":
    format_ = '%(asctime)s - %(levelname)s - %(message)s'
    logging.basicConfig(level=logging.INFO, format=format_)
    parser = argparse.ArgumentParser()
    parser.add_argument("--src", type=Path, default=Path("workspace"))
    parser.add_argument("--dst", type=Path, default=Path("../../user/pages/03.research/02.publications"))
    args = parser.parse_args()

    for src_path in tqdm(list(args.src.glob("*/*"))):
        relative_path = src_path.relative_to(args.src)
        dst_path = args.dst / relative_path
        if not dst_path.exists():
            logging.info(f"copying {relative_path.name}")
            copy_tree(src_path.as_posix(), dst_path.as_posix())
