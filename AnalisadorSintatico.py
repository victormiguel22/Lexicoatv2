from dataclasses import dataclass
from typing import List, Optional, Any

try:
    from AnalisadorLexico import AnalisadorLexico, Token, TipoToken
except ImportError:
    print("ERRO: Certifique-se de que AnalisadorLexico.py está no mesmo diretório!")
    exit(1)


# ============================================
# CLASSES DA ÁRVORE SINTÁTICA ABSTRATA (AST)
# ============================================

@dataclass
class NoAST:
    linha: int
    coluna: int


@dataclass
class Programa(NoAST):
    comandos: List[NoAST]

    def __str__(self):
        return f"Programa({len(self.comandos)} comandos)"


@dataclass
class DeclaracaoVariavel(NoAST):
    tipo: str
    nome: str
    tamanho_array: Optional[int] = None
    valor_inicial: Optional[NoAST] = None

    def __str__(self):
        array = f"[{self.tamanho_array}]" if self.tamanho_array is not None else ""
        init = f" = {self.valor_inicial}" if self.valor_inicial else ""
        return f"Declaracao({self.tipo}{array} {self.nome}{init})"


@dataclass
class DeclaracaoFuncao(NoAST):
    tipo_retorno: str
    nome: str
    parametros: List['Parametro']
    corpo: List[NoAST]

    def __str__(self):
        params = ", ".join(str(p) for p in self.parametros)
        return f"Funcao({self.tipo_retorno} {self.nome}({params}))"


@dataclass
class Parametro(NoAST):
    tipo: str
    nome: str

    def __str__(self):
        return f"{self.tipo} {self.nome}"


@dataclass
class Atribuicao(NoAST):
    nome: str
    expressao: NoAST

    def __str__(self):
        return f"Atribuicao({self.nome} = {self.expressao})"


@dataclass
class ComandoSe(NoAST):
    condicao: NoAST
    bloco_verdadeiro: List[NoAST]
    bloco_falso: Optional[List[NoAST]] = None

    def __str__(self):
        senao = " senao {...}" if self.bloco_falso else ""
        return f"Se({self.condicao}){senao}"


@dataclass
class ComandoEscreva(NoAST):
    expressao: NoAST

    def __str__(self):
        return f"Escreva({self.expressao})"


@dataclass
class ComandoLeia(NoAST):
    variavel: str

    def __str__(self):
        return f"Leia({self.variavel})"


@dataclass
class ExpressaoBinaria(NoAST):
    esquerda: NoAST
    operador: str
    direita: NoAST

    def __str__(self):
        return f"({self.esquerda} {self.operador} {self.direita})"


@dataclass
class Literal(NoAST):
    valor: Any
    tipo: str

    def __str__(self):
        if self.tipo == "cadeia":
            return f'"{self.valor}"'
        return str(self.valor)


@dataclass
class Identificador(NoAST):
    nome: str

    def __str__(self):
        return self.nome


# ============================================
# ERRO SINTÁTICO
# ============================================

@dataclass
class ErroSintatico:
    mensagem: str
    linha: int
    coluna: int
    token_encontrado: Optional[str] = None
    token_esperado: Optional[str] = None

    def __str__(self):
        msg = f"Erro sintático [linha {self.linha}, coluna {self.coluna}]: {self.mensagem}"
        if self.token_esperado:
            msg += f"\n  Esperado: {self.token_esperado}"
        if self.token_encontrado:
            msg += f"\n  Encontrado: {self.token_encontrado}"
        return msg


# ============================================
# ANALISADOR SINTÁTICO
# ============================================

class AnalisadorSintatico:
    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.posicao = 0
        self.erros: List[ErroSintatico] = []

    def token_atual(self) -> Token:
        if self.posicao < len(self.tokens):
            return self.tokens[self.posicao]
        return self.tokens[-1]

    def avancar(self) -> Token:
        token = self.token_atual()
        if self.posicao < len(self.tokens) - 1:
            self.posicao += 1
        return token

    def verificar(self, *tipos: TipoToken) -> bool:
        return self.token_atual().tipo in tipos

    def consumir(self, tipo: TipoToken, mensagem: str) -> Optional[Token]:
        if self.verificar(tipo):
            return self.avancar()
        token = self.token_atual()
        self.erros.append(ErroSintatico(
            mensagem,
            token.linha,
            token.coluna,
            token_encontrado=f"{token.tipo.value} '{token.lexema}'",
            token_esperado=tipo.value
        ))
        # Recuperação: avança para tentar continuar
        self.avancar()
        return None

    def analisar(self) -> Programa:
        comandos: List[NoAST] = []
        linha_inicio = 1
        coluna_inicio = 1

        if self.verificar(TipoToken.INICIO_BLOCO):
            t = self.avancar()
            linha_inicio = t.linha
            coluna_inicio = t.coluna

        while not self.verificar(TipoToken.FIM_ARQUIVO):
            if self.verificar(TipoToken.FIM_BLOCO):
                self.avancar()
                break

            cmd = self.comando()
            if cmd:
                comandos.append(cmd)

            # Se houve erro grave, pula até próximo comando possível
            if len(self.erros) > 0 and self.erros[-1].linha == self.token_atual().linha:
                while not self.verificar(
                    TipoToken.FIM_ARQUIVO, TipoToken.FIM_BLOCO,
                    TipoToken.TIPO_INTEIRO, TipoToken.TIPO_FLUTUANTE,
                    TipoToken.TIPO_LOGICO, TipoToken.TIPO_CADEIA,
                    TipoToken.IDENTIFICADOR, TipoToken.SE,
                    TipoToken.ESCREVA, TipoToken.LEIA
                ):
                    if self.verificar(TipoToken.FIM_ARQUIVO):
                        break
                    self.avancar()

        return Programa(linha=linha_inicio, coluna=coluna_inicio, comandos=comandos)

    def comando(self) -> Optional[NoAST]:
        if self.verificar(TipoToken.TIPO_INTEIRO, TipoToken.TIPO_FLUTUANTE,
                          TipoToken.TIPO_LOGICO, TipoToken.TIPO_CADEIA):
            return self.declaracao_variavel_ou_funcao()

        if self.verificar(TipoToken.SE):
            return self.comando_se()

        if self.verificar(TipoToken.ESCREVA):
            return self.comando_escreva()

        if self.verificar(TipoToken.LEIA):
            return self.comando_leia()

        if self.verificar(TipoToken.IDENTIFICADOR):
            return self.atribuicao()

        # Token inesperado
        token = self.token_atual()
        self.erros.append(ErroSintatico(
            "Comando inesperado",
            token.linha,
            token.coluna,
            token_encontrado=f"{token.tipo.value} '{token.lexema}'"
        ))
        self.avancar()
        return None

    def declaracao_variavel_ou_funcao(self) -> Optional[NoAST]:
        token_tipo = self.avancar()
        tipo = token_tipo.lexema
        linha = token_tipo.linha
        coluna = token_tipo.coluna

        token_nome = self.consumir(TipoToken.IDENTIFICADOR, "Esperado nome após tipo")
        if not token_nome:
            return None
        nome = token_nome.lexema

        tamanho_array = None
        if self.verificar(TipoToken.COLCHETE_ESQ):
            self.avancar()
            t_tam = self.consumir(TipoToken.INTEIRO, "Esperado tamanho do array")
            if t_tam:
                tamanho_array = int(t_tam.lexema)
            self.consumir(TipoToken.COLCHETE_DIR, "Esperado ']' após tamanho")

        if self.verificar(TipoToken.PARENTESE_ESQ):
            return self.declaracao_funcao(tipo, nome, linha, coluna)

        # Declaração de variável normal
        valor_inicial = None
        if self.verificar(TipoToken.ATRIBUICAO):
            self.avancar()
            valor_inicial = self.expressao()


        return DeclaracaoVariavel(
            linha=linha, coluna=coluna, tipo=tipo, nome=nome,
            tamanho_array=tamanho_array, valor_inicial=valor_inicial
        )

    def declaracao_funcao(self, tipo_retorno: str, nome: str, linha: int, coluna: int) -> DeclaracaoFuncao:
        self.consumir(TipoToken.PARENTESE_ESQ, "Esperado '(' após nome da função")

        parametros = []
        if not self.verificar(TipoToken.PARENTESE_DIR):
            parametros = self.lista_parametros()

        self.consumir(TipoToken.PARENTESE_DIR, "Esperado ')' após parâmetros")

        corpo = []
        if self.verificar(TipoToken.INICIO_BLOCO):
            self.avancar()
            while not self.verificar(TipoToken.FIM_BLOCO, TipoToken.FIM_ARQUIVO):
                cmd = self.comando()
                if cmd:
                    corpo.append(cmd)
            self.consumir(TipoToken.FIM_BLOCO, "Esperado 'fim' ao fechar função")
        else:
            cmd = self.comando()
            if cmd:
                corpo.append(cmd)

        return DeclaracaoFuncao(
            linha=linha, coluna=coluna,
            tipo_retorno=tipo_retorno, nome=nome,
            parametros=parametros, corpo=corpo
        )

    def lista_parametros(self) -> List[Parametro]:
        params = []
        while True:
            if not self.verificar(TipoToken.TIPO_INTEIRO, TipoToken.TIPO_FLUTUANTE,
                                  TipoToken.TIPO_LOGICO, TipoToken.TIPO_CADEIA):
                break
            token_tipo = self.avancar()
            tipo = token_tipo.lexema

            token_nome = self.consumir(TipoToken.IDENTIFICADOR, "Esperado nome do parâmetro")
            if not token_nome:
                break
            nome = token_nome.lexema

            params.append(Parametro(linha=token_tipo.linha, coluna=token_tipo.coluna, tipo=tipo, nome=nome))

            if not self.verificar(TipoToken.VIRGULA):
                break
            self.avancar()

        return params

    def atribuicao(self) -> Optional[Atribuicao]:
        token_nome = self.avancar()
        linha = token_nome.linha
        coluna = token_nome.coluna
        nome = token_nome.lexema

        self.consumir(TipoToken.ATRIBUICAO, "Esperado '=' após variável")
        expr = self.expressao()
        if expr is None:
            return None

        return Atribuicao(linha=linha, coluna=coluna, nome=nome, expressao=expr)

    def comando_se(self) -> Optional[ComandoSe]:
        token_se = self.avancar()
        linha = token_se.linha
        coluna = token_se.coluna

        self.consumir(TipoToken.PARENTESE_ESQ, "Esperado '(' após 'se'")
        cond = self.expressao()
        if cond is None:
            return None
        self.consumir(TipoToken.PARENTESE_DIR, "Esperado ')' após condição")

        if self.verificar(TipoToken.FACA):
            self.avancar()

        bloco_verdadeiro = []
        if self.verificar(TipoToken.INICIO_BLOCO):
            self.avancar()
            while not self.verificar(TipoToken.FIM_BLOCO, TipoToken.FIM_ARQUIVO, TipoToken.SENAO):
                cmd = self.comando()
                if cmd:
                    bloco_verdadeiro.append(cmd)
            self.consumir(TipoToken.FIM_BLOCO, "Esperado 'fim' após bloco 'se'")
        else:
            cmd = self.comando()
            if cmd:
                bloco_verdadeiro.append(cmd)

        bloco_falso = None
        if self.verificar(TipoToken.SENAO):
            self.avancar()
            bloco_falso = []
            if self.verificar(TipoToken.INICIO_BLOCO):
                self.avancar()
                while not self.verificar(TipoToken.FIM_BLOCO, TipoToken.FIM_ARQUIVO):
                    cmd = self.comando()
                    if cmd:
                        bloco_falso.append(cmd)
                self.consumir(TipoToken.FIM_BLOCO, "Esperado 'fim' após bloco 'senao'")
            else:
                cmd = self.comando()
                if cmd:
                    bloco_falso.append(cmd)

        return ComandoSe(linha=linha, coluna=coluna, condicao=cond,
                         bloco_verdadeiro=bloco_verdadeiro, bloco_falso=bloco_falso)

    def comando_escreva(self) -> Optional[ComandoEscreva]:
        token = self.avancar()
        self.consumir(TipoToken.PARENTESE_ESQ, "Esperado '(' após 'escreva'")
        expr = self.expressao()
        if expr is None:
            return None
        self.consumir(TipoToken.PARENTESE_DIR, "Esperado ')' após expressão")

        return ComandoEscreva(linha=token.linha, coluna=token.coluna, expressao=expr)

    def comando_leia(self) -> Optional[ComandoLeia]:
        token = self.avancar()
        self.consumir(TipoToken.PARENTESE_ESQ, "Esperado '(' após 'leia'")
        token_var = self.consumir(TipoToken.IDENTIFICADOR, "Esperado variável em 'leia'")
        var = token_var.lexema if token_var else ""
        self.consumir(TipoToken.PARENTESE_DIR, "Esperado ')' após variável")

        return ComandoLeia(linha=token.linha, coluna=token.coluna, variavel=var)

    # Expressões (sem mudanças)
    def expressao(self) -> Optional[NoAST]:
        return self.expressao_comparacao()

    def expressao_comparacao(self) -> Optional[NoAST]:
        expr = self.expressao_aditiva()
        while self.verificar(TipoToken.MAIOR, TipoToken.MENOR, TipoToken.MAIOR_IGUAL, TipoToken.MENOR_IGUAL):
            op = self.avancar()
            dir = self.expressao_aditiva()
            if dir is None:
                break
            expr = ExpressaoBinaria(linha=op.linha, coluna=op.coluna, esquerda=expr, operador=op.lexema, direita=dir)
        return expr

    def expressao_aditiva(self) -> Optional[NoAST]:
        expr = self.expressao_multiplicativa()
        while self.verificar(TipoToken.ADICAO, TipoToken.SUBTRACAO):
            op = self.avancar()
            dir = self.expressao_multiplicativa()
            if dir is None:
                break
            expr = ExpressaoBinaria(linha=op.linha, coluna=op.coluna, esquerda=expr, operador=op.lexema, direita=dir)
        return expr

    def expressao_multiplicativa(self) -> Optional[NoAST]:
        expr = self.expressao_primaria()
        while self.verificar(TipoToken.MULTIPLICACAO, TipoToken.DIVISAO):
            op = self.avancar()
            dir = self.expressao_primaria()
            if dir is None:
                break
            expr = ExpressaoBinaria(linha=op.linha, coluna=op.coluna, esquerda=expr, operador=op.lexema, direita=dir)
        return expr

    def expressao_primaria(self) -> Optional[NoAST]:
        token = self.token_atual()

        if self.verificar(TipoToken.INTEIRO):
            self.avancar()
            return Literal(linha=token.linha, coluna=token.coluna, valor=int(token.lexema), tipo="inteiro")
        if self.verificar(TipoToken.FLUTUANTE):
            self.avancar()
            return Literal(linha=token.linha, coluna=token.coluna, valor=float(token.lexema), tipo="flutuante")
        if self.verificar(TipoToken.CADEIA):
            self.avancar()
            return Literal(linha=token.linha, coluna=token.coluna, valor=token.lexema, tipo="cadeia")
        if self.verificar(TipoToken.BOOLEANO):
            self.avancar()
            val = token.lexema.lower() == "verdadeiro"
            return Literal(linha=token.linha, coluna=token.coluna, valor=val, tipo="logico")
        if self.verificar(TipoToken.IDENTIFICADOR):
            self.avancar()
            return Identificador(linha=token.linha, coluna=token.coluna, nome=token.lexema)
        if self.verificar(TipoToken.PARENTESE_ESQ):
            self.avancar()
            expr = self.expressao()
            self.consumir(TipoToken.PARENTESE_DIR, "Esperado ')' após expressão")
            return expr

        self.erros.append(ErroSintatico("Expressão inválida", token.linha, token.coluna))
        self.avancar()
        return None

    # Métodos públicos
    def tem_erros(self) -> bool:
        return len(self.erros) > 0

    def obter_erros(self) -> List[ErroSintatico]:  # <--- ADICIONADO!
        return self.erros

    def imprimir_erros(self):
        if self.tem_erros():
            print("\n=== ERROS SINTÁTICOS ENCONTRADOS ===")
            for e in self.erros:
                print(e)
                print()
        else:
            print("\n=== ANÁLISE SINTÁTICA CONCLUÍDA SEM ERROS ===")


# ============================================
# IMPRESSÃO DA AST (inalterada)
# ============================================

def imprimir_ast(no: Optional[NoAST], nivel: int = 0, prefixo: str = ""):
    if no is None:
        return

    indent = "  " * nivel
    print(f"{indent}{prefixo}{no}")

    if isinstance(no, Programa):
        for i, c in enumerate(no.comandos):
            imprimir_ast(c, nivel + 1, f"[{i}] ")

    elif isinstance(no, DeclaracaoVariavel):
        if no.valor_inicial:
            imprimir_ast(no.valor_inicial, nivel + 1, "valor: ")

    elif isinstance(no, DeclaracaoFuncao):
        for i, p in enumerate(no.parametros):
            imprimir_ast(p, nivel + 1, f"param[{i}]: ")
        for i, c in enumerate(no.corpo):
            imprimir_ast(c, nivel + 1, f"corpo[{i}]: ")

    elif isinstance(no, Atribuicao):
        imprimir_ast(no.expressao, nivel + 1, "expr: ")

    elif isinstance(no, ComandoSe):
        imprimir_ast(no.condicao, nivel + 1, "cond: ")
        for i, c in enumerate(no.bloco_verdadeiro):
            imprimir_ast(c, nivel + 1, f"entao[{i}]: ")
        if no.bloco_falso:
            for i, c in enumerate(no.bloco_falso):
                imprimir_ast(c, nivel + 1, f"senao[{i}]: ")

    elif isinstance(no, ComandoEscreva):
        imprimir_ast(no.expressao, nivel + 1, "expr: ")

    elif isinstance(no, ExpressaoBinaria):
        imprimir_ast(no.esquerda, nivel + 1, "esq: ")
        imprimir_ast(no.direita, nivel + 1, "dir: ")


# ============================================
# EXEMPLO DE USO
# ============================================

if __name__ == "__main__":
    codigo_exemplo = """
    inicio
        // Declaração de variáveis
        inteiro x = 10
        flutuante y = 3.14
        cadeia mensagem = "Olá"
        logico ativo = verdadeiro
        
        // Atribuição
        x = 20
        y = x + 5
        
        // Expressões numéricas
        inteiro resultado = (x + 5) * 2 - 10 / 2
        
        // Comando se com inicio/fim
        se (x > 15) faca
        inicio
            escreva("X é maior que 15")
            x = x - 5
        fim
        senao
        inicio
            escreva("X é menor ou igual a 15")
        fim
        
        // Comparações lógicas - se simples sem senao
        se (y >= 20) faca
            escreva("Y é maior ou igual a 20")
        
        // Leitura e escrita
        leia(x)
        escreva(x * 2)
        
        // Declaração de função
        inteiro soma(inteiro a, inteiro b)
        inicio
            inteiro res = a + b
            escreva(res)
        fim
        
        flutuante divide(flutuante x, flutuante y)
        inicio
            flutuante resultado = x / y
            escreva(resultado)
        fim
    fim
    """
    
    print("="*60)
    print("ANÁLISE LÉXICA")
    print("="*60)
    
    analisador_lexico = AnalisadorLexico(codigo_exemplo)
    tokens = analisador_lexico.analisar()
    
    if analisador_lexico.tem_erros():
        print("\n❌ ERRO: Análise léxica encontrou erros!")
        analisador_lexico.imprimir_erros()
        exit(1)
    
    print(f"✅ Análise léxica concluída: {len(tokens)} tokens encontrados")
    
    print("\n" + "="*60)
    print("ANÁLISE SINTÁTICA")
    print("="*60)
    
    analisador_sintatico = AnalisadorSintatico(tokens)
    ast = analisador_sintatico.analisar()
    
    if analisador_sintatico.tem_erros():
        analisador_sintatico.imprimir_erros()
    else:
        print("\n✅ Análise sintática concluída com sucesso!")
        
        print("\n" + "="*60)
        print("ÁRVORE SINTÁTICA ABSTRATA (AST)")
        print("="*60)
        imprimir_ast(ast)
    
    print("\n" + "="*60)
    print("ESTATÍSTICAS")
    print("="*60)
    print(f"Total de tokens: {len(tokens)}")
    print(f"Erros sintáticos: {len(analisador_sintatico.obter_erros())}")
    
    print("\n\n" + "="*60)
    print("TESTANDO CÓDIGO COM ERROS SINTÁTICOS")
    print("="*60)
    
    codigo_com_erros = """
    inicio
        inteiro x = 10
        
        // Falta parêntese de fechamento
        se (x > 5 faca
            escreva("teste")
        fim
        
        // Falta expressão de atribuição
        inteiro y =
        
        // Erro em expressão
        inteiro z = 10 + * 5
    fim
    """
    
    analisador_lexico2 = AnalisadorLexico(codigo_com_erros)
    tokens2 = analisador_lexico2.analisar()
    
    analisador_sintatico2 = AnalisadorSintatico(tokens2)
    ast2 = analisador_sintatico2.analisar()
    
    analisador_sintatico2.imprimir_erros()
    
    if ast2 and ast2.comandos:
        print("\n" + "="*60)
        print("AST PARCIAL (apesar dos erros)")
        print("="*60)
        imprimir_ast(ast2)
