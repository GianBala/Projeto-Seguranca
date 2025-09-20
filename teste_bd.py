from connections import *
conn = sqlite3.connect('usuarios.db')

# Cria um objeto cursor. Ele permite executar comandos SQL.
cursor = conn.cursor()
cursor.execute("SELECT nome, email FROM usuarios")
x = cursor.fetchall()
print(x)