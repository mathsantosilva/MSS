import os, subprocess, requests

class UpdaterCmd:
    def executar_comando_batch(self, dir_atual: str):
        comando = r"""@echo off
chcp 65001
cls
echo Aguarde enquanto a atualização esta em andamento
xcopy "C:\MSS_temp\BuscaMuro.exe" "{DIR}\BuscaMuro.exe" /w/E/Y/H
echo.
echo Atualização realizada com sucesso 
echo.
pause
exit
""".replace("{DIR}", dir_atual)
        with open("C:/MSS_temp/script_temp.bat", "a", encoding="UTF-8") as f:
            f.write(comando)
        subprocess.Popen(['start', 'cmd', '/k', 'C:/MSS_temp/script_temp.bat'], shell=True, text=True)

    def realizar_download(self, tag: str, popup):
        try:
            url = f"https://github.com/mathsantosilva/MSS/releases/download/{tag}/BuscaMuro.exe"
            r = requests.get(url); r.raise_for_status()
            os.makedirs("C:/MSS_temp", exist_ok=True)
            with open("C:/MSS_temp/BuscaMuro.exe", "wb") as f: f.write(r.content)
        except Exception as e:
            popup(f"Erro ao baixar atualização: {e}")
            raise
