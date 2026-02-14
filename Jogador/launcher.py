import requests
import os

VERSAO_LOCAL_ARQUIVO = "version.txt"
URL_RAW_VERSION = "https://raw.githubusercontent.com/ColapsoHumanoDEV/Puck-Pucka/main/version.txt"
URL_RAW_MAIN = "https://raw.githubusercontent.com/ColapsoHumanoDEV/Puck-Pucka/main/main.py"

def ler_versao_local():
    if os.path.exists(VERSAO_LOCAL_ARQUIVO):
        with open(VERSAO_LOCAL_ARQUIVO, "r") as f:
            return f.read().strip()
    return "0.0.0"

def atualizar_jogo(nova_versao, conteudo_novo):
    with open("main.py", "wb") as f:
        f.write(conteudo_novo)
    
    with open(VERSAO_LOCAL_ARQUIVO, "w") as f:
        f.write(nova_versao)

def verificar_e_rodar():
    v_local = ler_versao_local()
    
    try:
        response_v = requests.get(URL_RAW_VERSION)
        if response_v.status_code == 200:
            v_online = response_v.text.strip()
            
            if v_online > v_local:
                response_main = requests.get(URL_RAW_MAIN)
                if response_main.status_code == 200:
                    atualizar_jogo(v_online, response_main.content)
    except:
        pass

    os.system("python app.py")

if __name__ == "__main__":
    verificar_e_rodar()