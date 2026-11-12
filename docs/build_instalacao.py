"""Gera o Roteiro de Instalação em .docx/.pdf (mesmo conteúdo de INSTALACAO.md).

Uso: python docs/build_instalacao.py
Gera: entrega/Roteiro_de_Instalacao.docx e .pdf
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from docx_helpers import (  # noqa: E402
    CAPA_CAMPOS, ENTREGA_DIR, add_bullets, add_code_block, add_command, add_heading, add_para,
    add_steps, add_table, add_title_page, new_doc, save_with_pdf,
)

OUT_PATH = os.path.join(ENTREGA_DIR, "Roteiro_de_Instalacao.docx")
REPO_URL = "https://github.com/Acabaxi-Do-Alasca/dead_lock"

doc = new_doc()
add_title_page(
    doc,
    "Simulador de Gerenciador de Deadlocks",
    "Roteiro de Instalação",
    "Passo a passo para instalar e executar o simulador do Algoritmo do Banqueiro "
    "em um computador novo.",
    CAPA_CAMPOS,
)

add_para(
    doc,
    "Os comandos abaixo são para Windows; as diferenças para Linux e macOS estão "
    "indicadas. Todo o procedimento leva cerca de 5 minutos."
)

add_heading(doc, "1. Pré-requisitos")
add_table(doc, ["Item", "Versão", "Observação"], [
    ["Python", "3.10 ou superior", "Desenvolvido e testado no Python 3.14."],
    ["pip", "o que vem com o Python", "Instala as bibliotecas."],
    ["Tkinter", "o que vem com o Python", "Interface gráfica (no Windows já vem junto)."],
    ["Git", "qualquer versão recente", "Opcional: dá para baixar o projeto como ZIP."],
], col_widths_cm=[3, 4.5, 8.5])
add_para(doc, "Para conferir se o Python já está instalado, abra o Prompt de Comando ou o PowerShell e rode:")
add_command(doc, "python --version")
add_para(doc, "Se aparecer Python 3.10 ou mais novo, pule para o passo 3.")

add_heading(doc, "2. Instalar o Python (se necessário)")
add_steps(doc, [
    "Baixe o instalador em https://www.python.org/downloads/",
    "Na primeira tela do instalador, marque \"Add python.exe to PATH\".",
    "Clique em \"Install Now\". A instalação padrão já inclui o Tkinter (opção \"tcl/tk and IDLE\").",
    "Feche e abra o terminal de novo e confira com python --version.",
])
add_bullets(doc, [
    "Linux (Debian/Ubuntu): sudo apt install python3 python3-pip python3-venv python3-tk",
    "macOS: instale pelo site python.org (o instalador oficial já inclui o Tkinter).",
])

add_heading(doc, "3. Baixar o projeto")
add_para(doc, "Opção A, com Git:", bold=True)
add_command(doc, f"git clone {REPO_URL}.git")
add_command(doc, "cd dead_lock")
add_para(doc, "Opção B, sem Git:", bold=True)
add_para(
    doc,
    f"Abra {REPO_URL}, clique em Code → Download ZIP, extraia o arquivo e abra "
    "um terminal dentro da pasta extraída."
)

add_heading(doc, "4. Criar um ambiente virtual (recomendado)")
add_para(doc, "O ambiente virtual mantém as bibliotecas do projeto separadas das do sistema:")
add_command(doc, "python -m venv .venv")
add_para(doc, "Ative o ambiente:")
add_table(doc, ["Terminal", "Comando"], [
    ["Prompt de Comando (cmd)", ".venv\\Scripts\\activate.bat"],
    ["PowerShell", ".venv\\Scripts\\Activate.ps1"],
    ["Linux / macOS", "source .venv/bin/activate"],
], col_widths_cm=[6, 10])
add_para(
    doc,
    "Com o ambiente ativo, o terminal mostra (.venv) no começo da linha. Este "
    "passo é opcional: sem ele, as bibliotecas são instaladas no Python do sistema."
)

add_heading(doc, "5. Instalar as dependências")
add_command(doc, "python -m pip install -r requirements.txt")
add_para(
    doc,
    "Isso instala o matplotlib e o networkx. As demais bibliotecas usadas "
    "(Tkinter, unittest, logging) já fazem parte do Python."
)

add_heading(doc, "6. Verificar a instalação")
add_para(doc, "Rode a suíte de testes automatizados:")
add_command(doc, "python -m unittest discover -s tests -v")
add_para(doc, "O resultado esperado termina com:")
add_code_block(doc, ["Ran 41 tests in 0.0XXs", "", "OK"], font_size=9,
               color_for_line=lambda l: "8CD17D" if l == "OK" else "D4D4D4")

add_heading(doc, "7. Executar o simulador")
add_command(doc, "python main.py")
add_para(
    doc,
    "A janela do simulador abre e o terminal passa a mostrar o terminal de log, "
    "com cada passo do algoritmo. Mantenha os dois visíveis lado a lado. Uma "
    "cópia do log é gravada em logs/simulacao.log."
)
add_para(doc, "Teste rápido:", bold=True)
add_steps(doc, [
    "Aba Cenários prontos → Carregar Cenário C.",
    "Na aba Simulação, faça os pedidos P0 → (0,1,0), P1 → (0,0,1) e P2 → (1,0,0).",
    "Clique em Verificar Deadlock e depois em Recuperar do Deadlock (fim do painel da direita).",
])

add_heading(doc, "8. Problemas comuns")
add_table(doc, ["Problema", "Solução"], [
    ["'python' não é reconhecido como um comando",
     "O Python não está no PATH. No Windows, tente py no lugar de python (ex.: py main.py) ou reinstale marcando \"Add python.exe to PATH\"."],
    ["ModuleNotFoundError: No module named 'matplotlib' (ou 'networkx')",
     "As dependências não foram instaladas no mesmo Python que roda o programa. Rode python -m pip install -r requirements.txt com o mesmo comando python usado para abrir o simulador (e com o ambiente virtual ativo, se estiver usando um)."],
    ["ModuleNotFoundError: No module named 'tkinter'",
     "No Linux: sudo apt install python3-tk. No Windows: reinstale o Python mantendo marcada a opção \"tcl/tk and IDLE\"."],
    ["O PowerShell não deixa ativar o .venv",
     "Use o Prompt de Comando com .venv\\Scripts\\activate.bat, ou pule o passo 4."],
    ["A janela não abre (WSL, servidor ou SSH)",
     "O simulador precisa de uma interface gráfica. Rode-o diretamente no Windows, Linux com desktop ou macOS."],
    ["Acentos estranhos no terminal",
     "Use o Windows Terminal, o PowerShell ou o terminal do PyCharm/VS Code. O programa já envia o log em UTF-8."],
], col_widths_cm=[5.5, 10.5], font_size=10)

save_with_pdf(doc, OUT_PATH)
