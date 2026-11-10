## 構成

```
5ch_project/
│
├── .venv/
│   └── Python仮想環境
│
├── parse_thread.py
│   └── 取得したスレHTMLをJSONLへ変換
│
├── server/
│   │
│   ├── kakolog_servers.html
│   │   └── kakolog_servers.htmlを保存
│   │
│   └── servers.txt
│       └── サーバ一覧抽出結果
│
├── raw/
│   │
│   ├── 1589366535.html
│   ├── 1589366535.html
│   ├── 1589366623.html
│   └── ...
│
│
├── index/
│   │
│   └── jsonl/
│       ├── poverty_1589366535.jsonl
│       ├── poverty_1589366570.jsonl
│       └── ...
│
└── logs/
    ├── download.log
    ├── error.log
    └── parsed.log
```

## 処理の流れ

```
kako.5ch.io/poverty?page=N
            ↓
    スレHTML一括取得
            ↓
         raw保存
            ↓
     parse_thread.py
            ↓
        JSONL生成
            ↓
      頻度分析・検索
```

## html取得

Linuxコマンドで取得（量が多いので24101～24443とページ指定）

```bash
for page in $(seq 24101 24443)
do
    echo "page=${page}"

    curl -sL \
        "https://kako.5ch.io/poverty?page=${page}/" \
        -o page.html

    grep -oE 'test/read.cgi/poverty/[0-9]+' page.html |
    sort -u |
    while read -r thread
    do
        tid=$(basename "$thread")

        if [ -f "raw/${tid}.html" ]; then
            continue
        fi

        echo "  thread=${tid}"

        curl -sL \
            "https://kako.5ch.io/${thread}/" \
            -o "raw/${tid}.html"

        sleep 0.5
    done

    sleep 1
done
```

`/raw`に生のhtmlファイルが保存される。

## 実行

`python parse_thread.py` 

以下に正規化されたjsonとして保存される。

`/index/jsonl`
