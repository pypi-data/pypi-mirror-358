# local log (globalスコープを汚さないログツール) [llog]
# 【動作確認 / 使用例】

import sys
import time
import ezpip
llog = ezpip.load_develop("llog", "../", develop_flag = True)

test_log = llog.LLog("./test_log.log")
test_log.debug({"msg": "test1"})
test_log.debug({"msg": "test2"})
