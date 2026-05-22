```markdown
# Port Scanner 

**Curso:** Tecnólogo em Segurança Cibernética - SENAI  
**Disciplina:** Enumeração de Rede  
**Professor:** João Eduardo Luisi

---

## Sobre o Projeto

Este projeto consiste em um **scanner de portas TCP** desenvolvido em Python, com interface gráfica (Tkinter) e suporte a lista externa de serviços. Foi construído em três fases, seguindo as especificações da atividade prática.

### Funcionalidades

- Varredura de portas TCP (range definido pelo usuário)
- Detecção de portas **abertas**, **fechadas** ou **filtradas** (via timeout)
- **Multithreading** para aceleração da varredura
- **Banner grabbing** opcional (captura de banners dos serviços)
- Identificação de serviços a partir de arquivo externo (`servicos.txt`)
- Interface gráfica amigável (tema roxo, sem emojis)
- Salvamento automático de resultados em pasta `relatorios/`
- Opção de scan sequencial ou com threads

---

## Estrutura de Arquivos

```
PORT_SCAN/
| scan-fases/
| ├── scan-f1.py                # Fase 1: scanner de porta única (terminal)
| ├── scan-f3-completa.py       # Fase 3: scanner completo com multithreading e banner (terminal)
| ├── port_scanner.py           # Versão com interface gráfica (recomendada)
|── servicos.txt              # Arquivo de serviços (porta: nome)
├── relatorios/               # Pasta criada automaticamente para salvar os relatórios
└── README.md                 # Este arquivo
```

### Descrição dos Scripts

| Arquivo               | Descrição                                                                 |
|-----------------------|---------------------------------------------------------------------------|
| `scan-f1.py`          | Scanner de porta única – recebe IP e porta, exibe se está aberta/fechada. |
| `scan-f2.py`          | Scanner de range sequencial – varre intervalo de portas e mostra resumo.  |
| `scan-f3-completa.py` | Scanner avançado com multithreading, banner grabbing e salvamento em arquivo (terminal). |
| `port_scanner.py`     | Versão com **interface gráfica** (Tkinter). Inclui todas as funcionalidades e salva relatórios na pasta `relatorios/`. |
| `servicos.txt`        | Lista de serviços conhecidos (formato: `porta: nome`). Pode ser editada ou substituída. |

---

## Requisitos

- Python 3.6 ou superior
- Bibliotecas padrão:
  - `socket`
  - `threading`
  - `concurrent.futures`
  - `tkinter` (já inclusa no Python Windows; no Linux pode precisar instalar `python3-tk`)
  - `os`, `time`, `datetime`

Nenhuma biblioteca externa é necessária.

---

## Como Executar

### 1. Clone ou baixe os arquivos

Coloque todos os arquivos em uma mesma pasta.

### 2. Execute a versão desejada

#### Versão com Interface Gráfica (recomendada)

```bash
python port_scanner.py
```

#### Versões de terminal (Fases 1, 2 e 3)

```bash
python scan-f1.py
python scan-f2.py
python scan-f3-completa.py
```

### 3. Uso da Interface Gráfica

- **Alvo:** IP ou hostname (ex: `localhost`, `192.168.1.10`)
- **Range:** intervalo de portas no formato `inicio-fim` (ex: `20-1024`)
- **Opções:**
  - `Multithreading (rapido)`: acelera a varredura (recomendado)
  - `Capturar Banner (mais lento)`: tenta obter o banner do serviço
  - `Salvar resultados`: salva o relatório na pasta `relatorios/`
- Clique em **INICIAR SCAN** e aguarde.

Os resultados aparecem na área de texto e são salvos automaticamente (se a opção estiver marcada).

---

## Arquivo `servicos.txt`

O dicionário de serviços é carregado a partir deste arquivo.  
**Formato:** `porta: nome do serviço` (uma linha por porta).  
Linhas em branco ou começando com `#` são ignoradas.

Exemplo:
```
22: SSH
80: HTTP
443: HTTPS
```

Se o arquivo não for encontrado, o scanner usa um dicionário mínimo embutido.

Você pode substituir o arquivo por uma lista mais completa (a que acompanha o projeto já contém mais de 200 entradas).

---

## Limitações Conhecidas

- O scanner **não diferencia portas filtradas de fechadas** (timeout é tratado como fechada).
- Não implementa **SYN scan** (meio-aberto) – todas as verificações completam o handshake TCP.
- O banner grabbing é simples e pode não funcionar em serviços que exigem envio específico de comandos.
- A velocidade depende da latência da rede e do número de threads (padrão: 200).

Comparado ao **Nmap**, esta ferramenta é didática e muito mais limitada – ideal para aprendizado.

---

## Observações de Segurança

- **Use apenas em laboratórios autorizados** (redes isoladas, máquinas virtuais fornecidas pelo professor).
- **Nunca realize varreduras em redes de produção** ou sem permissão expressa.
- O escaneamento não autorizado pode ser considerado crime em muitas jurisdições.

---

## Exemplo de Saída (GUI)

```
Carregados 242 servicos do arquivo 'servicos.txt'
Iniciando scan em 192.168.1.100 - portas 20 a 100
Multithreading: SIM | Banner: NAO
  Porta 22 ABERTA - SSH
  Porta 80 ABERTA - HTTP
  Porta 443 ABERTA - HTTPS

=== RESUMO FINAL ===
Total de portas abertas: 3
Portas encontradas: [22, 80, 443]
Tempo total: 1.25 segundos

Resultados salvos em: relatorios/scan_192.168.1.100_20260521_153022.txt
```

---

## Próximos Passos (Sugestões de Melhoria)

- Adicionar suporte a **UDP scan**
- Implementar **SYN scan** (requer permissões de root)
- Permitir escolha do número máximo de threads
- Adicionar botão para cancelar o scan
- Exportar resultados em JSON ou CSV

---

## Licença

Projeto acadêmico – uso restrito ao ambiente de ensino.

# scan-TCP
