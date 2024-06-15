import flet as ft
import os
from qr_generator import QRGenerator


class QRManagerApp:
    # QRコード最大文字数
    MAX_LENGTH = 500

    def __init__(self, assets_dir='assets') -> None:
        '''コンストラクタ'''
        self.assets_dir = assets_dir
        self.page = None
        # ref群
        self.ref_qr_image = ft.Ref[ft.Image]()
        self.ref_tabs = ft.Ref[ft.Tabs]()
        self.ref_file_path = ft.Ref[ft.TextField]()
        self.ref_file_errlabel = ft.Ref[ft.Text]()
        self.ref_file_contents = ft.Ref[ft.TextField]()
        self.ref_contents = ft.Ref[ft.TextField]()

    def initialize_page(self, page: ft.Page):
        '''ページ初期設定'''
        self.page = page
        self.page.title = 'QR Manager'
        self.page.window_width = self.page.window_min_width = 360
        self.page.window_height = self.page.window_min_height = 640
        self.page.window_resizable = False
        self.page.update()

    def show_snack_bar(self, message: str):
        '''スナックバー表示'''
        self.page.snack_bar = ft.SnackBar(ft.Text(message), duration=750)
        self.page.snack_bar.open = True
        self.page.update()

    def on_pick_files_result(self, e: ft.FilePickerResultEvent):
        '''ファイル選択後処理'''
        if e.files and len(e.files) > 0:
            self.ref_file_path.current.value = e.files[0].path
            self.page.update()
            self.generate()

    def on_save_files_result(self, e: ft.FilePickerResultEvent):
        '''保存先選択後処理'''
        if e.path:
            QRGenerator.save_file_from_base64(
                self.ref_qr_image.current.src_base64, e.path)
            self.show_snack_bar('Saved QR Code.')

    def generate(self):
        '''生成処理'''
        text = ''
        match self.ref_tabs.current.selected_index:
            case 0:
                # テキスト入力時
                text = self.ref_contents.current.value
            case _:
                # テキストファイル入力時
                if not os.path.exists(self.ref_file_path.current.value):
                    # ファイル非存在時
                    self.ref_file_errlabel.current.value = 'file is not exists.'
                    self.ref_file_errlabel.current.visible = True
                    self.page.update()

                    text = ''
                else:
                    # ファイル存在時
                    self.ref_file_errlabel.current.visible = False
                    self.page.update()

                    text = QRGenerator.load_file(
                        self.ref_file_path.current.value)

                    if len(text) > QRManagerApp.MAX_LENGTH:
                        text = text[:QRManagerApp.MAX_LENGTH]
                        self.ref_file_errlabel.current.value = f'This file is more than {QRManagerApp.MAX_LENGTH} chars.'
                        self.ref_file_errlabel.current.visible = True

                self.ref_file_contents.current.value = text
                self.page.update()

        try:
            self.ref_qr_image.current.src_base64 = QRGenerator.generate_qr_base64(
                text)
            self.page.update()
        except Exception as e:
            self.show_snack_bar('Failed to generate.')

    def main(self, page: ft.Page):
        # ページ初期設定
        self.initialize_page(page)

        # ファイル選択ダイアログ
        pick_file_dialog = ft.FilePicker(on_result=self.on_pick_files_result)
        # ファイル保存先選択ダイアログ
        save_file_dialog = ft.FilePicker(on_result=self.on_save_files_result)
        # オーバーレイ設定
        page.overlay.extend([save_file_dialog, pick_file_dialog])

        # コントロール追加
        page.add(
            ft.Row([
                ft.Image(ref=self.ref_qr_image,
                         src_base64=QRGenerator.generate_qr_base64(''),
                         width=200,
                         height=200,
                         fit=ft.ImageFit.CONTAIN)],
                   alignment=ft.MainAxisAlignment.CENTER),
            ft.Tabs(ref=self.ref_tabs,
                    animation_duration=300,
                    tabs=[
                        ft.Tab(text='Text',
                               tab_content=ft.Icon(ft.icons.TEXT_FIELDS),
                               content=ft.Container(ft.TextField(ref=self.ref_contents,
                                                                 label='Generate by Text',
                                                                 multiline=True,
                                                                 max_lines=8,
                                                                 text_size=12,
                                                                 max_length=QRManagerApp.MAX_LENGTH,
                                                                 on_change=lambda _: self.generate()),
                                                    padding=ft.padding.all(8))),
                        ft.Tab(text='File',
                               tab_content=ft.Icon(ft.icons.FILE_OPEN),
                               content=ft.Container(ft.Column([
                                   ft.TextField(ref=self.ref_file_path,
                                                label='Generate by TextFile'),
                                    ft.Row([
                                        ft.ElevatedButton('Load File',
                                                          on_click=lambda _: pick_file_dialog.pick_files(initial_directory='.',
                                                                                                         allow_multiple=False,
                                                                                                         allowed_extensions=['txt', 'text', 'md', 'json', 'csv', 'del', 'sql', 'py'])),
                                        ft.Text(
                                            ref=self.ref_file_errlabel, color=ft.colors.RED, visible=False)
                                    ]),
                                   ft.TextField(ref=self.ref_file_contents,
                                                label="Text Preview",
                                                multiline=True,
                                                max_lines=6,
                                                text_size=12,
                                                read_only=True,
                                                max_length=QRManagerApp.MAX_LENGTH)
                               ]),
                                   padding=ft.padding.all(8))),
                    ],
                    expand=True,
                    on_change=lambda _: self.generate()
                    ),
            ft.Row([
                ft.ElevatedButton('Generate',
                                  on_click=lambda _: self.generate()),
                ft.ElevatedButton('Save',
                                  on_click=lambda _: save_file_dialog.save_file(initial_directory='.',
                                                                                file_name='qr.png',
                                                                                allowed_extensions=['png', 'ping', 'jpg', 'jpeg']))
            ]),
        )

    def run(self):
        '''アプリ実行'''
        ft.app(target=self.__class__().main, assets_dir=self.assets_dir,)
