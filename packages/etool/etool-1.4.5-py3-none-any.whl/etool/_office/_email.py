import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
import os
import re

class ManagerEmail:
    email_providers = {
                "qq.com": ("smtp.qq.com", 465),
                "foxmail.com": ("smtp.qq.com", 465),
                "exmail.qq.com": ("smtp.exmail.qq.com", 465),
                "163.com": ("smtp.163.com", 465),
                "126.com": ("smtp.126.com", 465),
                "yeah.net": ("smtp.yeah.net", 465),
                "sina.com": ("smtp.sina.com", 465),
                "sina.cn": ("smtp.sina.cn", 465),
                "sohu.com": ("smtp.sohu.com", 465),
                "outlook.com": ("smtp.office365.com", 587),
                "hotmail.com": ("smtp.office365.com", 587),
                "live.com": ("smtp.office365.com", 587),
                "gmail.com": ("smtp.gmail.com", 587),
                "yahoo.com": ("smtp.mail.yahoo.com", 465),
                "yahoo.com.cn": ("smtp.mail.yahoo.com.cn", 465),
                "aliyun.com": ("smtp.aliyun.com", 465),
                "139.com": ("smtp.139.com", 465),
                "189.cn": ("smtp.189.cn", 465),
            }

    @staticmethod
    def send_email(
        sender,
        password,
        message,
        recipient,
        subject=None,
        sender_show=None,
        recipient_show=None,
        file_path=None,
        image_path=None,
        cc_show="",
        smtp_ssl=True,
    ) -> str:
        """
        :param sender: str sender
        :param password: str sender password
        :param message: str message
        :param recipient: str recipient
        :param subject: str subject description
        :param sender_show: str sender display, does not actually affect anything like: "xxx"
        :param recipient_show: str recipient display, does not actually affect anything like: "xxx,xxxx"
        :param cc_show: str cc display, does not actually affect anything, multiple cc separated by ',' like: "xxx,xxxx"
        :param file_path: str file path
        :param image_path: str image path
        """
        # fill in the real sender email and password

        if not recipient.endswith(","):
            recipient = recipient + ","


        # define the method of sending attachments as a variable
        msg = MIMEMultipart()
        # email content
        content = (
            message + "<br><br>" + "来自 Allen 的 AI Agent 的邮件，有问题请联系我。"
        )

        # send content
        msg.attach(MIMEText(content, "html", "utf-8"))
        # call the module of sending attachments, send attachments
        if file_path:

            if isinstance(file_path, str):
                file_path = [file_path]
            for file_path in file_path:
                att = MIMEText(open(file_path, 'rb').read(), 'base64', 'utf-8')
                att['Content-Type'] = 'application/octet-stream'
                file_name = os.path.basename(file_path)
                if re.search(r'[\u4e00-\u9fff]', file_name):
                    att.add_header('Content-Disposition', 'attachment', filename=('utf-8', '', file_name))
                else:
                    att['Content-Disposition'] = f'attachment; filename="{file_name}"'
                msg.attach(att)
        # process images
        if image_path:
            if isinstance(image_path, str):
                image_path = [image_path]

            mime_images = ''
            for i, img_path in enumerate(image_path, start=1):
                mime_images += f'<p><img src="cid:imageid{i}" alt="imageid{i}"></p>'
                with open(img_path, 'rb') as img_file:
                    mime_img = MIMEImage(img_file.read(), _subtype='octet-stream')
                    mime_img.add_header('Content-ID', f'<imageid{i}>')
                    msg.attach(mime_img)
            
            mime_html = MIMEText(f'<html><body><p>{message or ""}</p>{mime_images}</body></html>', 'html', 'utf-8')
            msg.attach(mime_html)


        msg["Subject"] = subject if subject else "来自 AI 的邮件"
        # sender display, does not actually affect anything
        msg["from"] = sender_show if sender_show else sender
        # recipient display, does not actually affect anything
        msg["to"] = recipient_show if recipient_show else recipient
        # cc display, does not actually affect anything
        msg["Cc"] = cc_show

        # loop this list, remove empty data
        to_addrs = [addr for addr in recipient.split(",") if addr]

        host,port = ManagerEmail.email_providers.get(sender.split("@")[-1].lower(), ("smtp.exmail.qq.com", 465))
        try:
            if smtp_ssl:
                server = smtplib.SMTP_SSL(host, port)
            else:
                server = smtplib.SMTP(host, port)
                server.starttls()
            server.login(sender, password)
            server.sendmail(sender, to_addrs, msg.as_string())
            server.quit()
        except Exception as e:
            try:

                if e.smtp_code != -1:
                    return f"send error.{e}"
                else:
                    return "send success"
            except:
                return f"send error.{e}"
        return "send success"