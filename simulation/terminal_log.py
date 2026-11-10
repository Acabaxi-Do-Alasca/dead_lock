"""Terminal de log: mostra no console, passo a passo, o raciocínio do algoritmo.

Toda entrada registrada via `SystemState.log()` é enviada ao logger
"banqueiro". Este módulo liga esse logger a dois destinos:

1. O terminal (stdout), com uma cor por categoria e uma linha separadora a
   cada nova requisição -- é o "terminal de log" exibido durante a
   apresentação, rodando ao lado da janela do simulador.
2. O arquivo `logs/simulacao.log`, sem cores e com horário, para consulta
   posterior (é recriado a cada execução do programa).

Formato de cada linha:  [passo] CATEGORIA      | mensagem
"""

import logging
import os
import sys

LOGGER_NAME = "banqueiro"

RESET = "\033[0m"
CATEGORY_COLORS = {
    "REQUEST": "\033[1;36m",        # ciano negrito: um processo pediu recursos
    "SAFETY_CHECK": "\033[37m",     # cinza: comparação Need <= Work
    "DEADLOCK_CHECK": "\033[37m",   # cinza: comparação Request <= Work
    "RELEASE": "\033[34m",          # azul: processo (simulado) devolve recursos
    "GRANT": "\033[1;32m",          # verde: requisição concedida
    "DENY": "\033[33m",             # amarelo: requisição não atendida agora
    "ROLLBACK": "\033[1;31m",       # vermelho: alocação desfeita (estado inseguro)
    "RESULT": "\033[1;35m",         # magenta: conclusão de uma verificação
    "RECOVERY": "\033[1;31m",       # vermelho: tratamento de deadlock
    "ABORT": "\033[1;31m",          # vermelho: processo-vítima abortado
    "INFO": "",
}
SEPARATOR_BEFORE = {"REQUEST", "RECOVERY"}


class ConsoleFormatter(logging.Formatter):
    def __init__(self, use_colors: bool):
        super().__init__()
        self.use_colors = use_colors

    def format(self, record: logging.LogRecord) -> str:
        category = getattr(record, "category", "INFO")
        step = getattr(record, "step", 0)
        line = f"[{step:04d}] {category:<14} | {record.getMessage()}"
        if self.use_colors:
            color = CATEGORY_COLORS.get(category, "")
            if color:
                line = f"{color}{line}{RESET}"
        if category in SEPARATOR_BEFORE:
            line = "-" * 100 + "\n" + line
        return line


class FileFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        category = getattr(record, "category", "INFO")
        step = getattr(record, "step", 0)
        time = self.formatTime(record, "%H:%M:%S")
        return f"{time} [{step:04d}] {category:<14} | {record.getMessage()}"


def setup_terminal_log(log_dir: str | None = None) -> logging.Logger:
    """Configura o logger "banqueiro" para escrever no terminal e em arquivo."""
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False
    logger.handlers.clear()

    if sys.stdout is not None:
        if os.name == "nt":
            os.system("")  # habilita códigos de cor ANSI no console do Windows
        try:
            # UTF-8 para os acentos saírem certos em qualquer terminal (cmd,
            # PowerShell, Git Bash, terminal do PyCharm/VS Code), e escrita
            # linha a linha para nada ficar preso em buffer.
            sys.stdout.reconfigure(encoding="utf-8", errors="replace", line_buffering=True)
        except (AttributeError, ValueError):
            pass
        console = logging.StreamHandler(sys.stdout)
        console.setFormatter(ConsoleFormatter(use_colors=sys.stdout.isatty()))
        logger.addHandler(console)

    if log_dir is not None:
        os.makedirs(log_dir, exist_ok=True)
        file_handler = logging.FileHandler(
            os.path.join(log_dir, "simulacao.log"), mode="w", encoding="utf-8"
        )
        file_handler.setFormatter(FileFormatter())
        logger.addHandler(file_handler)

    return logger


def print_banner() -> None:
    if sys.stdout is None:
        return
    print("=" * 100)
    print(" TERMINAL DE LOG -- Simulador do Algoritmo do Banqueiro")
    print(" Cada passo do algoritmo aparece abaixo enquanto você usa a janela do simulador.")
    print(" Formato: [passo] CATEGORIA | mensagem   (cópia em logs/simulacao.log)")
    print("=" * 100)
