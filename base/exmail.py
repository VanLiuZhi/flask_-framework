#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
@author:   LiuZhi
@time:     2019-01-18 21:34
@contact:  vanliuzhi@qq.com
@software: PyCharm
"""

import smtplib

from flask_mail import sanitize_addresses

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from flask_app.utils import get_config

CONFIG = get_config()

FROM_USER, EXMAIL_PASSWORD = CONFIG.FROM_USER, CONFIG.EXMAIL_PASSWORD


def send_mail_task(msg):
    send_to = list(sanitize_addresses(msg.send_to))
    part = MIMEText(msg.html, 'html')
    mp = MIMEMultipart('alternative')
    mp['Subject'] = msg.subject
    mp['From'] = FROM_USER
    mp['To'] = ','.join(send_to)
    mp.attach(part)

    s = smtplib.SMTP_SSL("smtp.qq.com", port=465)
    s.login(FROM_USER, EXMAIL_PASSWORD)
    s.sendmail(FROM_USER, send_to, bytes(mp.as_string(), 'utf-8'))
    s.quit()
