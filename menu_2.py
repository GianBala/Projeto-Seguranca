import string
import sqlite3
import hashlib
import secrets
import string
from mail import *
from os import system


def gerar_string_aleatoria_32():
    caracteres = string.ascii_letters + string.digits
    return ''.join(secrets.choice(caracteres) for _ in range(32))


def clean():
    # Se for rodar no Windows troque "clear" por "cls"
    system("clear")


def criar_banco_dados():
    try:
        # Conecta ao banco de dados (cria se não existir)
        conn = sqlite3.connect('usuarios.db')
        cursor = conn.cursor()
        
        # Cria a tabela de usuários
        cursor.execute('''
        CREATE TABLE IF NOT EXISTS usuarios (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            senha_hash TEXT NOT NULL,
            salt TEXT NOT NULL,
            data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
        '''
        )
        conn.commit()
        cursor.execute("""
        CREATE TABLE IF NOT EXISTS chaves (
            email_1 TEXT NOT NULL,
            email_2 TEXT NOT NULL,
            cnave_privada TEXT NOT NULL
        )
        """)
        conn.commit()
        print("Banco de dados e tabela criados com sucesso!")
        return conn
        
    except sqlite3.Error as error:
        print(f"Erro ao criar banco de dados: {error}")
        return None


def gerar_salt(tamanho=16):
    return secrets.token_hex(tamanho)


def hash_senha(senha, salt):
    senha_salt = senha + salt
    return hashlib.sha256(senha_salt.encode()).hexdigest()


def inserir_usuario(conn, nome, email, senha):
    try:
        cursor = conn.cursor()
        
        # Verifica se o email já existe
        cursor.execute("SELECT id FROM usuarios WHERE email = ?", (email,))
        if cursor.fetchone():
            print("Email já cadastrado!")
            return False
        
        # Gera salt e hash da senha
        salt = gerar_salt()
        senha_hash = hash_senha(senha, salt)
        
        # Insere o usuário
        cursor.execute('''
        INSERT INTO usuarios (nome, email, senha_hash ,salt)
        VALUES (?, ?, ?, ?)
        ''', (nome, email, senha_hash, salt))
        
        conn.commit()
        print("Usuário cadastrado com sucesso!")
        input()
        return True
        
    except sqlite3.Error as error:
        print(f"Erro ao inserir usuário: {error}")
        return False


def login(conn, email, senha):
    try:
        cursor = conn.cursor()
        
        # Busca o usuário pelo email
        cursor.execute(f"SELECT nome, email, senha_hash, salt FROM usuarios WHERE email = '{email}'")
        resultado = cursor.fetchone()
        
        if not resultado:
            print("Usuário não encontrado!")
            return False
        
        nome, email, senha_hash_armazenado, salt = resultado
        
        # Gera o hash da senha fornecida com o salt armazenado
        senha_hash_tentativa = hash_senha(senha, salt)
        
        # Compara os hashes
        if senha_hash_tentativa == senha_hash_armazenado:
            print("Login bem-sucedido!")
            menu_usuario(conn, nome, email)
        else:
            print("Senha incorreta!")
            return False
            
    except sqlite3.Error as error:
        print(f"Erro ao verificar login: {error}")
        return False


def listar_usuarios(conn):
    """Lista todos os usuários (apenas para demonstração)"""
    try:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, email FROM usuarios")
        usuarios = cursor.fetchall()
        
        print("\n Lista de Usuários:")
        print("-" * 50)
        for usuario in usuarios:
            print(f"ID: {usuario[0]}, Nome: {usuario[1]}, Email: {usuario[2]}")
        print("-" * 50)
        input()
        
    except sqlite3.Error as error:
        print(f"Erro ao listar usuários: {error}")


def criar_chave(conn, email_1, email_2) -> None:
    chave = gerar_string_aleatoria_32()
    
    try:
        cursor = conn.cursor()
        cursor.execute(f"INSERT into chaves (email_1, email_2, cnave_privada) VALUES ('{email_1}', '{email_2}', '{chave}')")
        conn.commit()
        print("Chave Cadastrada com Sucesso!")
        input()
    
    except:
        return None


def verificar_chave(conn, email_1: str, email_2: str) -> str:
    try:
        cursor = conn.cursor()
        cursor.execute(f"SELECT cnave_privada FROM chaves WHERE email_1 = '{email_1}' AND email_2 = '{email_2}'")
        resultado = cursor.fetchone()
        
        if not resultado:
            print("Chave para esse Usuário não encontrada!")
            return None

        return resultado[0]
    
    except:
        return None


def menu_usuario(conn, nome: str, email: str) -> None:
    while True:
        clean()
        print("\n" + "="*70)
        print("MEN USUÁRIO")
        print("="*70)
        print("1. Criar Chave Privada")
        print("2. Enviar Mensagem")
        print("3. Descriptografar Mensagens")
        print("4. Sair")
        print("="*70)
        option = int(input())

        if option == 1:
            print("Digite o email para criar a chave: ")
            email_2 = input()
            criar_chave(conn, email, email_2)
        elif option == 2:
            print("Inserir Mensagem para Criptografar: ")
            msg = input()
            print("Insira o email do destinatário:")
            d_email = input()

            # Verificar se existe uma chave para esses usuarios
            chave = None
            chave = verificar_chave(conn, email, d_email)
            if chave != None:
                criptografar(nome, msg, d_email, chave)
                print(f"Mensagem Criptografada enviada para {d_email}")
                input()
            else:
                print("Chave Privada não cadastrada!")
                input()
        
        elif option == 3:
            print("Inserir Mensagem criptografada: ")
            msg_cryp = input()
            print("Digie o email do remetente")
            r_email = input()
            chave = None
            chave = verificar_chave(conn, r_email, email)
            if chave != None:
                msg = descriptografar(msg_cryp, chave)
                print(msg)
                input()
            else:
                print("Não existe chave entre você e esse usuário")
                input()
        
        elif option == 4:
            return


def menu():
    """Menu interativo"""
    conn = criar_banco_dados()
    if not conn:
        return
    
    while True:
        clean()
        print("\n" + "="*70)
        print("MENU PRINCIPAL")
        print("="*70)
        print("1. Cadastrar novo usuário")
        print("2. Fazer login")
        print("3. Listar usuários")
        print("4. Sair")
        print("="*70)
        
        opcao = input("Escolha uma opção: ").strip()
        
        if opcao == "1":
            print("\nCADASTRAR USUÁRIO")
            nome = input("Nome: ").strip()
            email = input("Email: ").strip().lower()
            senha = input("Senha: ").strip()
            
            if nome and email and senha:
                inserir_usuario(conn, nome, email, senha)
            else:
                print("Preencha todos os campos!")
                
        elif opcao == "2":
            print("\nLOGIN")
            email = input("Email: ").strip().lower()
            senha = input("Senha: ").strip()
            
            login(conn, email, senha)
            
            
        elif opcao == "3":
            listar_usuarios(conn)
            
        elif opcao == "4":
            print("Saindo do sistema...")
            break
            
        else:
            print("Opção inválida!")
    
    conn.close()

# Execução direta
if __name__ == "__main__":
    menu()