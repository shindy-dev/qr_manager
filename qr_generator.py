import qrcode
import base64
import io
import chardet


class QRGenerator:
    @staticmethod
    def generate_qr(qr_str: str) -> qrcode.QRCode:
        '''QRコード作成'''
        # QRコードの設定
        qr = qrcode.QRCode(
            # QRコードの大きさ(バージョン)。Noneで自動設定(1～22)。数値指定しても必要なら自動で大きくなる
            version=None,
            # 誤り訂正レベル(L：約7%,M：約15%,Q:約25%,H:約30%)
            error_correction=qrcode.constants.ERROR_CORRECT_M,
            box_size=12,  # サイズを何倍にするか。1ならdot-by-dot(px)
            border=4,  # 認識用余白(最低4)
        )
        # QRコード化したい文字列を追加
        qr.add_data(qr_str)
        # QRコード作成
        qr.make(fit=True)
        return qr

    @staticmethod
    def generate_qr_base64(qr_str: str) -> str:
        '''QRコード生成(base64形式)'''
        # QRコード画像生成
        img = QRGenerator.generate_qr(qr_str).make_image()
        # ストリームデータとして保持
        with io.BytesIO() as image_stream:
            img.save(image_stream, format="PNG")
            # BytesIOからBase64に変換
            return base64.b64encode(image_stream.getvalue()).decode("utf-8")

    @staticmethod
    def load_file(file_path: str) -> str:
        '''テキスト取得'''
        # バイナリデータを取得し、文字コードを推測
        with open(file_path, 'rb') as bf:
            encode_data = chardet.detect(bf.read())
        # ファイルを取得
        with open(file_path, mode='r', encoding=encode_data['encoding']) as f:
            return f.read()

    @staticmethod
    def save_file_from_base64(data: str, file_path: str):
        '''base64形式のデータをデコードし、ファイルとして保存'''
        # Decode base64 String Data
        decodedData = base64.b64decode((data))

        # Write Image from Base64 File
        with open(file_path, 'wb') as f:
            f.write(decodedData)
