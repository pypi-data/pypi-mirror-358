※下の方に日本語の説明があります

## English description
This package a logging tool that doesn't pollute the global scope.

How to use

```python
from llog import LLog

test_log = LLog("./test_log.log")
test_log.debug({"msg": "test1"})
test_log.debug({"msg": "test2"})
test_log.debug({"msg": "test3"})

```

Output result: test_log.log
```json
{"date": "2020-09-22 03:32:59.614418", "level": "DEBUG", "summary_stack": {"function": "<module>", "filename": "test_root.py"}, "contents": {"msg": "test1"}}
{"date": "2020-09-22 03:32:59.616413", "level": "DEBUG", "summary_stack": {"function": "<module>", "filename": "test_root.py"}, "contents": {"msg": "test2"}}
{"date": "2020-09-22 03:32:59.617411", "level": "DEBUG", "summary_stack": {"function": "<module>", "filename": "test_root.py"}, "contents": {"msg": "test3"}}
```

You can check the contents of the log file (the last n entries) as follows:

```python
test_log.tail(n = 2)
```

Result: standard output (console)
```
[log #1] {
  "date": "2020-09-22 03:32:59.616413",
  "level": "DEBUG",
  "summary_stack": {
    "function": "<module>",
    "filename": "test_root.py"
  },
  "contents": {"msg": "test2"}
}
[log #2] {
  "date": "2020-09-22 03:32:59.617411",
  "level": "DEBUG",
  "summary_stack": {
    "function": "<module>",
    "filename": "test_root.py"
  },
  "contents": {"msg": "test3"}
}
```

## 日本語の説明
ログの設定範囲を細かく管理できるログツール (他ツールのログ設定と競合しない)

簡単な使い方
```python
from llog import LLog

test_log = LLog("./test_log.log")
test_log.debug({"msg": "test1"})
test_log.debug({"msg": "test2"})
test_log.debug({"msg": "test3"})

```

出力結果: test_log.log
```json
{"date": "2020-09-22 03:32:59.614418", "level": "DEBUG", "summary_stack": {"function": "<module>", "filename": "test_root.py"}, "contents": {"msg": "test1"}}
{"date": "2020-09-22 03:32:59.616413", "level": "DEBUG", "summary_stack": {"function": "<module>", "filename": "test_root.py"}, "contents": {"msg": "test2"}}
{"date": "2020-09-22 03:32:59.617411", "level": "DEBUG", "summary_stack": {"function": "<module>", "filename": "test_root.py"}, "contents": {"msg": "test3"}}
```

ログファイルの内容 (末尾n件) を以下のように確認できます。

```python
test_log.tail(n = 2)
```

結果: 標準出力 (コンソール)
```
[log #1] {
  "date": "2020-09-22 03:32:59.616413",
  "level": "DEBUG",
  "summary_stack": {
    "function": "<module>",
    "filename": "test_root.py"
  },
  "contents": {"msg": "test2"}
}
[log #2] {
  "date": "2020-09-22 03:32:59.617411",
  "level": "DEBUG",
  "summary_stack": {
    "function": "<module>",
    "filename": "test_root.py"
  },
  "contents": {"msg": "test3"}
}
```

なお、 show_flag = False オプション引数で標準出力がoffにできます。
また、どちらの場合であっても、標準出力の他に返値として末尾ログ一覧が返ります。
