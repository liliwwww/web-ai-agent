import openai
import schedule
import time
import smtplib
import logging
from subprocess import run
from email.mime.text import MIMEText


# 配置日志记录
logging.basicConfig(
    filename='scheduler.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)


def send_email(to, title, body):
    max_retries = 3
    retries = 0
    while retries < max_retries:
        try:
            '''
            # 以下是简单的邮件发送示例，你需要根据实际情况修改邮箱配置
            sender = 'your_email@example.com'
            password = 'your_email_password'

            msg = MIMEText(body)
            msg['Subject'] = title
            msg['From'] = sender
            msg['To'] = to

            server = smtplib.SMTP('smtp.example.com', 587)
            server.starttls()
            server.login(sender, password)
            server.sendmail(sender, [to], msg.as_string())
            server.quit()
            '''
            logging.info(f"邮件发送成功，收件人: {to}, 主题: {title}")
            print(f"邮件发送成功，收件人: {to}, 主题: {title}")
            
            return True
        except Exception as e:
            retries += 1
            logging.error(f"邮件发送失败，第 {retries} 次重试: {e}")
    return False


def send_sms(phone, message):
    # 这里只是示例，实际需要实现短信发送逻辑
    logging.info(f"尝试向 {phone} 发送短信: {message}")
    return True


def send_cmd(cmd):
    # 这里只是示例，实际需要实现命令执行逻辑
    logging.info(f"尝试执行命令: {cmd}")
    return True


def send_sql(sql):
    # 这里只是示例，实际需要实现SQL执行逻辑
    logging.info(f"尝试执行SQL语句: {sql}")
    return True
