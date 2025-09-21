from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify
import sys, os
caminho_pai = os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir))
import base64
# Adiciona o caminho pai à lista de caminhos de importação do Python
sys.path.append(caminho_pai)

import connections, mail


app = Flask(__name__)
# É importante configurar uma chave secreta para usar 'flash messages'
app.secret_key = 'sua_chave_secreta_aqui'

# --- ROTAS DE AUTENTICAÇÃO ---


@app.route('/')
def login():
    """ Rota para a tela de login. """
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def do_login():
    """ Processa os dados do formulário de login. """
    # Lógica de autenticação viria aqui.
    # Por enquanto, vamos apenas redirecionar para o menu principal.
    login = request.form.get('login')
    senha = request.form.get('senha')
    # Exemplo de validação simples
    
    conn = connections.criar_banco_dados()

    if login and senha:
        # Se o login for bem-sucedido, redireciona
        resp,user = connections.login(conn,login,senha)
        
        if resp:
            session["nome_user"] = user[0]
            session["email_user"] = user[1]
            flash('Logado com sucesso!', 'success')
            return redirect(url_for('menu_principal'))
        else:
            flash('Login ou senha inválidos!', 'error')
            return redirect(url_for('login'))
    else:
        # Se falhar, exibe uma mensagem de erro
        flash('Login ou senha inválidos!', 'error')
        return redirect(url_for('login'))

@app.route('/cadastro')
def cadastro():
    """ Rota para a tela de cadastro. """
    return render_template('cadastro.html')

# Lembre-se que sua função no Flask deve estar assim:
@app.route('/enviar_por_chave_privada', methods=['POST'])
def envio_chave_privada():
    msg = request.form.get('msg')
    email_dest = request.form.get('destinatario')
    key_type = request.form.get('chave')

    conn = connections.criar_banco_dados()

    print(f"Recebido: msg='{msg}', dest='{email_dest}', chave='{key_type}'")

    if key_type == "publica":
        chave = None
        chave = connections.pegar_chave_publica(conn, email_dest)

        if chave == None:
            flash(f'Erro: Não há chave pública registrada', 'error')
            return redirect(url_for('enviar_mensagem'))
        chave = base64.b64decode(chave)
        if chave != None:
            connections.criptografar_publica(session["nome_user"], msg, email_dest, chave)
            flash(f'Mensagem Criptografada enviada para {email_dest}', 'success')
            print(f"Mensagem Criptografada enviada para {email_dest}")
        else:
            print("Não foi possivel encontra a Chave Pública!")
        # enviar_publica(msg,dest)

    elif key_type == "privada":
        chave = None
        chave = connections.verificar_chave(conn, session["email_user"], email_dest)

        if chave == None:
            flash(f'Erro: Não há chave privada cadastrada para {email_dest}', 'error')
            return redirect(url_for('enviar_mensagem'))
        if chave != None:
            connections.criptografar(session["nome_user"], msg, email_dest, chave)
            flash(f'Mensagem Criptografada enviada para {email_dest}', 'success')
            print(f"Mensagem Criptografada enviada para {email_dest}")
        # enviar_privada(msg,dest)
    
    # Adicione um retorno, como um redirecionamento
    #flash("Mensagem enviada!")
    
    return redirect(url_for('enviar_mensagem'))

@app.route('/cadastrar', methods=['POST'])
def do_cadastro():
    """ Processa os dados do formulário de cadastro. """
    # Lógica para salvar o novo usuário no banco de dados viria aqui.
    nome = request.form.get('nome')
    email = request.form.get('email')
    senha = request.form.get('senha')

    conn = connections.criar_banco_dados()
    cursor = conn.cursor()
    cursor.execute(f"SELECT nome, email FROM usuarios WHERE email = '{email}'")
    results = cursor.fetchall()
    if len(results) > 0:
        flash(f'Email ja cadastrado, por favor insira um email diferente', 'error')
        return redirect(url_for('cadastro'))

    if nome and email and senha:
        # Se o cadastro for bem-sucedido, redireciona para o login
        flash(f'Cadastro realizado com sucesso!', 'success')
        connections.cadastro(conn,nome,email,senha)
        return redirect(url_for('login'))
    else:
        print('Todos os campos são obrigatórios.', 'error')
        return redirect(url_for('cadastro')) 

@app.route('/desconectar')
def desconectar():
    """ Rota para fazer logout do usuário. """
    # Lógica de logout (limpar a sessão) viria aqui.
    return redirect(url_for('login'))


# --- ROTAS DO MENU PRINCIPAL E FUNCIONALIDADES ---

@app.route('/menu')
def menu_principal():
    """ Rota para o menu principal da aplicação. """
    # O nome de usuário viria da sessão do usuário logado.
    usuario = session["nome_user"] 
    return render_template('menu_principal.html', usuario=usuario)

@app.route('/chave_privada')
def cadastrar_chave_privada():
    """ Rota para a tela de gerenciamento de chaves. """
    usuario = session["nome_user"]
    conn = connections.criar_banco_dados()
    cursor = conn.cursor()
    cursor.execute(f"SELECT nome, email FROM usuarios WHERE email != '{session["email_user"]}'")
    x = cursor.fetchall()
    lista_contatos = []
    for user in x:
        usuari = {'nome': user[0], 'email': user[1]}
        lista_contatos.append(usuari)
    return render_template('cadastrar_chave.html', usuario=usuario, contatos=lista_contatos)

@app.route('/criar_chave', methods=['POST'])
def criar_chave():
    usuario = session["nome_user"]
    conn = connections.criar_banco_dados()

    nome_d = request.form.get('nome_d')
    email_d = request.form.get('destinatario')

    if not email_d:
        flash('Erro: Nenhum destinatário foi selecionado.', 'error')
        return redirect(url_for('cadastrar_chave_privada')) # Redireciona de volta em caso de erro

    connections.criar_chave(conn, session["email_user"], email_d)
    
    # CORREÇÃO 3: Usar redirect após um POST bem-sucedido
    flash(f'Chave para {nome_d} criada com sucesso!', 'success')
    return redirect(url_for('cadastrar_chave_privada'))

@app.route('/enviar')
def enviar_mensagem():
    """ Rota para a tela de envio de mensagens. """
    usuario = session["nome_user"] 
    conn = connections.criar_banco_dados()
    cursor = conn.cursor()
    cursor.execute(f"SELECT nome, email FROM usuarios WHERE email != '{session["email_user"]}'")
    x = cursor.fetchall()
    lista_contatos = []
    for user in x:
        usuari = {'nome': user[0], 'email': user[1]}
        lista_contatos.append(usuari)
        
    return render_template('enviar_mensagem.html', usuario=usuario, contatos=lista_contatos)

@app.route('/descriptografar')
def descriptografar_mensagem():
    usuario = session["nome_user"] 
    conn = connections.criar_banco_dados()
    cursor = conn.cursor()
    cursor.execute(f"SELECT nome, email FROM usuarios WHERE email != '{session["email_user"]}'")
    x = cursor.fetchall()
    lista_contatos = []
    for user in x:
        usuari = {'nome': user[0], 'email': user[1]}
        lista_contatos.append(usuari)
        
    return render_template('descriptografar_mensagem.html', usuario=usuario, contatos=lista_contatos)

# ROTA 2: Recebe os dados para processar a descriptografia (via AJAX)
@app.route('/processar_descriptografia', methods=['POST'])
def processar_descriptografia():
    
    msg_criptografada = request.form.get('msg_criptografada')
    remetente_email = request.form.get('remetente')
    tipo_chave = request.form.get('tipo_chave')

    conn = connections.criar_banco_dados()

    if not msg_criptografada or not remetente_email or not tipo_chave:
        return redirect(url_for('menu_principal'))

    print(f"Recebido para descriptografar: remetente='{remetente_email}', tipo_chave='{tipo_chave}'")

    if tipo_chave == "publica":
        chave = None
        chave = connections.pegar_chave_privada(conn, session["email_user"])
        chave = base64.b64decode(chave)
        if chave != None:
            try:
                msg = mail.descriptografar_publica(msg_criptografada, chave)
            except:
                #flash("Erro no pareamento de chaves, essa mensagem não foi direcionada a você", 'error')
                return jsonify({'status': 'error', 'message': "Erro no pareamento de chaves, essa mensagem não foi direcionada a você"})  
        else:
            #flash("Erro no pareamento de chaves, essa você não possui uma chave cadastrada para esse usuario", 'error')
            return jsonify({'status': 'error', 'message': "Erro no pareamento de chaves, você não possui uma chave cadastrada para esse usuario"})
    elif tipo_chave == "privada":
        chave = None
        chave = connections.verificar_chave(conn, remetente_email, session["email_user"])
        if chave != None:
            try:
                msg = mail.descriptografar_privada(msg_criptografada, chave)
            except:
                #flash("Erro no pareamento de chaves, essa mensagem não foi direcionada a você", 'error')
                return jsonify({'status': 'error', 'message': "Erro no pareamento de chaves, essa mensagem não foi direcionada a você"})      
        else:
            #flash("Erro no pareamento de chaves, essa você não possui uma chave cadastrada para esse usuario", 'error')
            return jsonify({'status': 'error', 'message': "Erro no pareamento de chaves, você não possui uma chave cadastrada para esse usuario"})
    
    msg_descriptografada = f"Mensagem de {remetente_email} foi descriptografada!: \n\n{msg}"
    print(msg_descriptografada)
    return jsonify({'status': 'success', 'message': msg_descriptografada})
    #return redirect(url_for('descriptografar_mensagem'))

@app.route('/pesquisar')
def pesquisar_usuarios():
    """ Rota para a tela de pesquisa de usuários. """
    usuario = session["nome_user"] 
    # Exemplo de lista de usuários que viria de uma busca no banco
    usuarios_encontrados = [
        {'nome': 'Gian', 'email': 'gianbala83@gmail.com'},
        {'nome': 'Herlan', 'email': 'herlan.init@gmail.com'}
    ]
    return render_template('pesquisar_usuarios.html', usuario=usuario, usuarios=usuarios_encontrados)

if __name__ == '__main__':
    app.run(debug=True)