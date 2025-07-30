
import sys
import time
from my_log_admin import main_logger

def my_func():
	# ログ出力 (level: debug) [llog]
	main_logger.debug({"event": "1+1 calculation started"})
	time.sleep(1)
	result = 1+1
	# ログ出力 (level: debug) [llog]
	main_logger.debug({
		"event": "1+1 calculation finished",
		"result": result
	})
