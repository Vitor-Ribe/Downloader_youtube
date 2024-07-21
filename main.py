import sys
import os
import re
import subprocess
import platform
from PyQt5.QtWidgets import QApplication, QMainWindow, QLabel, QLineEdit, QPushButton, QVBoxLayout, QWidget, QHBoxLayout, QMessageBox
from PyQt5.QtCore import QThread, pyqtSignal
from pytube import YouTube, Playlist
from tqdm import tqdm


class DownloadThread(QThread):
    # Define sinais para atualizar a interface
    progress_signal = pyqtSignal(int)
    finished_signal = pyqtSignal(str)

    def __init__(self, link, tipo, formato, caminho_destino):
        super().__init__()
        self.link = link
        self.tipo = tipo
        self.formato = formato
        self.caminho_destino = caminho_destino

    def run(self):
        def limpar_nome(nome_arquivo):
            """Retira caracteres do nome do arquivo de saída para que não atrapalhe no salvamento"""
            return re.sub(r'[\\/*?:"<>|]', "", nome_arquivo)

        def progresso(stream, chunk, bytes_remaining):
            """Callback para atualizar a barra de progresso"""
            self.progress_signal.emit(len(chunk))

        def formato_saida(vd, frmt, caminho_destino):
            """Baixa o vídeo no formato escolhido"""
            titulo = limpar_nome(vd.title)

            if frmt == "mp3":
                audio_stream = vd.streams.filter(only_audio=True, file_extension="mp4").order_by('abr').desc().first()
                pbar = tqdm(total=audio_stream.filesize, unit='B', unit_scale=True, desc=titulo, colour='green')
                audio_stream.download(output_path=caminho_destino, filename=titulo + ".mp3")
                pbar.close()
            elif frmt == "mp4":
                video_stream = vd.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first()
                pbar = tqdm(total=video_stream.filesize, unit='B', unit_scale=True, desc=titulo, colour='green')
                video_stream.download(output_path=caminho_destino, filename=titulo + ".mp4")
                pbar.close()

        def arquivo_existe(nome_arquivo, extensao, caminho_destino):
            """Verifica se o arquivo já existe no diretório de destino"""
            nome_completo = nome_arquivo + "." + extensao
            return nome_completo in os.listdir(caminho_destino)

        def is_youtube_link(link):
            # Verifica se o URL corresponde ao formato do YouTube
            youtube_padrao = r'^(https?://)?(www\.)?(youtube\.com|youtu\.?be)/.*$'
            return bool(re.match(youtube_padrao, link))

        if self.tipo == "video":
            if not is_youtube_link(self.link):
                self.finished_signal.emit("Link do YouTube inválido!")
                return
            yt = YouTube(self.link)
            yt.register_on_progress_callback(progresso)
            title = limpar_nome(yt.title)
            if not arquivo_existe(title, self.formato, self.caminho_destino):
                formato_saida(yt, self.formato, self.caminho_destino)

        elif self.tipo == "playlist":
            if not is_youtube_link(self.link):
                self.finished_signal.emit("Link do YouTube inválido!")
                return
            p = Playlist(self.link)
            for video in p.videos:
                title = limpar_nome(video.title)
                if not arquivo_existe(title, self.formato, self.caminho_destino):
                    video.register_on_progress_callback(progresso)
                    formato_saida(video, self.formato, self.caminho_destino)

        self.finished_signal.emit("Download Concluído!")


class DownloadWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Download de Vídeos')
        self.setGeometry(200, 200, 400, 300)
        self.setStyleSheet('background-color: #333; color: white;')

        self.tipo = None
        self.formato = None

        # Criando os widgets
        self.label_link = QLabel('Digite aqui seu link:', self)
        self.line_edit_link = QLineEdit(self)

        self.label_tipo = QLabel('Escolha o tipo que irá baixar:', self)
        self.btn_playlist = QPushButton('Playlist', self)
        self.btn_video = QPushButton('Vídeo', self)

        self.label_formato = QLabel('Escolha o formato de saída:', self)
        self.btn_mp3 = QPushButton('MP3', self)
        self.btn_mp4 = QPushButton('MP4', self)

        self.btn_download = QPushButton('Download', self)

        # Layouts para organizar os widgets
        vbox = QVBoxLayout()
        vbox.addWidget(self.label_link)
        vbox.addWidget(self.line_edit_link)
        vbox.addWidget(self.label_tipo)

        hbox_tipo = QHBoxLayout()
        hbox_tipo.addWidget(self.btn_playlist)
        hbox_tipo.addWidget(self.btn_video)
        vbox.addLayout(hbox_tipo)

        vbox.addWidget(self.label_formato)

        hbox_formato = QHBoxLayout()
        hbox_formato.addWidget(self.btn_mp3)
        hbox_formato.addWidget(self.btn_mp4)
        vbox.addLayout(hbox_formato)

        vbox.addWidget(self.btn_download)

        # Widget central que contém todos os elementos
        central_widget = QWidget()
        central_widget.setLayout(vbox)
        self.setCentralWidget(central_widget)

        # Conectar botões para alternar cor quando clicados
        self.btn_playlist.clicked.connect(self.on_btn_playlist_clicked)
        self.btn_video.clicked.connect(self.on_btn_video_clicked)
        self.btn_mp3.clicked.connect(self.on_btn_mp3_clicked)
        self.btn_mp4.clicked.connect(self.on_btn_mp4_clicked)
        self.btn_download.clicked.connect(self.on_btn_download_clicked)

    def on_btn_playlist_clicked(self):
        self.tipo = "playlist"
        self.btn_playlist.setStyleSheet('background-color: #555; color: white;')
        self.btn_video.setStyleSheet('')

    def on_btn_video_clicked(self):
        self.tipo = "video"
        self.btn_video.setStyleSheet('background-color: #555; color: white;')
        self.btn_playlist.setStyleSheet('')

    def on_btn_mp3_clicked(self):
        self.formato = "mp3"
        self.btn_mp3.setStyleSheet('background-color: #555; color: white;')
        self.btn_mp4.setStyleSheet('')

    def on_btn_mp4_clicked(self):
        self.formato = "mp4"
        self.btn_mp4.setStyleSheet('background-color: #555; color: white;')
        self.btn_mp3.setStyleSheet('')

    def on_btn_download_clicked(self):
        link = self.line_edit_link.text().strip()
        if not link or not self.tipo or not self.formato:
            QMessageBox.warning(self, "Aviso", "Por favor, preencha todos os campos e selecione opções válidas!")
            return

        caminho = os.path.join(os.path.expanduser("~"), "Downloads", "Arquivos Downloader")
        if not os.path.exists(caminho):
            os.makedirs(caminho)

        self.thread = DownloadThread(link, self.tipo, self.formato, caminho)
        self.thread.progress_signal.connect(self.update_progress)
        self.thread.finished_signal.connect(self.show_finished_message)
        self.thread.start()

    def update_progress(self, bytes_received):
        # Atualiza a barra de progresso aqui, se necessário
        pass

    def show_finished_message(self, message):
        QMessageBox.information(self, "Concluído", message)
        self.open_download_folder()

    def open_download_folder(self):
        caminho = os.path.join(os.path.expanduser("~"), "Downloads", "Arquivos Downloader")
        if platform.system() == "Windows":
            subprocess.run(['explorer', caminho])
        elif platform.system() == "Darwin":  # macOS
            subprocess.run(['open', caminho])
        elif platform.system() == "Linux":
            subprocess.run(['xdg-open', caminho])
        else:
            QMessageBox.warning(self, "Aviso", "Sistema operacional não suportado para abrir a pasta.")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = DownloadWindow()
    window.show()
    sys.exit(app.exec_())
