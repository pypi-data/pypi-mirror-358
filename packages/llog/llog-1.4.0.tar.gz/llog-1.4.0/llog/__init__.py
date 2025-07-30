
# local log (globalスコープを汚さないログツール) [llog]

import os
import sys
import fies
import json
import inspect
from sout import sout
from datetime import datetime

# スタックの情報
def get_stack_info(stack_back_offset):
	stack = inspect.stack()
	full_stack = [{"function": e.function, "filename": e.filename}
		for e in stack[stack_back_offset:]]
	return full_stack

# local log (globalスコープを汚さないログツール) [llog]
class LLog:
	# 初期化処理
	def __init__(self, filename, additional = None):
		self.filename = filename
		self.additional = additional	# 追加記録事項
		if self.additional is None: self.additional = {}
		# ログ出力ファイルの作成
		if self.filename not in fies: fies[self.filename] = ""
	# ログ出力 (level: debug) [llog]
	def debug(self, log_contents):
		self.__output_log("DEBUG", log_contents, full_stack_flag = False)
	# ログ出力 (level: info) [llog]
	def info(self, log_contents):
		self.__output_log("INFO", log_contents, full_stack_flag = False)
	# ログ出力 (level: warning) [llog]
	def warning(self, log_contents):
		self.__output_log("WARNING", log_contents, full_stack_flag = False)
	# ログ出力 (level: error) [llog]
	def error(self, log_contents):
		self.__output_log("ERROR", log_contents, full_stack_flag = True)
	# ログ出力 (level: critical) [llog]
	def critical(self, log_contents):
		self.__output_log("CRITICAL", log_contents, full_stack_flag = True)
	# ログ出力
	def __output_log(self, log_level, log_contents, full_stack_flag):
		# スタックの情報
		full_stack = get_stack_info(stack_back_offset = 3)
		# 各種情報の追記
		log_obj = {
			"date": str(datetime.now()),
			"level": log_level,
			"summary_stack": full_stack[0],
			"contents": log_contents
		}
		if full_stack_flag is True:
			log_obj["full_stack"] = full_stack
		# 追加情報
		for k in self.additional:
			log_obj[k] = self.additional[k]
		# jsonl形式に整形
		json_str = json.dumps(log_obj, ensure_ascii = False)
		# ファイル出力
		with open(self.filename, "a", encoding = "utf-8") as f:
			f.write(json_str + "\n")
	# 最新ログのレビュー (標準出力)
	def tail(self, n = 10, show_flag = True):
		# ログファイル読み込み
		with open(self.filename, "r", encoding = "utf-8") as f:
			raw_s = f.read()
		json_str_ls = raw_s.split("\n")
		obj_ls = [(idx, json.loads(s))
			for idx, s in enumerate(json_str_ls) if s.strip() != ""]
		latest_ls = obj_ls[-n:]
		# 表示
		if show_flag is True:
			for idx, one_log in latest_ls:
				print("[log #%d] "%idx, end = "")
				sout(one_log)
		return latest_ls
	# for文脈に対応
	def __iter__(self):
		# ログファイル読み込み
		with open(self.filename, "r", encoding = "utf-8") as f:
			while True:
				line = f.readline()
				if line == "": break
				obj = json.loads(line)
				yield obj
	# レコード数
	def __len__(self):
		cnt = 0
		for _ in self:
			cnt += 1
		return cnt
