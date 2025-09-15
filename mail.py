import base64
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.KDF import PBKDF2
from Crypto.Hash import SHA512

# Função de criptografia (MD5 / SHA256)

# Um função para o envio e-mail

# Envia via email criptografado


def enviar_email(body: str, subject: str, recipient_email: str) -> None:
    sender_email = "herlaninit2@gmail.com"
    sender_password = "kvwo fxcc cuyl jayq"
    
    #recipient_email = "gianbala83@gmail.com"
    #body = "Olha o carro da rua passando no seu ovo"
    #subject = "La ele 1000x"


    smtp_server = "smtp.gmail.com"
    smtp_port = 465
    server = smtplib.SMTP_SSL(smtp_server, smtp_port)
    server.login(sender_email, sender_password)
        
    # Configura a mensagem de e-mail
    msg = MIMEText(body)
    msg['Subject'] = subject
    msg['From'] = sender_email
    msg['To'] = recipient_email

    # Envia o e-mail
    server.sendmail(sender_email, recipient_email, msg.as_string())
    server.quit()
    print("E-mail enviado com sucesso!")


def gerar_chave(senha: str) -> bytes:
    # Um 'salt' aleatorio e gerado para cada chave, o que torna
    # os hashes de senhas identicas diferentes.

    salt = get_random_bytes(16)
    chave = PBKDF2(senha, salt, dkLen=32, count=100000, hmac_hash_module=SHA512)
    return salt + chave


def criptografar(sender: str, mensagem: str, destiny: str, senha: str) -> None:
    
    # Deriva a chave de criptografia a partir da senha
    salt_e_chave = gerar_chave(senha)
    salt = salt_e_chave[:16]
    chave = salt_e_chave[16:]

    # Converte a mensagem para bytes, que é o formato exigido pelo AES
    dados_em_bytes = mensagem.encode('utf-8')

    # Cria o objeto de criptografia AES
    cipher = AES.new(chave, AES.MODE_GCM)
    
    # Criptografa a mensagem e gera uma tag de autenticação
    ciphertext, tag = cipher.encrypt_and_digest(dados_em_bytes)
    
    #msg_crypt = (salt, cipher.nonce, tag, ciphertext)

    msg_crypt_text = salt + cipher.nonce + tag + ciphertext
    msg_crypt_text = base64.b64encode(msg_crypt_text).decode('utf-8')

    enviar_email(msg_crypt_text, f"Mensagem de :{sender}", destiny)


def descriptografar(mensagem_criptografada:str, senha: str) -> str:
    
    dados_bytes = base64.b64decode(mensagem_criptografada)
    
    salt = dados_bytes[:16]          # Primeiros 16 bytes
    nonce = dados_bytes[16:32]       # Proximos 16 bytes
    tag = dados_bytes[32:48]         # Proximos 16 bytes
    ciphertext = dados_bytes[48:]    # O restante

    
    # Deriva a chave novamente, usando o mesmo salt
    chave = PBKDF2(senha, salt, dkLen=32, count=100000, hmac_hash_module=SHA512)

    # Cria o objeto de descriptografia AES
    cipher = AES.new(chave, AES.MODE_GCM, nonce=nonce)
    
    # Descriptografa e verifica a autenticidade da mensagem
    try:
        dados_descriptografados = cipher.decrypt_and_verify(ciphertext, tag)
        return dados_descriptografados.decode('utf-8')
    except ValueError:
        return "Erro: Falha na autenticação. A mensagem ou a senha estão incorretas."


def test_stress():
    print("digite a msg para criptografar:")
    
    msg = input()
    destiny = "herlan.init@gmail.com"
    senha = "1234"
    criptografar("Giancarlo", msg, destiny, senha)
    print("SexSex")

    print("digite a msg para descriptografar:")
    msg_2 = input()
    msg_2 = msg_2.replace("\n", "")

    text = descriptografar(msg_2, senha)
    print(text)

if __name__ == "__main__":
    test_stress()