"""
Fluxo de execução:
    main -> scan(text) -> parse(tokens) -> (se válido) eval_stackcalc(tokens)

Gramática padrão EBNF:
    Program   = Expr ;
    Expr      = Number | Expr , Expr , Op ;
    Op        = "+" | "-" | "*" | "/" ;
    Number    = "0" | NonZero , { Digit } ;
    NonZero   = "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;
    Digit     = "0" | "1" | "2" | "3" | "4" | "5" | "6" | "7" | "8" | "9" ;


Ideia da pilha:
    - número => "push" na pilha
    - operador => "pop" 2 operandos, aplica operação e "push" do resultado
    - no final, deve sobrar o resultado
"""

import re
import sys

# 1) Definições de tokens (mantendo simples: tipo = string; valor = int|None)
TOKEN_NUM  = "NUM"
TOKEN_PLUS = "PLUS"
TOKEN_MIN  = "MIN"
TOKEN_MUL  = "MUL"
TOKEN_DIV  = "DIV"

# Um dicionário para traduzir rapidamente o caractere
OPS = {
    '+': TOKEN_PLUS,
    '-': TOKEN_MIN,
    '*': TOKEN_MUL,
    '/': TOKEN_DIV,
}

# Definir o que consideramos um número válido.
# Garante que aceitamos "123" e "0", mas rejeitamos "01" ou "abc".
INT_RE = re.compile(r'^(0|[1-9][0-9]*)$')

class LexicalError(Exception):
    pass

# 2) SCAN — Analisador Léxico
def scan(text):
    # Caso encontre algo inválido, levanta LexicalError.
    
    tokens = []
    # Quebramos a entrada por espaços para analisar cada "palavra".
    for p in text.split():
        # Verificamos primeiro se é um operador, pois é a checagem mais rápida.
        if p in OPS:
            tokens.append((OPS[p], None))
        # Se não for operador, vemos se corresponde ao nosso padrão de número.
        elif INT_RE.match(p):
            tokens.append((TOKEN_NUM, int(p)))
        # Se não for nem um nem outro, não sabemos o que é. É um erro!
        else:
            raise LexicalError(
                f"token inválido: '{p}' (esperado número não-negativo ou + - * /)"
            )
    return tokens

# 3) PARSE — Analisador Sintático
# Verifica se a sequência de tokens faz sentido. Ela usa a "pilha falsa", um contador q simula o tmn da pilha.
def parse(tokens):
    """
    Verifica se 'tokens' formam uma expressão RPN válida:
        Expr = Number | Expr Expr Op
    Retorna True (válida) ou False (erro de sintaxe).
    """
    # 'depth' representa quantos números estão "sobrando" na pilha, esperando uma operação.
    depth = 0
    for (kind, _) in tokens:
        # Se o token é um número...
        if kind == TOKEN_NUM:
            # ...a profundidade da nossa pilha simulada aumenta.
            depth += 1
        # Se for um operador...
        else:
            # ...precisamos de pelo menos 2 números na pilha para operar.
            if depth < 2:
                # Se não tiver, a sintaxe está errada. Ex: "5 +" ou "* 2 3"
                return False
            # Um operador consome 2 números e devolve 1 (o resultado).
            # Então, o saldo líquido na pilha é de -1.
            depth -= 1
            
    # No final a pilha deve ter somente 1 item.
    # Também garantimos que a expressão não estava vazia.
    return len(tokens) > 0 and depth == 1

# 4) (BÔNUS) Avaliador — O mano que faz o cálculo.
# Esta parte só é executada se o (parse) aprovar a expressão.
def divi(a, b):
    """Uma função auxiliar para tratar a divisão por zero e garantir divisão inteira."""
    if b == 0:
        raise ZeroDivisionError("Divisão por zero.")
    # Garantindo o truncamento
    return int(a / b)

def eval_stackcalc(tokens):
    
    # Executa a expressão RPN usando uma pilha de verdade (uma lista).
    # Assume que os tokens já foram validados pela função parse().
    
    # Agora sim, a pilha real de verdade.
    stack = []
    for (kind, val) in tokens:
        # Se for um número, simplesmente o adicionamos ao topo da pilha.
        if kind == TOKEN_NUM:
            stack.append(val)
        # Se for uma soma...
        elif kind == TOKEN_PLUS:
            # ...tiramos os dois últimos números da pilha.
            # Lembre-se: o último a entrar (b) é o primeiro a sair!
            b = stack.pop(); a = stack.pop()
            # Realizamos a operação e colocamos o resultado de volta na pilha.
            stack.append(a + b)
        # A lógica se repete para as outras operações...
        elif kind == TOKEN_MIN:
            b = stack.pop(); a = stack.pop()
            stack.append(a - b)
        elif kind == TOKEN_MUL:
            b = stack.pop(); a = stack.pop()
            stack.append(a * b)
        elif kind == TOKEN_DIV:
            b = stack.pop(); a = stack.pop()
            stack.append(divi(a, b))
        else:
            raise RuntimeError(f"token desconhecido em eval: {kind}")
            
    # Se a lógica do parser estiver correta, a pilha final SEMPRE terá só 1 item.
    # Esta verificação é uma segurança extra.
    if len(stack) != 1:
        raise ValueError("Erro de avaliação: pilha final não tem exatamente 1 item.")
    
    # O resultado final é o único item que sobrou na pilha.
    return stack[0]

# 5) O "Gerente" do processo
# Esta função coordena as chamadas para o scanner, parser e avaliador.
def run_stackcalc(source):
    """
    - scan(source)      -> tokens
    - parse(tokens)     -> valida
    - eval_stackcalc()  -> calcula o resultado se for válido
    Retorna uma tupla indicando sucesso ou falha, uma mensagem e o resultado.
    """
    try:
        # 1. Tenta traduzir o texto em tokens. Pode dar um Erro Léxico.
        tokens = scan(source)
    except LexicalError as e:
        return (False, f"Erro Léxico: {e}", None)

    # 2. Verifica se a sequência de tokens é gramaticalmente válida.
    ok = parse(tokens)
    if not ok:
        return (False, "Erro de Sintaxe", None)
        
    # 3. Se a sintaxe for válida, tenta calcular o resultado. Pode dar um Erro de Execução (ex: div por zero).
    try:
        result = eval_stackcalc(tokens)
    except ZeroDivisionError as e:
        return (False, f"Erro de Execução: {e}", None)
        
    # Se tudo correu bem, retorna o sucesso e o resultado.
    return (True, "Sintaxe Válida", result)

# 6) MAIN — Ponto de entrada do programa
# A única responsabilidade desta parte é interagir com o usuário.
def main():
    # Permite que a expressão seja passada como argumento na linha de comando...
    if len(sys.argv) > 1:
        source = " ".join(sys.argv[1:])
    # ...ou pede para o usuário digitar, caso o programa seja executado diretamente.
    else:
        source = input("Digite a expressão em RPN (StackCalc): ").strip()

    # Chama o nosso "gerente" para fazer todo o trabalho pesado.
    ok, msg, result = run_stackcalc(source)

    # Imprime o resultado para o usuário de forma clara.
    if ok:
        print(f"{msg}; Resultado = {result}")
    else:
        print(msg)

# Essa é uma convenção em Python. O código dentro deste 'if' só executa
# quando o arquivo é rodado diretamente (e não quando é importado por outro arquivo).
if __name__ == "__main__":
    main()