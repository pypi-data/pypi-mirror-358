
def adicao(a, b):
    return a + b
def subtracao(a, b):
    return a - b
def multiplicacao(a, b):
    return a * b
def divisao(a, b):
    if b == 0:
        return "Erro: Divisão por zero!"
    return a / b
def escolha_operacao(a,num1, num2):
    escolha = a
    while True:
        if escolha == '1':
            resultado = adicao(num1, num2)
        elif escolha == '2':
            resultado = subtracao(num1, num2)
        elif escolha == '3':
            resultado = multiplicacao(num1, num2)
        elif escolha == '4':
            resultado = divisao(num1, num2)
        else:
            print("Opção inválida. Tente novamente.")
            continue
        return resultado
