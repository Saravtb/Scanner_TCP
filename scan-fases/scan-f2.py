# Scanner de Range de Portas - Fase 2
# Autor: Aluno SENAI - Sprint 3
# Descrição: Varre um intervalo de portas TCP em um host, exibindo quais estão abertas
#            e mostrando um resumo ao final (total abertas/fechadas e tempo gasto).

import socket
import time

# ------------------------------------------------------------------
# Função para verificar se uma porta específica está aberta
# ------------------------------------------------------------------
def verificar_porta(host, porta):
    """
    Tenta estabelecer uma conexão TCP com o host na porta informada.
    Retorna True se a porta estiver aberta (conexão bem-sucedida),
    False caso contrário (fechada, filtrada ou erro).
    """
    try:
        # Cria um socket TCP/IP (AF_INET = IPv4, SOCK_STREAM = TCP)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Define um timeout curto (1 segundo) para não atrasar a varredura em ranges grandes.
        # Portas filtradas (firewall) podem demorar, mas o timeout evita travamentos.
        s.settimeout(1)

        # Tenta conectar; connect_ex retorna 0 se sucesso, ou código de erro (>0) se falha.
        codigo = s.connect_ex((host, porta))

        # Fecha o socket imediatamente (não mantém conexão aberta)
        s.close()

        # Retorna True apenas se o código for 0 (porta aberta)
        return codigo == 0

    # Em caso de qualquer exceção (ex: host inválido, rede indisponível), trata como porta fechada
    except:
        return False


# ------------------------------------------------------------------
# Função principal
# ------------------------------------------------------------------
def main():
    print("=== Scanner de Range de Portas ===")

    # Solicita o alvo (IP ou hostname) e o range de portas no formato "inicio-fim"
    alvo = input("IP alvo: ")
    range_str = input("Range (ex: 1-1024): ")

    # Converte a string "inicio-fim" em dois inteiros: inicio e fim
    # Ex: "20-80" -> inicio=20, fim=80
    inicio, fim = map(int, range_str.split("-"))

    print(f"\nEscaneando {alvo} das portas {inicio} a {fim}...\n")

    # Marca o tempo de início da varredura (para calcular a duração total)
    inicio_tempo = time.time()

    # Lista que armazenará as portas que estiverem abertas
    abertas = []

    # Contador de portas fechadas ou filtradas (não abertas)
    fechadas = 0

    # ------------------------------------------------------------------
    # MODO SEQUENCIAL (mais simples, mas mais lento para ranges grandes)
    # ------------------------------------------------------------------
    # O loop percorre cada porta no intervalo [inicio, fim] (inclusive)
    for porta in range(inicio, fim + 1):
        # Verifica se a porta está aberta chamando a função auxiliar
        if verificar_porta(alvo, porta):
            # Se aberta, adiciona à lista e exibe imediatamente no terminal
            abertas.append(porta)
            print(f"  Porta {porta} ABERTA")
        else:
            # Se fechada/filtrada, apenas incrementa o contador
            fechadas += 1

    # ------------------------------------------------------------------
    # (OPÇÃO COMENTADA) MODO COM MULTITHREADING - MUITO MAIS RÁPIDO
    # ------------------------------------------------------------------
    # Para acelerar a varredura, poderíamos usar concurrent.futures.ThreadPoolExecutor,
    # que testa várias portas simultaneamente. O código abaixo está comentado porque
    # o foco da Fase 2 é o modo sequencial (obrigatório). O modo com threads será
    # implementado na Fase 3 (avançado).
    #
    # Exemplo (não executado neste código):
    #
    # import concurrent.futures
    # with concurrent.futures.ThreadPoolExecutor(max_workers=100) as executor:
    #     futures = {executor.submit(verificar_porta, alvo, p): p for p in range(inicio, fim+1)}
    #     for future in concurrent.futures.as_completed(futures):
    #         porta = futures[future]
    #         if future.result():
    #             abertas.append(porta)
    #             print(f"  Porta {porta} ABERTA")
    #         else:
    #             fechadas += 1
    #
    # A vantagem é que 100 portas podem ser testadas em paralelo, reduzindo drasticamente
    # o tempo total. A desvantagem é a maior complexidade e a necessidade de controle
    # sobre o número máximo de threads para não sobrecarregar o sistema.

    # ------------------------------------------------------------------
    # Cálculo do tempo total e exibição do resumo
    # ------------------------------------------------------------------
    fim_tempo = time.time()
    tempo_total = round(fim_tempo - inicio_tempo, 2)  # arredonda para 2 casas decimais

    print("\n=== RESUMO ===")
    print(f"Portas abertas: {abertas}")
    print(f"Total abertas: {len(abertas)}")
    print(f"Total fechadas/filtradas: {fechadas}")
    print(f"Tempo total: {tempo_total} segundos")


# Garante que a função main() só será executada quando o script for rodado diretamente
if __name__ == "__main__":
    main()