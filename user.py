import uuid
import hashlib
from typing import Optional

class Usuario:

    def __init__(self, login: str, senha: str, nome: str, public_key: Optional[str] = None, private_key: Optional[str] = None):
        self.id = str(uuid.uuid4())
        self.login = login
        self.senha_hash = self._gerar_hash_senha(senha)
        self.nome = nome
        self.public_key = public_key
        self.private_key = private_key
    
    @staticmethod
    def _gerar_hash_senha(senha: str) -> str:
        """
        Gera o hash SHA-256 de uma senha.
        
        Atenção: Para uso em produção, adicione um 'salt' e use uma função de hash mais robusta como Argon2, bcrypt ou scrypt.
        """
        return hashlib.sha256(senha.encode('utf-8')).hexdigest()

    def verificar_senha(self, senha: str) -> bool:
        """
        Verifica se a senha fornecida corresponde ao hash armazenado.
        
        Args:
        - senha (str): A senha a ser verificada.
        
        Returns:
        - bool: True se a senha for válida, False caso contrário.
        """
        return self._gerar_hash_senha(senha) == self.senha_hash

# --- Exemplo de uso da classe ---
if __name__ == '__main__':
    # Criando uma instância de Usuario
    usuario1 = Usuario(
        login="joaosilva", 
        senha="minhasenha123", 
        nome="João da Silva",
        public_key="ABC...XYZ",
        private_key="123...789"
    )

    # Acessando os atributos
    print(f"ID: {usuario1.id}")
    print(f"Login: {usuario1.login}")
    print(f"Nome: {usuario1.nome}")
    print(f"Senha (hash): {usuario1.senha_hash}")
    print(f"Chave Pública: {usuario1.public_key}")
    print(f"Chave Privada: {usuario1.private_key}")
    
    print("-" * 30)

    # Verificando a senha
    senha_correta = "minhasenha123"
    senha_incorreta = "senhainvalida"

    print(f"Verificando senha '{senha_correta}': {usuario1.verificar_senha(senha_correta)}")
    print(f"Verificando senha '{senha_incorreta}': {usuario1.verificar_senha(senha_incorreta)}")