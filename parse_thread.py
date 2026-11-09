
from bs4 import BeautifulSoup
from pathlib import Path
from datetime import datetime
import json
import re
import hashlib

RAW_DIR = Path("raw")
OUT_DIR = Path("index/jsonl")

OUT_DIR.mkdir(parents=True, exist_ok=True)


def parse_thread(file_path):

    raw = file_path.read_bytes()

    # Shift-JIS系を優先して読み込む
    try:
        html = raw.decode("cp932")
    except UnicodeDecodeError:
        html = raw.decode("shift_jis", errors="replace")

    soup = BeautifulSoup(html, "lxml")

    canonical = soup.select_one(
        'link[rel="canonical"]'
    )

    title_tag = soup.select_one("#threadtitle")

    title = (
        title_tag.get_text(" ", strip=True)
        if title_tag else ""
    )

    url = canonical.get("href") if canonical else ""

    match = re.search(
        r"/read\.cgi/([^/]+)/(\d+)",
        url
    )

    board = match.group(1) if match else ""
    thread_id = match.group(2) if match else ""

    posts = []

    for post in soup.select("div.post"):

        post_id = post.get("data-id", "")

        name_tag = post.select_one(".postusername")
        date_tag = post.select_one(".date")
        uid_tag = post.select_one(".uid")
        content_tag = post.select_one(".post-content")

        name = (
            name_tag.get_text(" ", strip=True)
            if name_tag else ""
        )

        date = (
            date_tag.get_text(" ", strip=True)
            if date_tag else ""
        )

        uid = (
            uid_tag.get_text(" ", strip=True)
            if uid_tag else ""
        )

        content = ""

        if content_tag:
            content = content_tag.get_text(
                "\n", strip=True
            )

        posts.append({
            "post_id": post_id,
            "name": name,
            "date": date,
            "uid": uid,
            "content": content
        })

    return {
        "board": board,
        "thread_id": thread_id,
        "title": title,
        "url": url,
        "raw_sha256": hashlib.sha256(raw).hexdigest(),
        "posts": posts
    }


def main():

    for file_path in RAW_DIR.rglob("*.html"):

        try:
            result = parse_thread(file_path)

            if not result["thread_id"]:
                print("スレッドID取得失敗:", file_path)
                continue

            output = (
                OUT_DIR /
                f'{result["board"]}_{result["thread_id"]}.jsonl'
            )

            with output.open(
                "w", encoding="utf-8"
            ) as f:

                thread_info = {
                    k: v for k, v in result.items()
                    if k != "posts"
                }

                f.write(json.dumps(
                    {"type": "thread", **thread_info},
                    ensure_ascii=False
                ) + "\n")

                for post in result["posts"]:
                    f.write(json.dumps(
                        {
                            "type": "post",
                            "board": result["board"],
                            "thread_id": result["thread_id"],
                            **post
                        },
                        ensure_ascii=False
                    ) + "\n")

            print(
                result["thread_id"],
                result["title"],
                len(result["posts"])
            )

        except Exception as e:
            print("ERROR:", file_path, e)


if __name__ == "__main__":
    main()

