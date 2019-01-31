#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-20 00:25
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

unknown_error = (1000, 'unknown error', 400)
access_forbidden = (1001, 'access forbidden', 403)
unimplemented_error = (1002, 'unimplemented error', 400)
not_found = (1003, 'not found', 404)
illegal_state = (1004, 'illegal state', 400)
not_supported = (1005, '暂时不支持此操作', 400)
post_not_found = (1006, 'Post不存在', 400)
api_not_found = (1007, '接口不存在', 404) # 为了安全考虑，实际应用中最好不要返回如此明确的信息，以免接口被猜测出来
