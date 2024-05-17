import os
import re
from pytube import YouTube, Playlist


def limpar_nome(nome_arquivo):  # retira caracteres do nome do arquivo de saída para que não atrapalhe no salvamento
    return re.sub(r'[\\/*?:"<>|]', "", nome_arquivo)


def formato_saida(vd, frmt, caminho_destino):  # baixa o vídeo no formato escolhido
    print("Baixando " + vd.title + "...")

    if frmt == "mp3":
        audio_stream = vd.streams.filter(only_audio=True, file_extension="mp4").order_by('abr').desc().first()
        audio_stream.download(output_path=caminho_destino, filename=vd.title + ".mp3")
    elif frmt == "mp4":
        resolucao = vd.streams.filter(progressive=True, file_extension="mp4").order_by('resolution').desc().first()
        resolucao.download(output_path=caminho_destino, filename=vd.title + ".mp4")


def arquivo_existe(nome_arquivo, extensao, caminho_destino):
    nome_completo = nome_arquivo + "." + extensao
    return nome_completo in os.listdir(caminho_destino)


# tipo de video que irá baixar
while True:
    tipo = input("O que vc baixará? (playlist ou vídeo): ")
    if tipo != "playlist" and tipo != "video":
        print("Opção inválida! escolha uma opção válida!")
    else:
        break

# formato de saída
while True:
    formato = input("Digite o formato que você deseja baixar (mp3 ou mp4): ")
    if formato != "mp3" and formato != "mp4":
        print("Formato inválido! escolha um formato válido!")
    else:
        break

# busca o caminho da pasta Downloads no sistema operacional
caminho = os.path.join(os.path.expanduser("~"), "Downloads")

# verifica se a pasta "Arquivos" existe, se existir define ela como pasta para salvar os arquivos de saída. Se não, cria ela
pasta_destino = os.path.join(caminho, "Arquivos Downloader")
if not os.path.exists(pasta_destino):
    os.makedirs(pasta_destino)

if tipo == "video":
    link = input("Digite o link do vídeo que deseja baixar: ")
    yt = YouTube(link)
    title = limpar_nome(yt.title)  # limpa o titulo de caracteres que podem causar bugs
    if not arquivo_existe(title, formato, pasta_destino):
        formato_saida(yt, formato, pasta_destino)

elif tipo == "playlist":
    link = input("Digite o link da playlist que deseja baixar: ")
    p = Playlist(link)
    for video in p.videos:  # loop para baixar todos os vídeos da playlist
        title = limpar_nome(video.title)  # limpa o titulo de caracteres que podem causar bugs
        if not arquivo_existe(title, formato, pasta_destino):
            formato_saida(video, formato, pasta_destino)

print("Download Concluído!")
