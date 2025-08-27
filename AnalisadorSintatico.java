package lexico;
import java.util.List;
class AnalisadorSintatico {
    private List<Token> tokens;
    private int atual = 0;

    public AnalisadorSintatico(List<Token> tokens) {
        this.tokens = tokens;
    }

    public void analisar() {
        while (!estaNoFim()) {
            instrucao();
        }
        System.out.println("Análise sintática concluída com sucesso.");
    }

    private void instrucao() {
        if (corresponde("IDENTIFICADOR")) {
            String lexema = anterior().getLexema();
            if (lexema.equals("var")) {
                declaracaoVariavel();
            } else if (lexema.equals("function")) {
                declaracaoFuncao();
            } else if (lexema.equals("if")) {
                instrucaoIf();
            } else if (lexema.equals("print")) {
                instrucaoImprimir();
            } else if (lexema.equals("input")) {
                instrucaoEntrada();
            } else {
                atual--; 
                atribuicao();
            }
        } else {
            erro("Esperado declaração ou comando.");
        }
    }

    private void declaracaoVariavel() {
        consumir("IDENTIFICADOR", "identificador após 'var'");
    }

    private void atribuicao() {
        consumir("IDENTIFICADOR", "identificador para atribuição");
        consumir("ATRIBUICAO", "'=' para atribuição");
        expressao();
    }

    private void declaracaoFuncao() {
        consumir("IDENTIFICADOR", "nome da função");
        consumir("ABRE_COLCHETE", "'[' para bloco da função");
        while (!verificar("FECHA_COLCHETE")) {
            instrucao();
        }
        consumir("FECHA_COLCHETE", "']' para fechar bloco da função");
    }

    private void instrucaoIf() {
        consumir("ABRE_PARENTESE", "'(' após 'if'");
        expressaoLogica();
        consumir("FECHA_PARENTESE", "')' após condição");
        consumir("ABRE_COLCHETE", "'[' para bloco do 'if'");
        while (!verificar("FECHA_COLCHETE")) {
            instrucao();
        }
        consumir("FECHA_COLCHETE", "']' para fechar bloco do 'if'");
    }

    private void instrucaoImprimir() {
        // Já consumiu "print"
        consumir("ABRE_PARENTESE", "'(' após 'print'");
        expressao();
        consumir("FECHA_PARENTESE", "')' após expressão");
    }

    private void instrucaoEntrada() {
        // Já consumiu "input"
        consumir("ABRE_PARENTESE", "'(' após 'input'");
        consumir("IDENTIFICADOR", "identificador para 'input'");
        consumir("FECHA_PARENTESE", "')' após identificador");
    }

    private void expressao() {
        aditiva();
        while (corresponde("CONCATENACAO")) {
            aditiva();
        }
    }

    private void aditiva() {
        multiplicativa();
        while (corresponde("SOMA", "SUBTRACAO")) {
            multiplicativa();
        }
    }

    private void multiplicativa() {
        unaria();
        while (corresponde("MULTIPLICACAO", "DIVISAO")) {
            unaria();
        }
    }

    private void unaria() {
        if (corresponde("SUBTRACAO")) {
            unaria();
        } else if (corresponde("INCREMENTO", "DECREMENTO")) {
            consumir("IDENTIFICADOR", "identificador após incremento/decremento prefixado");
        } else {
            primaria();
        }
    }

    private void primaria() {
        if (corresponde("INTEIRO", "FLOAT", "STRING")) {
            // Literal
        } else if (corresponde("IDENTIFICADOR")) {
            // Identificador, opcionalmente seguido de postfix ++/--
            corresponde("INCREMENTO", "DECREMENTO");
        } else if (corresponde("ABRE_PARENTESE")) {
            expressao();
            consumir("FECHA_PARENTESE", "')' após expressão");
        } else {
            erro("Esperado literal, identificador ou expressão entre parênteses.");
        }
    }

    private void expressaoLogica() {
        expressao();
        if (corresponde("IGUAL", "MAIOR", "MENOR", "MAIOR_IGUAL", "MENOR_IGUAL")) {
            expressao();
        } else {
            erro("Esperado operador de comparação.");
        }
    }

    private boolean estaNoFim() {
        return atual >= tokens.size();
    }

    private Token espiar() {
        if (estaNoFim()) return null;
        return tokens.get(atual);
    }

    private Token anterior() {
        return tokens.get(atual - 1);
    }

    private Token avancar() {
        if (!estaNoFim()) atual++;
        return anterior();
    }

    private boolean verificar(String tipo) {
        if (estaNoFim()) return false;
        return espiar().getTipoToken().equals(tipo);
    }

    private boolean corresponde(String... tipos) {
        for (String tipo : tipos) {
            if (verificar(tipo)) {
                avancar();
                return true;
            }
        }
        return false;
    }

    private Token consumir(String tipo, String mensagem) {
        if (verificar(tipo)) {
            return avancar();
        }
        erro("Esperado " + mensagem);
        return null;
    }

    private void erro(String mensagem) {
        Token token = estaNoFim() ? null : espiar();
        System.out.println("Erro sintático: " + mensagem + " na posição " + (token != null ? token.getPosicao() : "fim"));
        System.exit(1);
    }
}