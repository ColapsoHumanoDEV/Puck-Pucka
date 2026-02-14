import requests
import os
import time

VERSAO_LOCAL_ARQUIVO = "version.txt"
URL_RAW_VERSION = f"https://raw.githubusercontent.com/ColapsoHumanoDEV/Puck-Pucka/main/version.txt?t={int(time.time())}"
URL_RAW_MAIN = f"https://raw.githubusercontent.com/ColapsoHumanoDEV/Puck-Pucka/main/Jogador/app.py?t={int(time.time())}"

def ler_versao_local():
    if os.path.exists(VERSAO_LOCAL_ARQUIVO):
        with open(VERSAO_LOCAL_ARQUIVO, "r") as f:
            return f.read().strip()
    return "0.0.0"

def atualizar_jogo(nova_versao, conteudo_novo):
    with open("app.py", "wb") as f:
        f.write(conteudo_novo)
    
    with open(VERSAO_LOCAL_ARQUIVO, "w") as f:
        f.write(nova_versao)
    
    print(f"ATUALIZADO: {nova_versao}")

def verificar_e_rodar():
    v_local = ler_versao_local()
    
    try:
        r = requests.get(URL_RAW_VERSION)
        if r.status_code == 200:
            v_online = r.text.strip()
            
            print(f"DEBUG: Local [{v_local}] | Online [{v_online}]")

            if v_online != v_local:
                print("Versao diferente detectada! Baixando...")
                r_main = requests.get(URL_RAW_MAIN)
                if r_main.status_code == 200:
                    atualizar_jogo(v_online, r_main.content)
                else:
                    print(f"Erro ao baixar main.py: {r_main.status_code}")
            else:
                print("Versoes sao iguais.")
        else:
            print(f"Erro ao conectar no GitHub: {r.status_code}")
    except Exception as e:
        print(f"Erro: {e}")

    print("--- Abrindo Jogo ---")
    os.system("python app.py")

if __name__ == "__main__":
    verificar_e_rodar()
