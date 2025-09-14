from user import Usuario
import json
from os import *
from mail import *

def menu_entrada(arquivo_json : str):
    print("1 - Fazer Login")
    print("2 - Realizar Cadastro")
    print("\n")

    resp = input()

    match resp:
        case "1":
            menu_login_usuario(arquivo_json)
        case "2":
            menu_cadastro_usuario(arquivo_json)
        case _:
            print("Por favor, digite uma opção válida")
            input()
            system('cls')
            menu_entrada(arquivo_json)

def menu_login_usuario(arquivo_json : str):
    login = input("Login: ")
    
    try:
        with open(arquivo_json, 'r') as arquivo:
            usuarios = json.load(arquivo)

    except json.JSONDecodeError:
        print(f"\nErro: O arquivo '{arquivo_json}' está vazio ou tem formato inválido.")
        return False
    except IOError as e:
        print(f"\nErro ao ler o arquivo: {e}")
        return False
    
    user = None
    for usuario in usuarios:
        if usuario.login == login:
            user = usuario
            break    
    
    if user != None:
        senha = input("Senha: ")

        while senha != user.senha:
            print("Senha Incorreta\n")
            senha = input("Senha: ")

        menu_principal(user, arquivo_json)
    
    else:
        print("\nUsuário não cadastrado")
        input()
        system('cls')
        menu_login_usuario(arquivo_json)
    


def menu_cadastro_usuario(arquivo_json : str):
    login = input("Digite seu email: ")
    senha = input("Digite sua senha: ")
    nome = input("Digite seu nome de usuario: ")

    novo_usuario = Usuario(login,senha,nome)
    
    salvar_usuario(novo_usuario, arquivo_json)
    input()
    system('cls')
    menu_entrada(arquivo_json)

def menu_principal(usuario: Usuario, arquivo_json : str):
    print(f"Usuario: {usuario.nome}\n\n")
    print("1 - Cadastrar Chave")
    print("2 - Enviar Mensagem")
    print("3 - Descriptografar Mensagem")
    print("4 - Deletar Conta")
    print("5 - Deslogar")
    print("\n")

    resp = input()

    match resp:
        case "1":
            cadastrar_chave(usuario, arquivo_json)

        case "2":
            system('cls')
            enviar_msg(usuario, arquivo_json)

            input()

            system('cls')
            menu_principal(usuario,arquivo_json)

        case "3":
            print("descripta")

        case "4":
            apagar_resp = input("\nTem certeza que deseja apagar sua conta? (S/N)")
            if apagar_resp.lower() == "s":
                deletar_usuario(usuario,arquivo_json)
                input()
                system('cls')
                menu_cadastro_usuario()
            else:
                system('cls')
                menu_principal(usuario,arquivo_json)
        
        case "5":
            system('cls')
            menu_principal()

        case _:
            system('cls')
            menu_principal(usuario)


def cadastrar_chave(usuario: Usuario):
    print(f"Usuario: {usuario.nome}\n\n")
    print("1 - Cadastrar Chave Pública")
    print("2 - Cadastrar Chave Privada")

    resp = input()

def enviar_msg(usuario: Usuario):
    print(f"Usuario: {usuario.nome}\n\n")
    mostrar_usuarios()

    destinatario = input("Insira o email do destinatario: ")
            
    print("Digite sua mensagem:")
    msg = input()

    criptografar(usuario.nome, msg, destinatario, usuario.senha)

def mostrar_usuarios(arquivo_json : str):
    if path.exists(arquivo_json):
        usuarios = []
        try:
            with open(arquivo_json, 'r', encoding='utf-8') as arquivo:
                usuarios = json.load(arquivo)

        except json.JSONDecodeError:
            print(f"\nErro: O arquivo '{arquivo_json}' está vazio ou tem formato inválido.")
            return False
        except IOError as e:
            print(f"\nErro ao ler o arquivo: {e}")
            return False
        
        if len(usuarios) > 0:
            for i, user in usuarios:
                print("---------------------------------------")
                #print(f"Usuario N° {i}")
                print(f"Nome: {user["nome"]}")
                print(f"Email: {user["login"]}")
                print(f"Chave Publica: {user["public_key"]}")
                
        else:
            print("\nNenhum usuario cadastrado.")
            return False
        
    else:
        print(f"\n{arquivo_json} nao encontrado.")
        return False

def salvar_usuario(usuario : Usuario, arquivo_json : str):
    arquivo = open("usuarios_adusuarios_cadastrados.json", "r+")
    input()
    dados_usuario = {
            "id": usuario.id,
            "login": usuario.login,
            "nome": usuario.nome,
            "senha_hash": usuario.senha_hash,
            "public_key": usuario.public_key,
            "private_key": usuario.private_key
        }
    
    usuarios_existentes = []

    usuarios_existentes = json.load(arquivo)
        
    usuarios_existentes.append(dados_usuario)
    
    json.dump(usuarios_existentes, arquivo, indent=4, ensure_ascii=False)
    print(f"Cadastro atualizado com sucesso!")
    arquivo.close()
    
    #except IOError as e:
    #    print(f"Erro ao salvar o arquivo: {e}")

def deletar_usuario(usuario : Usuario, arquivo_json: str):
    
    if path.exists(arquivo_json):
        try:
            with open(arquivo_json, 'r', encoding='utf-8') as arquivo:
                usuarios = json.load(arquivo)
        
        except json.JSONDecodeError:
            print(f"\nErro: O arquivo '{arquivo_json}' está vazio ou tem formato inválido.")
            return False
        except IOError as e:
            print(f"\nErro ao ler o arquivo: {e}")
            return False

        usuarios_atualizados = [u for u in usuarios if u.get('login') != usuario["login"]]

        if len(usuarios_atualizados) == len(usuarios):
            print(f"\nUsuário com o login '{usuario["login"]}' não foi encontrado.")
            return False
        
        try:
            with open(arquivo_json, 'w', encoding='utf-8') as arquivo:
                json.dump(usuarios_atualizados, arquivo, indent=4, ensure_ascii=False)

            print(f"Conta deletada com sucesso!.")
            return True
        except IOError as e:
            print(f"Erro ao salvar o arquivo: {e}")
            return False
    
    else:
        print(f"Erro ao acessar {arquivo_json}")
        return False