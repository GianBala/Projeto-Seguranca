from connections import *
conn = sqlite3.connect('usuarios.db')

# Cria um objeto cursor. Ele permite executar comandos SQL.
cursor = conn.cursor()
cursor.execute("SELECT nome, email FROM usuarios WHERE email = 'gianbala83@gmail.com'")
x = cursor.fetchall()
print(x)