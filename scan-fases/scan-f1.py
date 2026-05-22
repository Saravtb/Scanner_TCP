import socket

# Scanner de Porta Única
def verificar_porta(host, porta):
    """
    Verifica se uma determinada porta TCP está aberta em um host.
    Retorna True se a porta estiver aberta, False caso contrário.
    """
    try:
        # Cria um socket TCP (AF_INET = IPv4, SOCK_STREAM = TCP)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Define um tempo limite máximo de espera pela conexão (2 segundos)
        # Isso evita que o programa fique travado em portas filtradas (firewall)
        s.settimeout(2)

        # Tenta estabelecer uma conexão com o host e porta especificados.
        # O método connect_ex() retorna 0 se a conexão for bem-sucedida,
        # ou um código de erro (ex: 10060, 10061) em caso de falha.
        # Diferente do connect(), este não lança exceção, o que facilita o tratamento.
        codigo = s.connect_ex((host, porta))

        # Fecha o socket para liberar recursos do sistema
        s.close()

        # Se o código retornado for 0, a porta está aberta (conexão aceita)
        return codigo == 0

    # Captura qualquer erro relacionado a socket (ex: host inexistente, rede inacessível)
    except socket.error:
        return False


# Função principal que interage com o usuário no terminal
def main():
    print("=== Scanner de Porta Única ===")

    # Solicita ao usuário o endereço do alvo (IP ou nome de host)
    alvo = input("Digite o IP ou hostname: ")

    # Solicita o número da porta e converte para inteiro
    porta = int(input("Digite a porta: "))

    # Exibe mensagem indicando o início da verificação
    print(f"\nVerificando {alvo}:{porta} ...")

    # Chama a função de verificação e exibe o resultado apropriado
    if verificar_porta(alvo, porta):
        print(f"[+] Porta {porta} ABERTA")
    else:
        print(f"[-] Porta {porta} FECHADA ou FILTRADA")


# Garante que a função main() só será executada se o script for rodado diretamente
# (e não importado como módulo em outro programa)
if __name__ == "__main__":
    main()
