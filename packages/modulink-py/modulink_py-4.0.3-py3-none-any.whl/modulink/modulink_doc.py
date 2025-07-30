#!/usr/bin/env python3
# modulink CLI entrypoint

import argparse
import os
import shutil
from .docs import get_doc

def main():
    parser = argparse.ArgumentParser(description="Query ModuLink documentation.")
    parser.add_argument("topic", nargs="?", default="readme", help="Documentation topic (e.g., chain, middleware.Logging, examples, todo, readme)")
    parser.add_argument("--cheatsheet", action="store_true", help="Copy the ModuLink cheatsheet to ./references/modulink-py.md in your project.")
    args = parser.parse_args()
    if args.cheatsheet:
        src = os.path.join(os.path.dirname(__file__), "..", "references", "modulink-py.md")
        dst_dir = os.path.abspath(os.path.join(os.getcwd(), "references"))
        os.makedirs(dst_dir, exist_ok=True)
        dst = os.path.join(dst_dir, "modulink-py.md")
        shutil.copyfile(src, dst)
        print(f"Copied cheatsheet to {dst}")
    else:
        print(get_doc(args.topic))

if __name__ == "__main__":
    main()
