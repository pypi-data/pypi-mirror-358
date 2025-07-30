def menu():
    print("Calculadora Simples")
    print("1. Adição")
    print("2. Subtração")
    print("3. Multiplicação")
    print("4. Divisão")
    print("5. Sair")
    escolha = input("Escolha uma opção (1-5): ")
    return escolha

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

def calculadora():
    while True:
        escolha = menu()
        if escolha == '5':
            print("Saindo da calculadora.")
            break
        elif escolha not in ['1', '2', '3', '4']:
            print("Opção inválida. Tente novamente.")
            continue
        
        try:
            num1 = float(input("Digite o primeiro número: "))
            num2 = float(input("Digite o segundo número: "))
        except ValueError:
            print("Entrada inválida. Por favor, insira números válidos.")
            continue
        
        resultado = escolha_operacao(escolha, num1, num2)
        
        print(f"Resultado: {resultado}")
if __name__ == "__main__":
    calculadora()