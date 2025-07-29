# @Time : 2023-06-14 10:53
# @Author  : Huang.XiaoGang
# @Desc : ==============================================
# Life is Short I Use Python!!!                      ===
# ======================================================
# @Project : GbopApiClient
# @FileName: common
# @Software: PyCharm
from collections import namedtuple

ResultStruct = namedtuple('ResultStruct', ['result', 'code', 'message', 'data'])
ResultStruct.__new__.__defaults__ = (False, 0, '', None)
