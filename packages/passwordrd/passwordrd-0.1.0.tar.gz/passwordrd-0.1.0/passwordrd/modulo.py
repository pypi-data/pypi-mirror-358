class SetPassRD:
    def __init__(self, senha_correta: str):
        self.senha_correta = senha_correta

    def eval(self, codigo: str, linha: int, caractere: int, senha: str = None):
        """
        Executa o código via eval() após validar a senha.
        Recebe código, linha e caractere para erros mais precisos.

        Args:
            codigo (str): Código para executar.
            linha (int): Linha do código para mensagem de erro.
            caractere (int): Posição do caractere para mensagem de erro.
            senha (str): Senha para validar execução.

        Retorna:
            Resultado da avaliação do código.

        Raises:
            PermissionError: Se senha inválida.
            RuntimeError: Erros na execução do código, com detalhes.
        """
        if senha != self.senha_correta:
            raise PermissionError("Senha incorreta. Execução negada.")

        try:
            # Segurança: restringe builtins vazios.
            resultado = eval(codigo, {"__builtins__": {}})
            return resultado
        except Exception as e:
            msg_erro = f"Erro ao executar código na linha {linha}, caractere {caractere}: {e}"
            raise RuntimeError(msg_erro)
