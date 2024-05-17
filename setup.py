from cx_Freeze import setup, Executable

# Inclua dependências adicionais aqui, se necessário
build_exe_options = {
    "packages": ["os", "re", "pytube", "tqdm"],
    "excludes": [],
}

setup(
    name="YouTube Downloader",
    version="0.1",
    description="Um downloader de vídeos do YouTube",
    options={"build_exe": build_exe_options},
    executables=[Executable("main.py", base=None, target_name="youtube_downloader.exe")],
)
