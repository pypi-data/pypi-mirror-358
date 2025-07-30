# 関数実行時間のロギング [ticklog]
# 【動作確認 / 使用例】

import sys
import time
import ezpip
ticklog = ezpip.load_develop("ticklog", "../", develop_flag = True)

@ticklog
def some_proc():
	time.sleep(0.5)

@ticklog
def other_proc():
	time.sleep(0.1)

some_proc()
other_proc()
some_proc()
# → 「ticklog.llog」に実行時間が出力される

# ログの中身を見る
ticklog.llog.tail(n = 3)

# ログファイルパスを変更する (llog形式)
ticklog.setpath("other_path.llog")
