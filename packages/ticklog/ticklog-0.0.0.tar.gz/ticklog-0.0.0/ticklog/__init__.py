# 関数実行時間のロギング [log_time]

import sys
import llog
import time

# 現在時刻を取得する関数
now = time.time

class LogTimeObj:
	# 初期化処理
	def __init__(self):
		# デフォルトのログ保存パス
		self.log_path = "./timelog.llog"
	# ログファイルパスを変更する [log_time]
	def setpath(self, new_path): self.log_path = new_path
	# デコレータ(@log_time)として呼ばれた時 [log_time]
	def __call__(self, org_proc):
		# 時間測定機能などを追加した関数
		def timelog_wrapper(*args, **kwargs):
			t0 = now()	# 開始時刻を記録
			res = org_proc(*args, **kwargs)	# 元の処理を実行
			self.llog.info({"name": org_proc.__name__, "exec_sec": now() - t0})	# 所要時間をロギング
			return res
		return timelog_wrapper
	# llogオブジェクトの取得 [log_time]
	@property
	def llog(self): return llog.LLog(self.log_path)

# log_pathモジュールとLogTimeObjオブジェクトを同一視
sys.modules[__name__] = LogTimeObj()
