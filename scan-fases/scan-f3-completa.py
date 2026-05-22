"""
PORT SCANNER - FASE 3 (COMPLETO)
--------------------------------
Funcionalidades:
- Escaneamento de um range de portas TCP
- Multithreading (ThreadPoolExecutor) para acelerar a varredura
- Banner grabbing opcional (captura de informações dos serviços)
- Identificação de serviços conhecidos via dicionário
- Salvamento dos resultados em arquivo .txt
- Modo sequencial também disponível (para comparação)

Aviso: Use apenas em laboratório autorizado!
"""

import socket
import time
import concurrent.futures

# ==================================================================
# DICIONÁRIO DE SERVIÇOS CONHECIDOS (PORTA -> NOME DO SERVIÇO)
# ==================================================================
# Mapeia números de porta para o nome do serviço típico que roda nela.
# Isso permite identificar rapidamente qual serviço provavelmente está
# rodando em uma porta aberta.
SERVICOS = {
    20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet",
    25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
    143: "IMAP", 443: "HTTPS", 993: "IMAPS", 995: "POP3S",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Alt"
}

# ==================================================================
# FUNÇÃO DE BANNER GRABBING
# ==================================================================
def banner_grabbing(host, porta):
    """
    Tenta capturar o banner (mensagem de boas-vindas) de um serviço.
    O banner geralmente contém informações como nome do software, versão,
    sistema operacional, etc. Útil para enumeração mais detalhada.

    Parâmetros:
        host (str): IP ou hostname do alvo
        porta (int): Número da porta já aberta

    Retorna:
        str: Banner capturado (limitado a 1024 bytes) ou mensagem de erro.
    """
    try:
        # Cria um socket TCP
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(2)                     # Aguarda no máximo 2 segundos
        s.connect((host, porta))            # Conecta à porta (já sabemos que está aberta)
        s.send(b"\n")                       # Envia uma quebra de linha (muitos serviços respondem a isso)
        banner = s.recv(1024).decode().strip()  # Lê até 1024 bytes e decodifica
        s.close()
        return banner if banner else "Banner vazio"
    except:
        return "Não capturado"


# ==================================================================
# FUNÇÃO DE VERIFICAÇÃO DE PORTA (COM OU SEM BANNER)
# ==================================================================
def verificar_porta(host, porta, fazer_banner=False):
    """
    Verifica se uma porta TCP está aberta. Opcionalmente, captura o banner.

    Parâmetros:
        host (str): IP ou hostname
        porta (int): Número da porta
        fazer_banner (bool): Se True, tenta capturar o banner da porta aberta

    Retorna:
        tuple: (porta, bool_aberta, banner_ou_None)
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)                     # Timeout de 1 segundo (rápido para ranges grandes)
        codigo = s.connect_ex((host, porta))  # connect_ex retorna 0 se sucesso, erro caso contrário

        if codigo == 0:                     # Porta aberta
            banner = None
            if fazer_banner:                # Se o usuário optou por banner grabbing
                banner = banner_grabbing(host, porta)
            s.close()
            return (porta, True, banner)
        else:                               # Porta fechada ou filtrada
            s.close()
            return (porta, False, None)
    except:
        # Qualquer exceção (ex: host inexistente) tratamos como porta não acessível
        return (porta, False, None)


# ==================================================================
# FUNÇÃO PRINCIPAL DE SCAN (COM SUPORTE A MULTITHREADING)
# ==================================================================
def scanner_range(host, inicio, fim, usar_threads=True, capturar_banner=False):
    """
    Escaneia um intervalo de portas em um host.

    Parâmetros:
        host (str): IP ou hostname
        inicio (int): primeira porta do intervalo
        fim (int): última porta do intervalo
        usar_threads (bool): se True, usa multithreading (rápido); se False, modo sequencial (lento)
        capturar_banner (bool): se True, tenta capturar banner das portas abertas

    Retorna:
        list: Lista das portas abertas encontradas
    """
    portas = list(range(inicio, fim + 1))   # Gera lista com todas as portas do intervalo
    abertas = []
    print(f"\n[+] Escaneando {host} das portas {inicio} a {fim}...\n")

    if usar_threads:
        # ---------- MODO COM MULTITHREADING (PARALELO) ----------
        # ThreadPoolExecutor gerencia um pool de threads. max_workers=200 significa que
        # até 200 portas serão testadas simultaneamente.
        with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
            # Submete uma tarefa (verificar_porta) para cada porta.
            # O dicionário futures mapeia cada Future (tarefa em andamento) à sua porta.
            futures = {executor.submit(verificar_porta, host, p, capturar_banner): p for p in portas}

            # as_completed() retorna os futures à medida que são concluídos (não na ordem original)
            for future in concurrent.futures.as_completed(futures):
                porta, is_open, banner = future.result()
                if is_open:
                    abertas.append(porta)
                    servico = SERVICOS.get(porta, "Desconhecido")   # Busca nome do serviço no dicionário
                    print(f"  [+] Porta {porta} ABERTA - {servico}")
                    if capturar_banner and banner:
                        print(f"      Banner: {banner[:100]}")      # Mostra apenas os primeiros 100 caracteres
    else:
        # ---------- MODO SEQUENCIAL (UM POR UM) - MAIS LENTO ----------
        for porta in portas:
            porta, is_open, banner = verificar_porta(host, porta, capturar_banner)
            if is_open:
                abertas.append(porta)
                servico = SERVICOS.get(porta, "Desconhecido")
                print(f"  [+] Porta {porta} ABERTA - {servico}")
                if capturar_banner and banner:
                    print(f"      Banner: {banner[:100]}")

    return abertas


# ==================================================================
# FUNÇÃO PARA SALVAR RESULTADOS EM ARQUIVO TEXTO
# ==================================================================
def salvar_resultados(host, inicio, fim, abertas, tempo, arquivo="scan_resultado.txt"):
    """
    Salva um relatório detalhado do scan em um arquivo .txt.

    Parâmetros:
        host (str): Alvo escaneado
        inicio, fim (int): Intervalo de portas
        abertas (list): Lista de portas abertas
        tempo (float): Tempo total do scan em segundos
        arquivo (str): Nome do arquivo de saída (padrão: scan_resultado.txt)
    """
    with open(arquivo, "w") as f:
        f.write(f"SCAN REALIZADO EM: {time.ctime()}\n")   # Data e hora legível
        f.write(f"ALVO: {host}\n")
        f.write(f"RANGE: {inicio} - {fim}\n")
        f.write(f"TEMPO TOTAL: {tempo:.2f} segundos\n")
        f.write(f"TOTAL PORTAS ABERTAS: {len(abertas)}\n")
        f.write("PORTAS ABERTAS:\n")
        for p in abertas:
            servico = SERVICOS.get(p, "Desconhecido")
            f.write(f"  {p} - {servico}\n")
    print(f"\n[+] Resultados salvos em {arquivo}")


# ==================================================================
# FUNÇÃO PRINCIPAL (INTERFACE COM USUÁRIO VIA TERMINAL)
# ==================================================================
def main():
    """
    Função principal que interage com o usuário, obtém parâmetros,
    executa o scan e pergunta se deseja salvar os resultados.
    """
    print("=== PORT SCANNER - TRABALHO SPRINT 3 ===\n")

    # Entrada do alvo
    alvo = input("IP ou hostname alvo: ")

    # Entrada do range de portas (formato "inicio-fim")
    range_str = input("Range de portas (ex: 1-1024): ")
    try:
        inicio, fim = map(int, range_str.split("-"))
        if inicio > fim or inicio < 1 or fim > 65535:
            raise ValueError
    except:
        print("Formato inválido. Use início-fim (ex: 20-443) e portas entre 1 e 65535.")
        return

    # Opções do usuário
    usar_threads = input("Usar multithreading? (s/n): ").lower().startswith('s')
    capturar_banner = input("Tentar banner grabbing? (s/n): ").lower().startswith('s')

    # Medição do tempo de execução
    inicio_tempo = time.time()

    # Executa o scan (retorna lista de portas abertas)
    abertas = scanner_range(alvo, inicio, fim, usar_threads, capturar_banner)

    tempo_total = time.time() - inicio_tempo

    # Exibe resumo final no terminal
    print("\n=== RESUMO FINAL ===")
    print(f"Portas abertas encontradas: {len(abertas)}")
    if abertas:
        print(f"Lista: {abertas}")
    print(f"Tempo total: {tempo_total:.2f} segundos")

    # Pergunta se deseja salvar o relatório
    salvar = input("\nSalvar resultados em arquivo? (s/n): ").lower().startswith('s')
    if salvar:
        # Gera nome de arquivo padrão (pode ser alterado)
        salvar_resultados(alvo, inicio, fim, abertas, tempo_total)


# ==================================================================
# PONTO DE ENTRADA DO SCRIPT
# ==================================================================
if __name__ == "__main__":
    print("\nATENÇÃO: Use apenas em laboratório autorizado!\n")
    main()