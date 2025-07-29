from easyqr import easyqr as qr
from MyQR import myqr
import qrcode
class ManagerQrcode:    

    @staticmethod
    def decode_qrcode(path):
        """
        Decode a QR code
        :param path: The path to the image
        :return: The decoded address
        """
        url = qr.upload(path)
        url = qr.online(url)
        return url

    
    @staticmethod
    def generate_english_qrcode(words, save_path):
        """
        Generate a QR code for English content
        :param words: The content of the QR code
        :param save_path: The path to save the QR code
        :return: The path to the QR code
        """
        try:

            myqr.run(
                words=words,
                save_name=save_path
            )
            return save_path
        except Exception as e:
            print(e)
            return None

    @staticmethod
    def generate_qrcode(path, save_path):
        """
        Generate a QR code
        :param path: The content of the QR code
        :param save_path: The path to save the QR code
        :return: The path to the QR code
        """
        img = qrcode.make(path)
        img.save(save_path)
        return save_path


