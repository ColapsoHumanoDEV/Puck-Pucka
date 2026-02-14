import customtkinter as ctk
import time, sqlite3, requests, os  

# // Configurações

pasta_sql = 'SQL'
caminho_db = os.path.join(pasta_sql, 'config.db')

if not os.path.exists(pasta_sql):
    os.makedirs(pasta_sql)

conexaoConfig = sqlite3.connect(caminho_db, check_same_thread=False)
cursorConfig = conexaoConfig.cursor()

cursorConfig.execute("""
CREATE TABLE IF NOT EXISTS configs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    sessao INTEGER NOT NULL UNIQUE
    )
""")

cursorConfig.execute("SELECT sessao FROM configs WHERE id = 1")
resultado = cursorConfig.fetchone()

sessionNumber = 0

# // Sessão

pasta_sql = 'SQL'
caminho_db = os.path.join(pasta_sql, 'session.db')

if not os.path.exists(pasta_sql):
    os.makedirs(pasta_sql)

conexaoSession = sqlite3.connect(caminho_db, check_same_thread=False)
cursorSession = conexaoSession.cursor()

cursorSession.execute("""
CREATE TABLE IF NOT EXISTS sessões (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token INTEGER NOT NULL UNIQUE
)
""")

cursorSession.execute("SELECT token FROM sessões")
resultado = cursorSession.fetchone()

for token in cursorSession.execute("SELECT token FROM sessões"):
    url = 'http://127.0.0.1:5000/'
    tipo_envio = "Verificar Token"
        
    dados = {
        "tipo": tipo_envio,
        "token": token[0]
    }
    try:
        response = requests.post(url, json=dados)
        resposta = response.json()
        if resposta.get("valido") == "True":
            print("Sessão válida encontrada:", token[0])
            sessionNumber = token[0]
        else:
            print("Sessão inválida encontrada:", token[0])
            cursorSession.execute("DELETE FROM sessões WHERE token = ?", (token[0],))
            conexaoSession.commit()
            sessionNumber = None
    except Exception as e:
        print("Erro ao verificar sessão no Cliente:", e)
        
if sessionNumber and sessionNumber is not None and isinstance(sessionNumber, int):
    cursorConfig.execute("SELECT id FROM configs WHERE sessao = ?", (sessionNumber,))
    resultado = cursorConfig.fetchone()

    if resultado is None:
        cursorConfig.execute("DELETE FROM configs WHERE sessao != ?", (sessionNumber,))
        cursorConfig.execute("INSERT INTO configs (sessao) VALUES (?)", (sessionNumber,))
        conexaoConfig.commit()
        print("Sessão salva no banco de dados.")
    else:
        print("Sessão já existe no banco de dados.")
else:
    sessionNumber = None
    print("Nenhuma sessão válida encontrada. Por favor, faça login.")


# // Variaveis
interface = "Login"
interfaceAtual = ""
tela_cheia = False
Guis = {}

# // Conta da Sessão Atual

usuario = ""
nametag = ""

# // Configurações
ctk.set_appearance_mode('dark')

jogo = ctk.CTk()
jogo.title('Puck Pucka')

if tela_cheia:
    jogo.update_idletasks()
    jogo.overrideredirect(True)
    jogo.geometry(f"{jogo.winfo_screenwidth()}x{jogo.winfo_screenheight()}+0+0")
    jogo.bind("<Escape>", lambda e: jogo.destroy())
else:
    jogo.state('zoomed')

    # // Interfaces Globais

def mudarInterface(interface2):
    global interfaceAtual, interface, Guis
    if not interfaceAtual == interface2:
        interface = interface2
        print("Interface atualizada para:", interface2)
        atualizarInterface() # Chama a atualização visual

# // Interface de Login/Cadastro
def mudarLoginOuCadastro():
    global interface
    # Alterna o estado da variável
    if interface == "Login":
        interface = "Cadastro"
    else:
        interface = "Login"
    
    atualizarInterface() # Executa a limpeza e redesenha

def loginOucadastro():
    global interfaceAtual, interface, Guis

    if interface == "Login" or interface == "Cadastro":
        usuario = Guis["Usuario"].get()
        senha = Guis["Senha"].get()

        url = 'http://127.0.0.1:5000/'
        tipo_envio = "Entrar na Conta" if interface == "Login" else "Criar Conta"
        
        dados = {
            "tipo": tipo_envio,
            "usuario": str(usuario), # Corrigido: parênteses em vez de colchetes
            "senha": str(senha)    # Corrigido: parênteses em vez de colchetes
        }
        try:
            response = requests.post(url, json=dados)
            resposta = response.json()
            if resposta.get("valido") == "True":
                token = resposta.get("token")
                if interface == "Cadastro":
                    mudarInterface("Login")
                if interface == "Login":
                    print(resposta.get("mensagem"))
                    cursorSession.execute("INSERT INTO sessões (token) VALUES (?)", (token,))
                    conexaoSession.commit()
                    cursorConfig.execute("INSERT OR REPLACE INTO configs (id, sessao) VALUES (1, ?)", (token,))
                    conexaoConfig.commit()
                    global sessionNumber
                    sessionNumber = token
                    print("Sessão salva no banco de dados.")
                    mudarInterface("Carregamento-1")
                    print(f"{tipo_envio} com sucesso!")
            else:
                print("Operação inválida!")
        except Exception as e:
            print("Erro ao fazer ação no Cliente:", e)

def atualizarInterface():
    global interfaceAtual, interface, Guis, sessionNumber

    interfaceAtual = interface
    for gui in Guis.values():
        gui.destroy()
    
    if interface == "Login":
        Guis["Fundo2"] = ctk.CTkFrame(jogo, width=700, height=900)
        Guis["Fundo2"].place(x=800, y=100)

        Guis["TextCommandForUser"] = ctk.CTkLabel(Guis["Fundo2"], text="Entre na sua Conta", 
                font=("Arial", 30, "bold"), 
                fg_color="transparent")
        Guis["TextCommandForUser"].place(x=220, y=30)

        Guis["TextU"] = ctk.CTkLabel(Guis["Fundo2"], text="Usuário:", 
                font=("Arial", 25, "bold"), 
                fg_color="transparent")
        Guis["TextU"].place(x=300, y=100)

        Guis["Usuario"] = ctk.CTkEntry(Guis["Fundo2"], width=300, height=50, font=("Arial", 30, "bold"))
        Guis["Usuario"].place(x=200, y=150)

        Guis["TextS"] = ctk.CTkLabel(Guis["Fundo2"], text="Senha:", 
                font=("Arial", 25, "bold"), 
                fg_color="transparent")
        Guis["TextS"].place(x=300, y=250)

        Guis["Senha"] = ctk.CTkEntry(Guis["Fundo2"], width=300, height=50, font=("Arial", 30, "bold"), show="*")
        Guis["Senha"].place(x=200, y=300)

        Guis["Action"] = ctk.CTkButton(Guis["Fundo2"], width=300, height=50, font=("Arial", 30, "bold"), text="Entrar", command=loginOucadastro)
        Guis["Action"].place(x=200, y=400)
        
        Guis["Mudar"] = ctk.CTkButton(Guis["Fundo2"], width=300, height=50, font=("Arial", 30, "bold"), text="Cadastra-se", command=mudarLoginOuCadastro)
        Guis["Mudar"].place(x=200, y=550)

    elif interface == "Cadastro":
        Guis["Fundo2"] = ctk.CTkFrame(jogo, width=700, height=900)
        Guis["Fundo2"].place(x=800, y=100)

        Guis["TextCommandForUser"] = ctk.CTkLabel(Guis["Fundo2"], text="Cadastre-se para Jogar", 
                font=("Arial", 30, "bold"), 
                fg_color="transparent")
        Guis["TextCommandForUser"].place(x=220, y=30)

        Guis["TextU"] = ctk.CTkLabel(Guis["Fundo2"], text="Usuário:", 
                font=("Arial", 25, "bold"), 
                fg_color="transparent")
        Guis["TextU"].place(x=300, y=100)

        Guis["Usuario"] = ctk.CTkEntry(Guis["Fundo2"], width=300, height=50, font=("Arial", 30, "bold"))
        Guis["Usuario"].place(x=200, y=150)

        Guis["TextS"] = ctk.CTkLabel(Guis["Fundo2"], text="Senha:", 
                font=("Arial", 25, "bold"), 
                fg_color="transparent")
        Guis["TextS"].place(x=300, y=250)

        Guis["Senha"] = ctk.CTkEntry(Guis["Fundo2"], width=300, height=50, font=("Arial", 30, "bold"), show="*")
        Guis["Senha"].place(x=200, y=300)

        Guis["Action"] = ctk.CTkButton(Guis["Fundo2"], width=300, height=50, font=("Arial", 30, "bold"), text="Cadastrar", command=loginOucadastro)
        Guis["Action"].place(x=200, y=400)
        
        Guis["Mudar"] = ctk.CTkButton(Guis["Fundo2"], width=300, height=50, font=("Arial", 30, "bold"), text="Logar", command=mudarLoginOuCadastro)
        Guis["Mudar"].place(x=200, y=550)
    elif interface == "Carregamento-1":
        Guis["TextCommandForUser"] = ctk.CTkLabel(jogo, text="Carregando o Jogo...", 
                font=("Arial", 30, "bold"), 
                fg_color="transparent")
        Guis["TextCommandForUser"].place(x=1000, y=700)
        for i2 in range(13):
            Guis["TextCommandForUser"].configure(text=f"Carregando o Jogo...")
            if i2 == 0 or i2 == 4 or i2 == 7 or i2 == 10:
                Guis["TextCommandForUser"].configure(text=f"Carregando o Jogo.")
            elif i2 == 1 or i2 == 5 or i2 == 8 or i2 == 11:
                Guis["TextCommandForUser"].configure(text=f"Carregando o Jogo..")
            elif i2 == 2 or i2 == 6 or i2 == 9:
                Guis["TextCommandForUser"].configure(text=f"Carregando o Jogo...")
            elif i2 == 12:
                mudarInterface("Lobby")
            jogo.update()
            time.sleep(0.5)
    elif interface == "Lobby":
        
        # // Barra Superior

        Guis["Bar"] = ctk.CTkFrame(jogo, width=2000, height=100, fg_color="gray20")
        Guis["Bar"].place(x=0, y=0)

        abaAtual = "JogarFrame"

        LobbyButtons = ["Loja", "Jogar", "Configurações", "Perfil", "Amizades", "Pedidos", "Adicionar Amigo"]

        for i, button in enumerate(LobbyButtons):
            nome_aba = button + "Frame"
    
            Guis[f"LobbyButton{i}"] = ctk.CTkButton(
            Guis["Bar"], 
            width=200, 
            height=50, 
            font=("Arial", 30, "bold"), 
            text=button, 
            command=lambda b=nome_aba: mudarAba(b)
            )
    
            Guis[f"LobbyButton{i}"].place(x=20 + i*200, y=30)
            
        def mudarAba(aba):
            for obj in Guis:
                if not "Bar" in obj and not any("LobbyButton" + str(i) in obj for i in range(len(LobbyButtons))):
                    Guis[obj].destroy()
            abaAtual = aba
            if aba == "ConfiguraçõesFrame":
                print("Configurações abertas")
            elif aba == "LojaFrame":
                print("Loja aberta")
            elif aba == "JogarFrame":
                print("Jogar aberto")
            elif aba == "PerfilFrame":
                print("Perfil aberto")
            elif aba == "AmizadesFrame":
                Guis["AmizadesFrame"] = ctk.CTkFrame(jogo, width=500, height=900)
                Guis["AmizadesFrame"].place(x=400, y=100)

                Guis["Amizades-List"] = ctk.CTkScrollableFrame(Guis["AmizadesFrame"], width=600, height=700)
                Guis["Amizades-List"].place(x=50, y=100)
                def removerAmizade(a, i):
                    tipo_envio = "Remover Amizade"
                    print(f"Remover amizade de {a}")
                    dados = {
                        "tipo": tipo_envio,  
                        "token": sessionNumber if sessionNumber and sessionNumber is not None else None,
                        "amigo_id": a
                    }
                    try:
                        response = requests.post(url, json=dados)
                        resposta = response.json()
                        if resposta.get("valido") == "True":
                            Guis[f"Amizade{i}"].destroy()
                            Guis[f"RemoverAmizade{i}"].destroy()
                        else:
                            print("Algo deu errado ao remover amizade!")
                    except Exception as e:
                        print("Erro ao fazer ação no Cliente:", e)
                url = 'http://127.0.0.1:5000/'
                tipo_envio = "CarregarAmizades" if interface == "Lobby" and abaAtual == "AmizadesFrame" else "Mandando no Lugar errado"

                dados = {
                    "tipo": tipo_envio,  
                    "token": sessionNumber if sessionNumber and sessionNumber is not None else None
                }
                try:
                    response = requests.post(url, json=dados)
                    resposta = response.json()
                    if resposta.get("valido") == "True":
                        amizades = resposta.get("amizades")
                        for i, amizade in enumerate(amizades):
                            Guis[f"Amizade{i}"] = ctk.CTkLabel(Guis["Amizades-List"], text=amizade, 
                                    font=("Arial", 20, "bold"), 
                                    fg_color="transparent")
                            Guis[f"Amizade{i}"].pack(pady=10)
                            Guis[f"RemoverAmizade{i}"] = ctk.CTkButton(Guis["Amizades-List"], width=100, height=30, font=("Arial", 15, "bold"), text="Remover Amizade", command=lambda a=amizade: removerAmizade(a, i))
                            Guis[f"RemoverAmizade{i}"].pack(pady=5)
                    else:
                        print("Algo deu errado ao carregar amizades!")
                    
                except Exception as e:
                    print("Erro ao fazer ação no Cliente:", e)
            elif aba == "PedidosFrame":
                Guis["PedidosFrame"] = ctk.CTkFrame(jogo, width=500, height=900)
                Guis["PedidosFrame"].place(x=400, y=100)

                Guis["Pedidos-List"] = ctk.CTkScrollableFrame(Guis["PedidosFrame"], width=600, height=700)
                Guis["Pedidos-List"].place(x=50, y=100)

                def aceitarPedido(pedido, button, i):
                    tipo_envio = "Aceitar Amizade"
                    print(f"Aceitar pedido de {pedido}")
                    dados = {
                        "tipo": tipo_envio,  
                        "token": sessionNumber if sessionNumber and sessionNumber is not None else None,
                        "amigo_id": pedido
                    }
                    try:
                        response = requests.post(url, json=dados)
                        resposta = response.json()
                        if resposta.get("valido") == "True":
                            Guis[f"PedidoAceitar{i}"].destroy()
                            Guis[f"PedidoRecusar{i}"].destroy()
                            Guis[f"Pedido{i}"].destroy()
                        else:
                            print("Algo deu errado ao carregar pedidos!")
                    except Exception as e:
                        print("Erro ao fazer ação no Cliente:", e)
                def recusarPedido(pedido, button, i):
                    tipo_envio = "Recusar Amizade"
                    print(f"Recusar pedido de {pedido}")
                    dados = {
                        "tipo": tipo_envio,  
                        "token": sessionNumber if sessionNumber and sessionNumber is not None else None,
                        "amigo_id": pedido
                    }
                    try:
                        response = requests.post(url, json=dados)
                        resposta = response.json()
                        if resposta.get("valido") == "True":
                            Guis[f"PedidoAceitar{i}"].destroy()
                            Guis[f"PedidoRecusar{i}"].destroy()
                            Guis[f"Pedido{i}"].destroy()
                        else:
                            print("Algo deu errado ao carregar pedidos!")
                    except Exception as e:
                        print("Erro ao fazer ação no Cliente:", e)

                url = 'http://127.0.0.1:5000/'
                tipo_envio = "Pedidos de Amizade" if interface == "Lobby" and abaAtual == "PedidosFrame" else "Mandando no Lugar errado"

                dados = {
                    "tipo": tipo_envio,  
                    "token": sessionNumber if sessionNumber and sessionNumber is not None else None
                }
                try:
                    response = requests.post(url, json=dados)
                    resposta = response.json()
                    if resposta.get("valido") == "True":
                        pedidos = resposta.get("pedidos")
                        for i, pedido in enumerate(pedidos):
                            Guis[f"Pedido{i}"] = ctk.CTkLabel(Guis["Pedidos-List"], text=pedido, 
                                    font=("Arial", 20, "bold"), 
                                    fg_color="transparent")
                            Guis[f"Pedido{i}"].pack(pady=10)
                            Guis[f"PedidoAceitar{i}"] = ctk.CTkButton(Guis["Pedidos-List"], width=100, height=30, font=("Arial", 15, "bold"), text="Aceitar", command=lambda p=pedido: aceitarPedido(p, Guis[f"PedidoAceitar{i}"], i))
                            Guis[f"PedidoAceitar{i}"].pack(pady=5)
                            Guis[f"PedidoRecusar{i}"] = ctk.CTkButton(Guis["Pedidos-List"], width=100, height=30, font=("Arial", 15, "bold"), text="Recusar", command=lambda p=pedido: recusarPedido(p, Guis[f"PedidoRecusar{i}"], i))
                            Guis[f"PedidoRecusar{i}"].pack(pady=5)
                    else:
                        print("Algo deu errado ao carregar pedidos!")
                    
                except Exception as e:
                    print("Erro ao fazer ação no Cliente:", e)
            elif aba == "Adicionar AmigoFrame":
                print("Adicionar Amizade aberto")
                def adicionarAmigo():
                    url = 'http://127.0.0.1:5000/'
                    tipo_envio = "Adicionar Amigo" if interface == "Lobby" and abaAtual == "Adicionar AmigoFrame" else "Mandando no Lugar errado"
                    
                    amigo_id = Guis["BuscarAmigo"].get()

                    print(f"Tentando adicionar amigo com ID: {amigo_id}")
                    print(f"Token da sessão: {sessionNumber}")

                    dados = {
                        "tipo": tipo_envio,  
                        "token": sessionNumber if sessionNumber and sessionNumber is not None else None,
                        "amigo_id": amigo_id
                    }
                    try:
                        response = requests.post(url, json=dados)
                        resposta = response.json()
                        if resposta.get("valido") == "True":
                            print("Amigo adicionado com sucesso!")
                        else:
                            print("Algo deu errado ao adicionar amigo!")
                    except Exception as e:
                        print("Erro ao fazer ação no Cliente:", e)
                    
                Guis["Adicionar AmigoFrame"] = ctk.CTkFrame(jogo, width=500, height=900)
                Guis["Adicionar AmigoFrame"].place(x=400, y=100)

                Guis["BuscarAmigo"] = ctk.CTkEntry(Guis["Adicionar AmigoFrame"], width=500, height=50, font=("Arial", 30, "bold"))
                Guis["BuscarAmigo"].place(x=50, y=100)

                Guis["AdicionarAmigoButton"] = ctk.CTkButton(Guis["Adicionar AmigoFrame"], width=500, height=50, font=("Arial", 30, "bold"), text="Adicionar Amigo", command=lambda: adicionarAmigo())
                Guis["AdicionarAmigoButton"].place(x=100, y=100)
                
                
        mudarAba("JogarFrame")




# // Verificar sessão

if sessionNumber is not None and sessionNumber is not None and isinstance(sessionNumber, int):
    print("Sessão carregada e encontrada com sucesso!")
    mudarInterface("Carregamento-1")

atualizarInterface()
jogo.mainloop()