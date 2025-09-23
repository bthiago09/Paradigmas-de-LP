"""
Fluxo de execução:
    main -> scan(text) -> parse(tokens) -> (se válido) eval_stackcalc(tokens)

Gramática (EBNF) resumida:
    Program  = Expr ;
    Expr     = Number | Expr , Expr , Op ;
    Op       = "+" | "-" | "*" | "/" ;
    Number   = "0" | NonZeroDigit , { Digit } ;

Ideia da pilha:
    - número => "push" na pilha
    - operador => "pop" 2 operandos, aplica operação e "push" do resultado
    - no final, deve sobrar exatamente 1 item (o resultado)
"""

import re
import sys

# 1) Definições de tokens (mantendo simples: tipo = string; valor = int|None)
TOKEN_NUM  = "NUM"
TOKEN_PLUS = "PLUS"
TOKEN_MIN  = "MIN"
TOKEN_MUL  = "MUL"
TOKEN_DIV  = "DIV"

OPS = {
    '+': TOKEN_PLUS,
    '-': TOKEN_MIN,
    '*': TOKEN_MUL,
    '/': TOKEN_DIV,
}

# Inteiro não-negativo em base 10 (sem sinal):
INT_RE = re.compile(r'^(0|[1-9][0-9]*)$')

class LexicalError(Exception):
    """Erro de análise léxica (símbolo/token inválido)."""
    pass

# 2) SCAN — Analisador Léxico
#    Entrada: strirng com tokens separados por espaço
#    Saída: lista de tokens como tuplas (tipo, valor_ou_None)
def scan(text):
    """
    Divide 'text' por espaços e classifica cada pedaço como:
        - Operador: + - * /
        - Número: inteiro decimal não-negativo
    Caso encontre algo inválido, levanta LexicalError.
    """
    tokens = []
    for p in text.split():
        if p in OPS:
            tokens.append((OPS[p], None))
        elif INT_RE.match(p):
            tokens.append((TOKEN_NUM, int(p)))
        else:
            raise LexicalError(
                f"token inválido: '{p}' (esperado número não-negativo ou + - * /)"
            )
    return tokens

# 3) PARSE — Analisador Sintático (validação via profundidade de operandos)
#    Regras:
#      - NUM => depth += 1
#      - OP  => precisa depth >= 2; depois depth -= 1
#    Aceita se: depth == 1 e pelo menos 1 token foi lido.
def parse(tokens):
    """
    Verifica se 'tokens' formam uma expressão RPN válida:
        Expr = Number | Expr Expr Op
    Retorna True (válida) ou False (erro de sintaxe).
    """
    depth = 0  # quantos operandos "disponíveis" temos no momento
    for (kind, _) in tokens:
        if kind == TOKEN_NUM:
            depth += 1
        else:
            if depth < 2:
                return False
            depth -= 1
    return len(tokens) > 0 and depth == 1

# 4) (BÔNUS NÉ PAI) Avaliador — executa de fato a expressão usando uma pilha
#    Política de divisão:
#      - Inteira truncada para zero: divi(a, b) = int(a / b)
#        Ex.: 7/3=2, -7/3=-2  (diferente de // que faria -7//3==-3)
def divi(a, b):
    if b == 0:
        raise ZeroDivisionError("Divisão por zero.")
    return int(a / b)  # truncamento para zero

def eval_stackcalc(tokens):
    """
    Executa a expressão RPN usando uma pilha de inteiros.
    Pré-condição: tokens já foram validados em parse() (boa prática).
    """
    st = []
    for (kind, val) in tokens:
        if kind == TOKEN_NUM:
            st.append(val)                    # push número
        elif kind == TOKEN_PLUS:
            b = st.pop(); a = st.pop()
            st.append(a + b)
        elif kind == TOKEN_MIN:
            b = st.pop(); a = st.pop()
            st.append(a - b)
        elif kind == TOKEN_MUL:
            b = st.pop(); a = st.pop()
            st.append(a * b)
        elif kind == TOKEN_DIV:
            b = st.pop(); a = st.pop()
            st.append(divi(a, b))
        else:
            raise RuntimeError(f"token desconhecido em eval: {kind}")
    if len(st) != 1:
        raise ValueError("Erro de avaliação: pilha final não tem exatamente 1 item.")
    return st[0]

# 5) Função de alto nível: valida e, se válido, avalia (bônus)
def run_stackcalc(source):
    """
    - scan(source)      -> tokens
    - parse(tokens)     -> valida
    - eval_stackcalc()  -> (bônus) calcula resultado se válido
    Retorna (ok: bool, msg: str, result: int|None)
    """
    try:
        tokens = scan(source)
    except LexicalError as e:
        return (False, f"Erro Léxico: {e}", None)

    ok = parse(tokens)
    if not ok:
        return (False, "Erro de Sintaxe", None)

    # BÔNUS: calcular o resultado (pilha de inteiros)
    try:
        result = eval_stackcalc(tokens)
    except ZeroDivisionError as e:
        return (False, f"Erro de Execução: {e}", None)
    return (True, "Sintaxe Válida", result)

# 6) MAIN — Ponto de entrada
#     - Roda run_stackcalc
#     - Imprime status sintático e, se válido, o resultado
def main():
    if len(sys.argv) > 1:
        source = " ".join(sys.argv[1:])
    else:
        source = input("Digite a expressão em RPN (StackCalc): ").strip()

    ok, msg, result = run_stackcalc(source)
    if ok:
        print(f"{msg}; Resultado = {result}")
    else:
        print(msg)

if __name__ == "__main__":
    main()
