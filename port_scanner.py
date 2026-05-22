"""
PORT SCANNER COM INTERFACE GRÁFICA - VERSÃO COMPLETA
----------------------------------------------------
Autor: Aluno SENAI - Sprint 3
Descrição: Ferramenta educacional para varredura de portas TCP.
           Permite escanear um range de portas em um alvo, com opção de
           multithreading, banner grabbing e salvamento de relatórios.
           Interface gráfica desenvolvida com Tkinter (tema roxo).

Funcionalidades:
- Escaneamento de portas em um alvo (IP ou hostname)
- Range de portas personalizável (ex: 1-1024)
- Multithreading para acelerar (ThreadPoolExecutor)
- Opção de banner grabbing (identificação de serviços)
- Interface gráfica amigável com barra de progresso
- Resultados exibidos em tempo real
- Resumo final com tempo total
- Salvamento em arquivo .txt dentro da pasta "relatorios" (criada automaticamente)

Aviso: Use apenas em ambientes autorizados (laboratório didático).
"""

# ======================================================================
# IMPORTAÇÃO DAS BIBLIOTECAS
# ======================================================================

import socket               # Fornece funções de rede (criação de sockets TCP)
import time                 # Para medir a duração do scan (time.time())
import threading            # Permite executar o scan em uma thread separada (não travar a GUI)
import concurrent.futures   # Facilita o uso de pool de threads (ThreadPoolExecutor)
import tkinter as tk        # Biblioteca padrão para interfaces gráficas
from tkinter import scrolledtext, messagebox, ttk  # Widgets específicos: área de texto com scroll, popups, botões estilizados
from datetime import datetime  # Para gerar timestamps nos nomes dos arquivos e relatórios
import os                   # Para verificar existência de arquivos e criar pastas

# ======================================================================
# CARREGAMENTO DE SERVIÇOS A PARTIR DE ARQUIVO EXTERNO
# ======================================================================

def carregar_servicos(arquivo="servicos.txt"):
    """
    Carrega um dicionário que mapeia números de porta para nomes de serviço.
    O arquivo deve ter o formato: "porta: nome_do_servico" (uma linha por porta).
    Linhas vazias ou começando com '#' são ignoradas.

    Se o arquivo não existir, usa um dicionário mínimo embutido (fallback).
    """
    servicos = {}

    # Verifica se o arquivo existe
    if not os.path.exists(arquivo):
        print(f"Arquivo {arquivo} nao encontrado. Usando servicos basicos.")
        # Dicionário mínimo com as portas mais comuns (para não ficar sem referência)
        return {
            20: "FTP-DATA", 21: "FTP", 22: "SSH", 23: "Telnet",
            25: "SMTP", 53: "DNS", 80: "HTTP", 110: "POP3",
            143: "IMAP", 443: "HTTPS", 993: "IMAPS", 995: "POP3S",
            3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 8080: "HTTP-Alt"
        }

    try:
        # Abre o arquivo em modo leitura com codificação UTF-8
        with open(arquivo, "r", encoding="utf-8") as f:
            for linha in f:
                linha = linha.strip()          # Remove espaços e quebra de linha
                if not linha or linha.startswith("#"):
                    continue                   # Pula linhas vazias ou comentários
                if ":" not in linha:
                    continue                   # Formato inválido, pula
                porta_str, nome = linha.split(":", 1)   # Divide no primeiro ':'
                porta = int(porta_str.strip())          # Converte para inteiro
                nome = nome.strip()                     # Remove espaços do nome
                servicos[porta] = nome
        print(f"Carregados {len(servicos)} servicos do arquivo {arquivo}")
    except Exception as e:
        print(f"Erro ao ler {arquivo}: {e}. Usando dicionario basico.")
        # Fallback mínimo caso ocorra erro na leitura
        servicos = {80: "HTTP", 443: "HTTPS", 22: "SSH", 21: "FTP"}

    return servicos

# Dicionário global de serviços (será usado em todo o programa)
SERVICOS = carregar_servicos()

# ======================================================================
# FUNÇÕES DE BANNER GRABBING E VERIFICAÇÃO DE PORTA
# ======================================================================

def banner_grabbing(host, porta):
    """
    Tenta se conectar a uma porta já aberta e capturar o banner (mensagem de boas-vindas)
    que o serviço envia. Isso ajuda a identificar o software e versão.
    Retorna o banner como string ou "Nao capturado" em caso de falha.
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Cria socket TCP/IP
        s.settimeout(2)         # Aguarda no máximo 2 segundos por resposta
        s.connect((host, porta)) # Conecta à porta
        s.send(b"\n")           # Envia um caractere de nova linha (muitos serviços respondem a isso)
        banner = s.recv(1024).decode().strip()  # Lê até 1024 bytes e decodifica
        s.close()
        return banner if banner else "Banner vazio"
    except:
        return "Nao capturado"

def verificar_porta(host, porta, fazer_banner=False):
    """
    Verifica se uma determinada porta está aberta.
    Retorna uma tupla: (porta, bool_aberta, banner_ou_None)
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)                 # Timeout de 1 segundo para evitar travamentos
        # connect_ex retorna 0 em caso de sucesso (porta aberta), ou código de erro
        codigo = s.connect_ex((host, porta))
        if codigo == 0:                 # Porta aberta
            banner = None
            if fazer_banner:            # Se o usuário optou por banner grabbing
                banner = banner_grabbing(host, porta)
            s.close()
            return (porta, True, banner)
        else:                           # Porta fechada ou filtrada
            s.close()
            return (porta, False, None)
    except:
        # Qualquer exceção (ex: host inválido) tratamos como porta não acessível
        return (porta, False, None)

# ======================================================================
# CLASSE PRINCIPAL DA INTERFACE GRÁFICA (Tkinter)
# ======================================================================

class PortScannerGUI:
    """
    Cria a janela principal, gerencia os parâmetros do scan, exibe resultados
    e executa o scan em uma thread separada para não congelar a interface.
    """

    def __init__(self, root):
        """
        Construtor: configura a janela, as cores, os widgets e as variáveis de controle.
        """
        self.root = root
        self.root.title("Port Scanner - Servicos Externos")
        self.root.geometry("900x650")      # Largura x Altura inicial
        self.root.resizable(True, True)    # Permite redimensionar

        # Paleta de cores - tema roxo (sem emojis)
        cor_fundo = "#2E1C40"       # Roxo escuro (fundo da janela)
        cor_frame = "#3D2B56"       # Roxo médio (frames)
        cor_botao = "#7B4F9C"       # Roxo claro (botões)
        cor_texto = "#F0E6FF"       # Texto claro
        cor_resultado_bg = "#1A1125" # Fundo da área de resultados (quase preto)
        cor_resultado_fg = "#D9C9F0" # Texto dos resultados

        self.root.configure(bg=cor_fundo)

        # Estilização dos widgets usando ttk.Style (tema "clam" permite customização)
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TLabel", background=cor_fundo, foreground=cor_texto, font=("Segoe UI", 9))
        style.configure("TButton", background=cor_botao, foreground="white", font=("Segoe UI", 9, "bold"))
        style.map("TButton", background=[("active", "#9B6FC0")])  # Cor ao passar o mouse
        style.configure("TLabelframe", background=cor_fundo, foreground=cor_texto, font=("Segoe UI", 10, "bold"))
        style.configure("TLabelframe.Label", background=cor_fundo, foreground=cor_texto)
        style.configure("TCheckbutton", background=cor_fundo, foreground=cor_texto, font=("Segoe UI", 9))
        style.configure("TProgressbar", troughcolor=cor_frame, background=cor_botao)

        # Variáveis de controle (associadas aos campos de entrada e checkboxes)
        self.alvo_var = tk.StringVar(value="localhost")
        self.range_var = tk.StringVar(value="20-1024")
        self.usar_threads_var = tk.BooleanVar(value=True)
        self.banner_var = tk.BooleanVar(value=False)
        self.salvar_var = tk.BooleanVar(value=True)

        # ---------- Frame de parâmetros ----------
        frame_entrada = ttk.LabelFrame(root, text="Parametros do Scan", padding=10)
        frame_entrada.pack(fill="x", padx=10, pady=5)

        # Linha 0: Alvo
        ttk.Label(frame_entrada, text="Alvo (IP ou hostname):").grid(row=0, column=0, sticky="w", pady=5)
        entry_alvo = ttk.Entry(frame_entrada, textvariable=self.alvo_var, width=40, font=("Consolas", 9))
        entry_alvo.grid(row=0, column=1, sticky="w", padx=5)

        # Linha 1: Range
        ttk.Label(frame_entrada, text="Range de portas (ex: 1-1024):").grid(row=1, column=0, sticky="w", pady=5)
        ttk.Entry(frame_entrada, textvariable=self.range_var, width=20, font=("Consolas", 9)).grid(row=1, column=1, sticky="w", padx=5)

        # Linha 2: Checkboxes (opções)
        frame_opcoes = ttk.Frame(frame_entrada)
        frame_opcoes.grid(row=2, column=0, columnspan=2, sticky="w", pady=5)
        ttk.Checkbutton(frame_opcoes, text="Multithreading (rapido)", variable=self.usar_threads_var).pack(side="left", padx=5)
        ttk.Checkbutton(frame_opcoes, text="Capturar Banner (mais lento)", variable=self.banner_var).pack(side="left", padx=5)
        ttk.Checkbutton(frame_opcoes, text="Salvar resultados", variable=self.salvar_var).pack(side="left", padx=5)

        # Botão de início (aciona a thread de scan)
        self.btn_iniciar = ttk.Button(frame_entrada, text="INICIAR SCAN", command=self.iniciar_scan_thread)
        self.btn_iniciar.grid(row=3, column=0, columnspan=2, pady=10)

        # ---------- Barra de progresso (indeterminada) ----------
        self.progresso = ttk.Progressbar(root, mode='indeterminate')
        self.progresso.pack(fill="x", padx=10, pady=5)

        # ---------- Área de resultados (com scroll) ----------
        frame_resultado = ttk.LabelFrame(root, text="Resultados do Scan", padding=5)
        frame_resultado.pack(fill="both", expand=True, padx=10, pady=5)

        self.txt_resultado = scrolledtext.ScrolledText(
            frame_resultado, wrap=tk.WORD, font=("Consolas", 9),
            bg=cor_resultado_bg, fg=cor_resultado_fg,
            insertbackground="white"  # Cor do cursor de digitação
        )
        self.txt_resultado.pack(fill="both", expand=True)

        # ---------- Barra de status (rodapé) ----------
        self.status_var = tk.StringVar(value="Pronto. Aguardando comando.")
        status_bar = ttk.Label(root, textvariable=self.status_var, relief="sunken", anchor="w")
        status_bar.pack(fill="x", padx=10, pady=5)

        # Log inicial informando quantos serviços foram carregados
        self.log(f"Carregados {len(SERVICOS)} servicos do arquivo 'servicos.txt'")

    # ------------------------------------------------------------------
    # Métodos auxiliares da interface
    # ------------------------------------------------------------------

    def log(self, mensagem):
        """
        Insere uma mensagem na área de resultados (thread-safe).
        Usa 'after' para agendar a inserção na thread principal do Tkinter.
        """
        def _log():
            self.txt_resultado.insert(tk.END, mensagem + "\n")
            self.txt_resultado.see(tk.END)   # Rola automaticamente para o final
        self.root.after(0, _log)

    def limpar_resultados(self):
        """Limpa todo o conteúdo da área de resultados."""
        self.txt_resultado.delete(1.0, tk.END)

    # ------------------------------------------------------------------
    # Métodos de controle do scan (threading)
    # ------------------------------------------------------------------

    def iniciar_scan_thread(self):
        """
        Valida os parâmetros e inicia o scan em uma thread separada.
        Isso impede que a interface gráfica congele durante a varredura.
        """
        # Desativa o botão e inicia a barra de progresso
        self.btn_iniciar.config(state="disabled")
        self.progresso.start()
        self.limpar_resultados()
        self.status_var.set("Escaneando... aguarde")

        # Obtém os valores dos campos
        alvo = self.alvo_var.get().strip()
        range_str = self.range_var.get().strip()
        usar_threads = self.usar_threads_var.get()
        capturar_banner = self.banner_var.get()
        salvar = self.salvar_var.get()

        # Valida o range de portas (formato "inicio-fim", valores entre 1 e 65535)
        try:
            inicio, fim = map(int, range_str.split("-"))
            if inicio > fim or inicio < 1 or fim > 65535:
                raise ValueError
        except:
            messagebox.showerror("Erro", "Range invalido. Use formato: inicio-fim (ex: 1-1024) e portas entre 1 e 65535.")
            self.btn_iniciar.config(state="normal")
            self.progresso.stop()
            self.status_var.set("Erro no range.")
            return

        # Cria e inicia a thread que executará o scan (daemon = True para encerrar junto com o programa)
        thread = threading.Thread(target=self.executar_scan, args=(alvo, inicio, fim, usar_threads, capturar_banner, salvar))
        thread.daemon = True
        thread.start()

    def executar_scan(self, alvo, inicio, fim, usar_threads, capturar_banner, salvar):
        """
        Executa efetivamente o scan (roda em thread separada).
        Realiza a varredura sequencial ou com multithreading, exibe resultados
        e salva o relatório se solicitado.
        """
        tempo_inicio = time.time()
        portas_abertas = []

        # Registro inicial no log
        self.log(f"Iniciando scan em {alvo} - portas {inicio} a {fim}")
        self.log(f"Multithreading: {'SIM' if usar_threads else 'NAO'} | Banner: {'SIM' if capturar_banner else 'NAO'}")

        if usar_threads:
            # ---------- MODO COM MULTITHREADING (rápido) ----------
            portas = list(range(inicio, fim+1))
            # Cria um pool de até 200 threads simultâneas
            with concurrent.futures.ThreadPoolExecutor(max_workers=200) as executor:
                # Submete uma tarefa para cada porta; futures é um dicionário {future: porta}
                futures = {executor.submit(verificar_porta, alvo, p, capturar_banner): p for p in portas}
                # Itera à medida que as tarefas vão sendo concluídas
                for future in concurrent.futures.as_completed(futures):
                    porta, is_open, banner = future.result()
                    if is_open:
                        portas_abertas.append(porta)
                        servico = SERVICOS.get(porta, "Desconhecido")
                        self.log(f"  Porta {porta} ABERTA - {servico}")
                        if capturar_banner and banner:
                            self.log(f"      Banner: {banner[:100]}")
        else:
            # ---------- MODO SEQUENCIAL (mais lento, útil para testes) ----------
            for porta in range(inicio, fim+1):
                porta, is_open, banner = verificar_porta(alvo, porta, capturar_banner)
                if is_open:
                    portas_abertas.append(porta)
                    servico = SERVICOS.get(porta, "Desconhecido")
                    self.log(f"  Porta {porta} ABERTA - {servico}")
                    if capturar_banner and banner:
                        self.log(f"      Banner: {banner[:100]}")

        tempo_total = time.time() - tempo_inicio

        # Exibe o resumo final
        self.log("\n=== RESUMO FINAL ===")
        self.log(f"Total de portas abertas: {len(portas_abertas)}")
        if portas_abertas:
            self.log(f"Portas encontradas: {portas_abertas}")
        else:
            self.log("Nenhuma porta aberta encontrada.")
        self.log(f"Tempo total: {tempo_total:.2f} segundos")

        # ========== SALVAMENTO DO RELATÓRIO ==========
        if salvar:
            # Cria a pasta "relatorios" se não existir
            pasta_relatorios = "relatorios"
            if not os.path.exists(pasta_relatorios):
                os.makedirs(pasta_relatorios)

            # Gera um nome único com timestamp (ano_mes_dia_hora_minuto_segundo)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            nome_arquivo = f"scan_{alvo}_{timestamp}.txt"
            caminho_completo = os.path.join(pasta_relatorios, nome_arquivo)

            try:
                with open(caminho_completo, "w", encoding="utf-8") as f:
                    f.write(f"SCAN REALIZADO EM: {datetime.now().strftime('%d/%m/%Y %H:%M:%S')}\n")
                    f.write(f"ALVO: {alvo}\n")
                    f.write(f"RANGE: {inicio}-{fim}\n")
                    f.write(f"TEMPO TOTAL: {tempo_total:.2f}s\n")
                    f.write(f"TOTAL PORTAS ABERTAS: {len(portas_abertas)}\n")
                    f.write("PORTAS ABERTAS:\n")
                    for p in portas_abertas:
                        servico = SERVICOS.get(p, "Desconhecido")
                        f.write(f"  {p} - {servico}\n")
                self.log(f"\nResultados salvos em: {caminho_completo}")
            except Exception as e:
                self.log(f"\nErro ao salvar arquivo: {e}")

        # Atualiza a barra de status e reativa o botão (usando 'after' por segurança)
        self.status_var.set(f"Scan concluido em {tempo_total:.2f}s - {len(portas_abertas)} portas abertas")
        self.root.after(0, lambda: self.btn_iniciar.config(state="normal"))
        self.root.after(0, self.progresso.stop)


# ======================================================================
# PONTO DE ENTRADA DO PROGRAMA
# ======================================================================

if __name__ == "__main__":
    # Mensagem de alerta exibida no terminal (não na GUI)
    print("Atencao: Use apenas em laboratorio autorizado!")

    # Cria a janela principal do Tkinter
    root = tk.Tk()
    # Instancia a nossa classe, que constrói toda a interface
    app = PortScannerGUI(root)
    # Inicia o loop de eventos da interface (mantém a janela aberta)
    root.mainloop()