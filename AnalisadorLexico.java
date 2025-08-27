package lexico;

import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Map;

public class AnalisadorLexico {
    public static void main(String[] args) {
        Map<String, Map<Character, String>> afd = new HashMap<>();

        Map<Character, String> q0 = new HashMap<>();
        q0.put(' ', "q5"); q0.put('\t', "q5"); q0.put('\n', "q5");
        q0.put('(', "q6"); q0.put(')', "q7"); q0.put('[', "q8"); q0.put(']', "q9");
        q0.put('+', "q10"); q0.put('-', "q11"); q0.put('*', "q12"); q0.put('/', "q13");
        q0.put('=', "q14"); q0.put('>', "q15"); q0.put('<', "q16"); q0.put('&', "q17");
        q0.put('"', "q18");
        for (char c = '0'; c <= '9'; c++) q0.put(c, "q1");
        for (char c = 'a'; c <= 'z'; c++) q0.put(c, "q2");
        for (char c = 'A'; c <= 'Z'; c++) q0.put(c, "q2");
        afd.put("q0", q0);


        Map<Character, String> q1 = new HashMap<>();
        for (char c = '0'; c <= '9'; c++) q1.put(c, "q1");
        q1.put('.', "q3");
        afd.put("q1", q1);


        Map<Character, String> q2 = new HashMap<>();
        for (char c = '0'; c <= '9'; c++) q2.put(c, "q2");
        for (char c = 'a'; c <= 'z'; c++) q2.put(c, "q2");
        for (char c = 'A'; c <= 'Z'; c++) q2.put(c, "q2");
        afd.put("q2", q2);


        Map<Character, String> q3 = new HashMap<>();
        for (char c = '0'; c <= '9'; c++) q3.put(c, "q4");
        afd.put("q3", q3);


        Map<Character, String> q4 = new HashMap<>();
        for (char c = '0'; c <= '9'; c++) q4.put(c, "q4");
        afd.put("q4", q4);


        afd.put("q5", new HashMap<>());
        afd.put("q6", new HashMap<>());
        afd.put("q7", new HashMap<>());
        afd.put("q8", new HashMap<>());
        afd.put("q9", new HashMap<>());


        Map<Character, String> q10 = new HashMap<>();
        q10.put('+', "q19");
        afd.put("q10", q10);


        Map<Character, String> q11 = new HashMap<>();
        q11.put('-', "q20");
        afd.put("q11", q11);

        afd.put("q12", new HashMap<>());
        afd.put("q13", new HashMap<>());

        Map<Character, String> q14 = new HashMap<>();
        q14.put('=', "q21");
        afd.put("q14", q14);

        Map<Character, String> q15 = new HashMap<>();
        q15.put('=', "q22");
        afd.put("q15", q15);

        Map<Character, String> q16 = new HashMap<>();
        q16.put('=', "q23");
        afd.put("q16", q16);

        afd.put("q17", new HashMap<>());

        Map<Character, String> q18 = new HashMap<>();
        for (char c = '0'; c <= '9'; c++) q18.put(c, "q18");
        for (char c = 'a'; c <= 'z'; c++) q18.put(c, "q18");
        for (char c = 'A'; c <= 'Z'; c++) q18.put(c, "q18");
        q18.put(' ', "q18"); q18.put('!', "q18"); q18.put('@', "q18"); q18.put('#', "q18"); q18.put('$', "q18");
        q18.put('%', "q18"); q18.put('&', "q18"); q18.put('*', "q18"); q18.put('(', "q18"); q18.put(')', "q18");
        q18.put('-', "q18"); q18.put('_', "q18"); q18.put('+', "q18"); q18.put('=', "q18"); q18.put('{', "q18");
        q18.put('}', "q18"); q18.put('[', "q18"); q18.put(']', "q18"); q18.put('|', "q18"); q18.put('\\', "q18");
        q18.put(':', "q18"); q18.put(';', "q18"); q18.put('<', "q18"); q18.put('>', "q18"); q18.put(',', "q18");
        q18.put('.', "q18"); q18.put('?', "q18"); q18.put('/', "q18");
        q18.put('"', "q24");
        afd.put("q18", q18);

        afd.put("q19", new HashMap<>());
        afd.put("q20", new HashMap<>());
        afd.put("q21", new HashMap<>());
        afd.put("q22", new HashMap<>());
        afd.put("q23", new HashMap<>());

        afd.put("q24", new HashMap<>());

        Map<String, String> estadosFinais = new HashMap<>();
        estadosFinais.put("q1", "INTEIRO");
        estadosFinais.put("q2", "IDENTIFICADOR");
        estadosFinais.put("q4", "FLOAT");
        estadosFinais.put("q5", "ESPACO");
        estadosFinais.put("q6", "ABRE_PARENTESE");
        estadosFinais.put("q7", "FECHA_PARENTESE");
        estadosFinais.put("q8", "ABRE_COLCHETE");
        estadosFinais.put("q9", "FECHA_COLCHETE");
        estadosFinais.put("q10", "SOMA");
        estadosFinais.put("q11", "SUBTRACAO");
        estadosFinais.put("q12", "MULTIPLICACAO");
        estadosFinais.put("q13", "DIVISAO");
        estadosFinais.put("q14", "ATRIBUICAO");
        estadosFinais.put("q15", "MAIOR");
        estadosFinais.put("q16", "MENOR");
        estadosFinais.put("q17", "CONCATENACAO");
        estadosFinais.put("q19", "INCREMENTO");
        estadosFinais.put("q20", "DECREMENTO");
        estadosFinais.put("q21", "IGUAL");
        estadosFinais.put("q22", "MAIOR_IGUAL");
        estadosFinais.put("q23", "MENOR_IGUAL");
        estadosFinais.put("q24", "STRING");

        String entrada = " if (cont >10)/ ";
        List<Token> listaDeTokens = new ArrayList<>();
        String estado = "q0";
        String lexema = "";
        int posicao = 0;
        int indice = 0;

        while (indice < entrada.length()) {
            char caractere = entrada.charAt(indice);

            Map<Character, String> transicoes = afd.get(estado);
            if (transicoes.containsKey(caractere)) {
                estado = transicoes.get(caractere);
                if (!estado.equals("q5")) {
                    lexema += caractere;
                }
                posicao += 1;
                indice += 1;
            } else if (estadosFinais.containsKey(estado)) {
                if (!estadosFinais.get(estado).equals("ESPACO")) {
                    listaDeTokens.add(new Token(estadosFinais.get(estado), lexema, posicao));
                }
                estado = "q0";
                lexema = "";
            } else {
                System.out.println("Erro: token inválido: " + lexema + caractere);
                break;
            }
        }

        if (estadosFinais.containsKey(estado) && !estadosFinais.get(estado).equals("ESPACO")) {
            listaDeTokens.add(new Token(estadosFinais.get(estado), lexema, posicao));
        }

        for (Token tk : listaDeTokens) {
            System.out.println(tk);
        }

        AnalisadorSintatico parser = new AnalisadorSintatico(listaDeTokens);
        parser.analisar();
    }
}