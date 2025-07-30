
import sys
from relpath import add_import_path
add_import_path("../../")
# local log (globalスコープを汚さないログツール) [llog]
from llog import LLog

# local log (globalスコープを汚さないログツール) [llog]
main_logger = LLog(
	filename = "./test_log.log"
)
