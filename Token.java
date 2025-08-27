package lexico;

class Token {
    private String tipoToken;
    private String lexema;
    private int posicao;

    public Token(String tipoToken, String lexema, int posicao) {
        this.tipoToken = tipoToken;
        this.lexema = lexema;
        this.posicao = posicao;
    }

    public String getTipoToken() {
        return tipoToken;
    }

    public String getLexema() {
        return lexema;
    }

    public int getPosicao() {
        return posicao;
    }

    @Override
    public String toString() {
        return tipoToken + "," + lexema + "=";
    }
}