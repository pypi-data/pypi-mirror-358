# 関数実行時間のロギング [log_time]
# 【動作確認 / 使用例】

import sys
import time
import ezpip
log_time = ezpip.load_develop("log_time", "../", develop_flag = True)

@log_time
def some_proc():
	time.sleep(0.5)

@log_time
def other_proc():
	time.sleep(0.1)

some_proc()
other_proc()
some_proc()
# → 「timelog.llog」に実行時間が出力される

# ログの中身を見る
log_time.llog.tail(n = 3)

# ログファイルパスを変更する (llog形式)
log_time.setpath("other_path.llog")
