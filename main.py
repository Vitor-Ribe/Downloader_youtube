import os
import re
from pytube import YouTube, Playlist
from tqdm import tqdm

# Variável global para a barra de progresso
global pbar


def limpar_nome(nome_arquivo):
    """Retira caracteres do nome do arquivo de saída para que não atrapalhe no salvamento"""
    return re.sub(r'[\\/*?:"<>|]', "", nome_arquivo)


def progresso(stream, chunk, bytes_remaining):
    """Callback para atualizar a barra de progresso"""
    global pbar
    pbar.update(len(chunk))


def formato_saida(vd, frmt, caminho_destino):
    """Baixa o vídeo no formato escolhido"""
    global pbar
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


# Pergunta o tipo de vídeo que será baixado
while True:
    tipo = input("O que você baixará? (playlist ou vídeo): ")
    if tipo not in ["playlist", "video"]:
        print("Opção inválida! Escolha uma opção válida!")
    else:
        break

# Pergunta o formato de saída
while True:
    formato = input("Digite o formato que você deseja baixar (mp3 ou mp4): ")
    if formato not in ["mp3", "mp4"]:
        print("Formato inválido! Escolha um formato válido!")
    else:
        break

# Busca o caminho da pasta Downloads no sistema operacional
caminho = os.path.join(os.path.expanduser("~"), "Downloads")

# Verifica se a pasta "Arquivos Downloader" existe; se não, cria ela
pasta_destino = os.path.join(caminho, "Arquivos Downloader")
if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)

if tipo == "video":
    link = input("Digite o link do vídeo que deseja baixar: ")
    print("Processando vídeos...")
    yt = YouTube(link)
    yt.register_on_progress_callback(progresso)
    title = limpar_nome(yt.title)
    if not arquivo_existe(title, formato, pasta_destino):
        formato_saida(yt, formato, pasta_destino)

elif tipo == "playlist":
    link = input("Digite o link da playlist que deseja baixar: ")
    print("Processando vídeos...")
    p = Playlist(link)
    for video in p.videos:
        title = limpar_nome(video.title)
        if not arquivo_existe(title, formato, pasta_destino):
            video.register_on_progress_callback(progresso)
            formato_saida(video, formato, pasta_destino)

print('Download Concluído!')
