from pypdf import PdfWriter, PdfReader, PdfMerger, PdfReader, PdfWriter
from pathlib import Path
import os
from pathlib import Path
from win32com.client import Dispatch, gencache, DispatchEx
import win32com.client
import time
import ctypes
from ctypes import wintypes
from pdf2docx import Converter


class PDFConverter:
    def pdfconverter(self, pathname: str, outpath: str):
        self._handle_postfix = ["doc", "docx", "ppt", "pptx", "xls", "xlsx"]
        self._filename_list = list()
        self._export_folder = outpath
        if not os.path.exists(self._export_folder):
            os.mkdir(self._export_folder)
        self._enumerate_filename(pathname)
        print("need to convert files：", len(self._filename_list))
        for filename in self._filename_list:
            postfix = filename.split(".")[-1].lower()
            funcCall = getattr(self, postfix)
            print("original file：", filename)
            funcCall(filename)
        print("conversion completed!")

    def _enumerate_filename(self, pathname):
        full_pathname = os.path.abspath(pathname)
        if os.path.isfile(full_pathname):
            if self._is_legal_postfix(full_pathname):
                self._filename_list.append(full_pathname)
            else:
                raise TypeError(
                    "file {} is not valid! only support the following file types: {}".format(
                        pathname, "、".join(self._handle_postfix)
                    )
                )
        elif os.path.isdir(full_pathname):
            for relpath, _, files in os.walk(full_pathname):

                for name in files:
                    filename = os.path.join(full_pathname, relpath, name)
                    if self._is_legal_postfix(filename):
                        self._filename_list.append(os.path.join(filename))
        else:
            raise TypeError(
                "file/folder {} does not exist or is not valid!".format(pathname)
            )

    def _is_legal_postfix(self, filename):
        return filename.split(".")[
            -1
        ].lower() in self._handle_postfix and not os.path.basename(filename).startswith(
            "~"
        )

    def get_short_path_name(self, long_path):
        """
        Convert the given absolute path to a short path (DOS 8.3 format).
        If the conversion fails or short paths are not enabled, the original path is returned.
        """
        GetShortPathNameW = ctypes.windll.kernel32.GetShortPathNameW

        GetShortPathNameW.argtypes = [wintypes.LPCWSTR, wintypes.LPWSTR, wintypes.DWORD]
        GetShortPathNameW.restype = wintypes.DWORD

        buffer_size = 260
        output_buf = ctypes.create_unicode_buffer(buffer_size)
        result = GetShortPathNameW(long_path, output_buf, buffer_size)

        if result > 0 and result < buffer_size:
            return output_buf.value
        else:
            return long_path

    def doc(self, filename):
        """
        doc and docx files conversion
        """
        name = os.path.basename(filename).split(".")[0] + ".pdf"
        word = None
        doc = None

        try:
            # initialize the Word COM object
            gencache.EnsureModule("{00020905-0000-0000-C000-000000000046}", 0, 8, 4)
            word = DispatchEx("Word.Application")
            word.Visible = 0
            word.DisplayAlerts = 0

            # convert the file path to the absolute path short path
            abs_path = os.path.abspath(filename)
            abs_short_path = self.get_short_path_name(abs_path)

            pdf_file = os.path.join(self._export_folder, name)
            pdf_short_path = self.get_short_path_name(pdf_file)

            # add a retry mechanism
            max_retries = 3
            retry_count = 0
            while retry_count < max_retries:

                try:
                    doc = word.Documents.Open(
                        abs_short_path,
                        ReadOnly=True,
                        Visible=False,
                        ConfirmConversions=False,
                    )
                    # save to the short path
                    doc.SaveAs(pdf_short_path, FileFormat=17)
                    print(f"successfully converted: {filename}")
                    break

                except Exception as e:
                    retry_count += 1
                    if retry_count == max_retries:
                        print(f"after {max_retries} attempts, still failed: {filename}")
                        raise
                    print(f"the {retry_count}th attempt failed, preparing to retry...")
                    time.sleep(2)  # 等待2秒后重试

        except Exception as e:
            print(f"failed to convert file {filename}: {str(e)}")
            raise

        finally:
            # ensure all COM objects are cleaned up
            if doc:
                try:
                    doc.Close(SaveChanges=False)
                except:
                    pass
            if word:
                try:
                    word.Quit()
                except:
                    pass
            # force cleanup COM objects
            if doc:
                del doc

            if word:
                del word
            # force garbage collection
            import gc

            gc.collect()

    def docx(self, filename):
        self.doc(filename)

    def xls(self, filename):
        """
        xls and xlsx files conversion, and set to scale to a single page (horizontal)
        """
        name = os.path.basename(filename).split(".")[0] + ".pdf"
        exportfile = os.path.join(self._export_folder, name)
        xlApp = DispatchEx("Excel.Application")
        xlApp.Visible = False

        xlApp.DisplayAlerts = 0
        books = xlApp.Workbooks.Open(filename, False)

        for sheet in books.Worksheets:
            # disable Zoom to fit the multi-page scaling effect
            sheet.PageSetup.Zoom = False

            # limit the content to 1 page width and 1 page height
            sheet.PageSetup.FitToPagesWide = 1
            sheet.PageSetup.FitToPagesTall = 1

            # set horizontal printing
            # xlOrientationPortrait = 1, xlOrientationLandscape = 2
            sheet.PageSetup.Orientation = 2

            sheet.PageSetup.LeftMargin = 0
            sheet.PageSetup.RightMargin = 0
            sheet.PageSetup.TopMargin = 0
            sheet.PageSetup.BottomMargin = 0

            # set the paper size, for example A4
            # from win32com.client import constants
            # sheet.PageSetup.PaperSize = constants.xlPaperA4

        books.ExportAsFixedFormat(0, exportfile)
        books.Close(False)
        print(f"saved the PDF file: {exportfile}")
        xlApp.Quit()

    def xlsx(self, filename):
        self.xls(filename)

    def ppt(self, filename):
        """
        export the PPT file to the pdf format
        :param filename: the name of the PPT file
        :param output_filename: the name of the exported pdf file
        :return:
        """
        name = os.path.basename(filename).split(".")[0] + ".pdf"
        exportfile = os.path.join(self._export_folder, name)

        ppt_app = win32com.client.Dispatch("PowerPoint.Application")
        ppt = ppt_app.Presentations.Open(filename)
        ppt.SaveAs(exportfile, 32)
        print(f"saved the PDF file: {exportfile}")
        ppt_app.Quit()

    def pptx(self, filename):
        self.ppt(filename)

    def pdf2docx(self, filename):
        """
        pdf to docx, the best effect for pure text + images, other formats like hyperlinks will not be preserved
        """
        cv = Converter(filename)
        cv.convert(filename.replace(".pdf", ".docx"), start=0, end=None)
        cv.close()


class ManagerPdf:
    """
    PDF file manager, providing encryption, decryption, splitting, merging, etc.


    manager = PdfManager()
    manager.encrypt_pdf(Path('ex1.pdf'), new_password='leafage')
    manager.decrypt_pdf(Path('ex1123_encrypted.pdf'), password='leafage')
    manager.split_by_pages(Path('ex1.pdf'), pages_per_split=5)
    manager.split_by_num(Path('A.pdf'), num_splits=122)
    manager.merge_pdfs(
        filenames=[Path('ex1.pdf'), Path('ex2.pdf')],
        merged_name=Path('merged.pdf')
    )
    manager.insert_pdf(
        pdf1=Path('ex1.pdf'),
        pdf2=Path('ex2.pdf'),
        insert_page_num=10,
        merged_name=Path('pdf12.pdf')
    )
    manager.auto_merge(Path("PDF"))
    """

    @staticmethod
    def pdfconverter(pathname: str, outpath: str):
        """
        batch convert files to pdf
        :param pathname: the path of the file to be converted
        :param outpath: the path of the converted file
        :return:
        """
        converter = PDFConverter()
        converter.pdfconverter(pathname, outpath)

    @staticmethod
    def create_watermarks(
        pdf_file_path: str, watermark_file_path: str, save_path: str = "watermarks"
    ):
        """
        add watermarks to the pdf file
        :param pdf_file_path: the path of the pdf file
        :param watermark_file_path: the path of the watermark file
        :param save_path: the path to save the watermarked file
        :return:
        """

        def create_watermark(input_pdf, watermark, output_pdf):
            # get the watermark
            watermark_obj = PdfReader(watermark, strict=False)
            watermark_page = watermark_obj.get_page(0)

            # create the reader and writer objects
            pdf_reader = PdfReader(input_pdf, strict=False)
            pdf_writer = PdfWriter()

            # add watermarks to all pages and create a new pdf file
            for page in range(pdf_reader.get_num_pages()):
                page = pdf_reader.get_page(page)
                page.merge_page(watermark_page)
                pdf_writer.add_page(page)

            with open(output_pdf, "wb") as out:
                pdf_writer.write(out)

        # determine if it is a file or a folder
        if os.path.isfile(pdf_file_path):
            create_watermark(
                pdf_file_path,
                watermark_file_path,
                os.path.join(save_path, os.path.basename(pdf_file_path)),
            )
        else:

            for pdf_file in os.listdir(pdf_file_path):
                if pdf_file[-3:] == "pdf":
                    input_pdf = os.path.join(pdf_file_path, pdf_file)
                    create_watermark(
                        input_pdf,
                        watermark_file_path,
                        os.path.join(save_path, os.path.basename(pdf_file)),
                    )

    @staticmethod
    def open_pdf_file(filename: Path, mode: str = "rb"):
        """use the context manager to open the PDF file"""
        return filename.open(mode)

    @staticmethod
    def get_reader(filename: Path, password: str = None) -> PdfReader:
        """get the PDF reader instance"""
        try:
            pdf_reader = PdfReader(filename, strict=False)
            if pdf_reader.is_encrypted:

                if password is None or not pdf_reader.decrypt(password):
                    print(f"{filename} is encrypted or the password is incorrect!")
                    return None
            return pdf_reader
        except Exception as err:

            print(f"failed to open the file: {err}")
            return None

    @staticmethod
    def write_pdf(writer: PdfWriter, filename: Path):
        """write the PDF file"""
        with filename.open("wb") as output_file:
            writer.write(output_file)

    @staticmethod
    def encrypt_pdf(
        filename: str,
        new_password: str,
        old_password: str = None,
        encrypted_filename: Path = None,
    ):
        """encrypt the PDF file"""
        pdf_reader = ManagerPdf.get_reader(Path(filename), old_password)
        if pdf_reader is None:
            return

        pdf_writer = PdfWriter()
        pdf_writer.append_pages_from_reader(pdf_reader)
        pdf_writer.encrypt(new_password)

        if encrypted_filename is None:
            encrypted_filename = Path(filename).with_name(
                f"{Path(filename).stem}_encrypted.pdf"
            )

        ManagerPdf.write_pdf(pdf_writer, encrypted_filename)
        print(f"encrypted file saved as: {encrypted_filename}")

    @staticmethod
    def decrypt_pdf(
        filename: str,
        password: str,
        decrypted_filename: Path = None,
    ):
        """decrypt the encrypted PDF file"""
        pdf_reader = ManagerPdf.get_reader(Path(filename), password)
        if pdf_reader is None:
            return

        if not pdf_reader.is_encrypted:
            print("the file is not encrypted, no operation needed!")
            return

        pdf_writer = PdfWriter()
        pdf_writer.append_pages_from_reader(pdf_reader)

        if decrypted_filename is None:
            decrypted_filename = Path(filename).with_name(
                f"{Path(filename).stem}_decrypted.pdf"
            )

        ManagerPdf.write_pdf(pdf_writer, decrypted_filename)
        print(f"decrypted file saved as: {decrypted_filename}")

    @staticmethod
    def split_by_pages(
        filename: str | Path,
        pages_per_split: int,
        password: str = None,
    ):
        """split the PDF file by the number of pages"""
        if isinstance(filename, str):
            filename = Path(filename)
        pdf_reader = ManagerPdf.get_reader(filename, password)

        if pdf_reader is None:
            return

        total_pages = len(pdf_reader.pages)
        if pages_per_split < 1:
            print("each file must contain at least 1 page!")
            return

        num_splits = (total_pages + pages_per_split - 1) // pages_per_split
        print(
            f"the PDF file will be split into {num_splits} parts, each part contains at most {pages_per_split} pages."
        )

        for split_num in range(num_splits):
            pdf_writer = PdfWriter()
            start = split_num * pages_per_split
            end = min(start + pages_per_split, total_pages)
            for page in range(start, end):
                pdf_writer.add_page(pdf_reader.pages[page])

            split_filename = filename.with_name(
                f"{filename.stem}_part_by_page{split_num + 1}.pdf"
            )
            ManagerPdf.write_pdf(pdf_writer, split_filename)
            print(f"generated: {split_filename}")

    @staticmethod
    def split_by_num(
        filename: str | Path,
        num_splits: int,
        password: str = None,
    ):
        """split the PDF file by the number of pages"""
        if isinstance(filename, str):
            filename = Path(filename)

        try:
            pdf_reader = ManagerPdf.get_reader(filename, password)
            if pdf_reader is None:
                return

            total_pages = len(pdf_reader.pages)
            if num_splits < 2:
                print("the number of parts cannot be less than 2!")
                return
            if total_pages < num_splits:
                print(
                    f"the number of parts({num_splits}) should not be greater than the total number of pages({total_pages})!"
                )

                return

            pages_per_split = total_pages // num_splits
            extra_pages = total_pages % num_splits
            print(
                f"the PDF has {total_pages} pages, will be split into {num_splits} parts, each part contains at most {pages_per_split} pages."
            )

            start = 0
            for split_num in range(1, num_splits + 1):
                pdf_writer = PdfWriter()
                # distribute extra pages to the first few splits
                end = start + pages_per_split + (1 if split_num <= extra_pages else 0)
                for page in range(start, end):
                    pdf_writer.add_page(pdf_reader.pages[page])

                split_filename = filename.with_name(
                    f"{filename.stem}_part_by_num{split_num}.pdf"
                )
                ManagerPdf.write_pdf(pdf_writer, split_filename)
                print(f"generated: {split_filename}")
                start = end

        except Exception as e:
            print(f"error occurred when splitting the PDF: {e}")

    @staticmethod
    def merge_pdfs(
        filenames: str | list[str],
        merged_name: str,
        passwords: list = None,
    ):
        """merge multiple PDF files into one"""
        if passwords and len(passwords) != len(filenames):
            print(
                "the length of the password list must be the same as the length of the file list!"
            )
            return

        writer = PdfWriter()

        if isinstance(filenames, str):
            if os.path.isfile(filenames):
                filenames = [filenames]
            elif os.path.isdir(filenames):
                filenames = [str(path) for path in Path(filenames).rglob("*.pdf")]

        for idx, file in enumerate(filenames):
            password = passwords[idx] if passwords else None
            pdf_reader = ManagerPdf.get_reader(Path(file), password)
            if not pdf_reader:
                print(f"skip file: {file}")
                continue
            for page in range(len(pdf_reader.pages)):
                writer.add_page(pdf_reader.pages[page])

            print(f"merged: {file}")

        with Path(merged_name).open("wb") as f_out:
            writer.write(f_out)

        print(f"merged file saved as: {merged_name}")

    @staticmethod
    def insert_pdf(
        pdf1: str | Path,
        pdf2: str | Path,
        insert_page_num: int,
        merged_name: str | Path,
        password1: str = None,
        password2: str = None,
    ):
        """insert the pdf2 into the specified page after the pdf1"""
        if isinstance(pdf1, str):
            pdf1 = Path(pdf1)
        if isinstance(pdf2, str):

            pdf2 = Path(pdf2)
        if isinstance(merged_name, str):
            merged_name = Path(merged_name)

        pdf1_reader = ManagerPdf.get_reader(pdf1, password1)
        pdf2_reader = ManagerPdf.get_reader(pdf2, password2)
        if not pdf1_reader or not pdf2_reader:
            return

        total_pages_pdf1 = len(pdf1_reader.pages)
        if not (0 <= insert_page_num <= total_pages_pdf1):
            print(
                f"the insertion position is abnormal, the insertion page number is: {insert_page_num}, the PDF1 file has: {total_pages_pdf1} pages!"
            )
            return

        writer = PdfWriter()
        with ManagerPdf.open_pdf_file(pdf1, "rb") as f_pdf1:
            writer.append(f_pdf1, pages=(0, insert_page_num))
        with ManagerPdf.open_pdf_file(pdf2, "rb") as f_pdf2:
            writer.append(f_pdf2)
        with ManagerPdf.open_pdf_file(pdf1, "rb") as f_pdf1:
            writer.append(f_pdf1, pages=(insert_page_num, len(pdf1_reader.pages)))

        with merged_name.open("wb") as f_out:
            writer.write(f_out)
        print(f"inserted file saved as: {merged_name}")
