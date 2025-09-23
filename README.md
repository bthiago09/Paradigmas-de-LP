# Paradigmas de Linguagens de Programação  

Esse repositório é pra guardar códigos e experimentos da disciplina de **Paradigmas de Linguagens de Programação**.  
Por enquanto só tem um projetinho: um **StackCalc** (calculadora em **RPN — Notação Polonesa Reversa**).  

## O que ele faz?  

- Lê uma expressão em RPN (exemplo: `3 4 + 2 *` → `(3 + 4) * 2`).  
- Passa por três etapas:  
  1. **Scan** → separa a string em tokens.  
  2. **Parse** → valida a gramática (EBNF básica).  
  3. **Eval** → se tudo der certo, avalia a expressão usando pilha.  

## Como rodar  

```bash
python stackcalc.py "3 4 + 2 *"
Sintaxe Válida; Resultado = 14 
```

## Obs

- Se colocar coisa errada, aparece Erro Léxico ou Erro de Sintaxe.
- Tem tratamento pra divisão por zero também (não vai explodir o programa).
