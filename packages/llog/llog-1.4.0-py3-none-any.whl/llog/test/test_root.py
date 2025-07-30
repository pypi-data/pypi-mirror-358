
import sys
from my_log_admin import main_logger
from some_parts import my_func

# ログ出力 (level: info) [llog]
main_logger.info({"event": "app_boot"})
my_func()
# ログ出力 (level: info) [llog]
main_logger.info({"event": "app_terminated"})

# 最新ログのレビュー (標準出力)
main_logger.tail(n = 3)

obj = main_logger.tail(n = 3, show_flag = False)
print(str(obj)[:100])

print("%d records"%len(main_logger))
