import os
import sys
test_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(test_dir)
sys.path.insert(0, os.path.join(project_root, "src"))
from etool import *
import pytest
os.chdir("./tests")

def test_speed_manager():

    assert ManagerSpeed.network() is not None

    assert ManagerSpeed.disk() is not None

    assert ManagerSpeed.memory() is not None
    assert ManagerSpeed.gpu_memory() is not None


def test_screen_share():
    # 由于 screen_share 是一个长时间运行的服务，测试时可以检查是否能启动
    assert callable(ManagerShare.screen_share)


def test_share_file():
    # 由于 share_file 是一个长时间运行的服务，测试时可以检查是否能启动
    assert callable(ManagerShare.share_file)


# 跳过
@pytest.mark.skip(reason="发送邮件不宜频繁测试，跳过")
def test_email_manager():
    # 假设 send_email 方法返回 True 表示成功
    assert (
        ManagerEmail.send_email(
            sender="allen_2100@foxmail.com",
            password="********",
            message="测试邮件内容",
            sender_show="allen_2100@foxmail.com",
            recipient="allen_2100@foxmail.com",
            recipient_show="allen_2100@foxmail.com",
            subject="测试邮件",
            file_path="result.docx",
            image_path="pic1.webp",
        )
        == "send success"
    )


@pytest.mark.skip(reason="定时发送不宜频繁测试，跳过")
def test_scheduler_manager():
    # 假设 send_email 方法返回 True 表示成功
    def job():
        print("job")

    def func_success():
        print("success")

    def func_failure():
        print("failure")

    # 每2秒执行一次job，成功时执行func_success，失败时执行func_failure
    ManagerScheduler.pocwatch(job, 2, func_success, func_failure)


def test_image_manager():
    # 假设 merge_LR 和 merge_UD 方法返回合并后的图片路径
    assert ManagerImage.merge_LR(["pic1.webp", "pic2.webp"]) is not None
    assert ManagerImage.merge_UD(["pic1.webp", "pic2.webp"]) is not None
    assert ManagerImage.fill_image("pic1_UD.webp") is not None
    assert isinstance(ManagerImage.cut_image("pic1_UD_fill.webp"), list)
    assert ManagerImage.rename_images("image_dir", remove=True) is not None


def test_password_manager():
    # 检查生成的密码列表和随机密码是否符合预期
    assert (
        len(
            ManagerPassword.generate_pwd_list(
                ManagerPassword.results["all_letters"]
                + ManagerPassword.results["digits"],
                2,
            )
        )
        > 0
    )
    assert len(ManagerPassword.random_pwd(8)) == 8


def test_password_manager_convert_base():
    assert ManagerPassword.convert_base("A1F", 16, 2) == "101000011111"
    assert ManagerPassword.convert_base("-1101", 2, 16) == "-D"
    assert ManagerPassword.convert_base("Z", 36, 10) == "35"


def test_qrcode_manager():
    # 假设 gen_en_qrcode 和 gen_qrcode 方法返回生成的二维码路径
    assert (
        ManagerQrcode.generate_english_qrcode("https://www.baidu.com", "qr.png")
        is not None
    )
    assert ManagerQrcode.generate_qrcode("百度", "qr.png") is not None
    assert ManagerQrcode.decode_qrcode("qr.png") is not None


def test_ipynb_manager():
    # 假设 merge_notebooks 和 convert_notebook_to_markdown 方法返回 True 表示成功
    assert ManagerIpynb.merge_notebooks("ipynb_dir") is not None
    assert (
        ManagerIpynb.convert_notebook_to_markdown("ipynb_dir.ipynb", "md") is not None
    )


def test_docx_manager():
    # 假设 get_pictures 方法返回提取的图片数量
    assert ManagerDocx.replace_words("ex1.docx", "1", "2") is not None
    assert ManagerDocx.change_forward("ex1.docx", "result.docx") is not None
    assert ManagerDocx.get_pictures("ex1.docx", "result") is not None


def test_md_docx_manager():
    # 测试Markdown转换为Word文档功能
    assert ManagerMd.convert_md_to_docx("test.md", "test.docx") is not None
    
    # 测试Markdown转换为HTML网页功能
    assert ManagerMd.convert_md_to_html("test.md", "test.html") is not None
    
    # 测试从Markdown提取表格到Excel功能
    assert ManagerMd.extract_tables_to_excel("test.md", "test.xlsx") is not None


def test_excel_manager():
    # 假设 excel_format 方法返回 True 表示成功
    assert ManagerExcel.excel_format("ex1.xlsx", "result.xlsx") is not None


@pytest.mark.skip(reason="CICD环境没有office组件，跳过")
def test_pdf_manager():
    # doc、xlsx等转换为pdf(转换一个)
    ManagerPdf.pdfconverter(
        os.path.join(os.path.dirname(__file__), "pdf", "ex1.docx"),
        os.path.join(os.path.dirname(__file__), "pdf_out"),
    )
    # doc、xlsx等转换为pdf(转换一个目录下的所有文件)
    ManagerPdf.pdfconverter(
        os.path.join(os.path.dirname(__file__), "pdf"),
        os.path.join(os.path.dirname(__file__), "pdf_out"),
    )

    # 给pdf文件添加水印（一个文件）
    ManagerPdf.create_watermarks(
        os.path.join(os.path.dirname(__file__), "pdf_out", "ex1.pdf"),
        os.path.join(os.path.dirname(__file__), "pdf_out", "watermarks.pdf"),
        os.path.join(os.path.dirname(__file__), "pdf_out_watermark"),
    )
    # 给pdf文件添加水印（一个目录下的所有文件）
    ManagerPdf.create_watermarks(
        os.path.join(os.path.dirname(__file__), "pdf_out"),
        os.path.join(os.path.dirname(__file__), "pdf_out", "watermarks.pdf"),
        os.path.join(os.path.dirname(__file__), "pdf_out_watermark"),
    )

    # 合并pdf文件（一个目录下的所有文件）
    ManagerPdf.merge_pdfs(
        os.path.join(os.path.dirname(__file__), "pdf_out"),
        os.path.join(os.path.dirname(__file__), "pdf_out", "merged.pdf"),
    )

    # 拆分pdf文件（按页数）每3页一份
    ManagerPdf.split_by_pages(
        os.path.join(os.path.dirname(__file__), "pdf_out", "merged.pdf"), 3
    )
    # 拆分pdf文件（按份数）生成2份
    ManagerPdf.split_by_num(
        os.path.join(os.path.dirname(__file__), "pdf_out", "merged.pdf"), 2
    )

    # 将pdf ex2插入到pdf ex1的指定页后
    ManagerPdf.insert_pdf(
        os.path.join(os.path.dirname(__file__), "pdf_out", "ex1.pdf"),
        os.path.join(os.path.dirname(__file__), "pdf_out", "ex2.pdf"),
        0,
        os.path.join(os.path.dirname(__file__), "pdf_out", "pdf_insert.pdf"),
    )

    # 加密pdf文件
    ManagerPdf.encrypt_pdf(
        os.path.join(os.path.dirname(__file__), "pdf_out", "ex1.pdf"), r"1234567890"
    )
    # 解密pdf文件
    ManagerPdf.decrypt_pdf(
        os.path.join(os.path.dirname(__file__), "pdf_out", "ex1_encrypted.pdf"),
        r"1234567890",
    )


def test_install_manager():
    # 安装依赖
    requirements_file = os.path.join(os.path.dirname(__file__), "requirements.txt")
    failed_file = os.path.join(os.path.dirname(__file__), "failed_requirements.txt")
    continue_install = ManagerInstall.install(
        requirements_file=requirements_file, failed_file=failed_file, retry=2
    )
    assert continue_install is True
#  pytest tests/test_etool.py --disable-warnings