# Roteiro de Instalação

Passo a passo para instalar e executar o Simulador do Algoritmo do Banqueiro
em um computador novo. Os comandos abaixo são para Windows; as diferenças
para Linux e macOS estão indicadas.

## 1. Pré-requisitos

| Item | Versão | Observação |
|---|---|---|
| Python | 3.10 ou superior | Desenvolvido e testado no Python 3.14 |
| pip | o que vem com o Python | Instala as bibliotecas |
| Tkinter | o que vem com o Python | Interface gráfica (no Windows já vem junto) |
| Git | qualquer versão recente | Opcional: dá para baixar o projeto como ZIP |

Para conferir se o Python já está instalado, abra o **Prompt de Comando** ou o
**PowerShell** e rode:

```bash
python --version
```

Se aparecer `Python 3.10` ou mais novo, pule para o passo 3.

## 2. Instalar o Python (se necessário)

1. Baixe o instalador em https://www.python.org/downloads/
2. Na primeira tela do instalador, marque **"Add python.exe to PATH"**.
3. Clique em **"Install Now"**. A instalação padrão já inclui o Tkinter
   (opção "tcl/tk and IDLE").
4. Feche e abra o terminal de novo e confira com `python --version`.

> Linux (Debian/Ubuntu): `sudo apt install python3 python3-pip python3-venv python3-tk`
> macOS: instale pelo site python.org (o instalador oficial já inclui o Tkinter).

## 3. Baixar o projeto

**Opção A, com Git:**

```bash
git clone https://github.com/Acabaxi-Do-Alasca/dead_lock.git
cd dead_lock
```

**Opção B, sem Git:** abra https://github.com/Acabaxi-Do-Alasca/dead_lock,
clique em **Code → Download ZIP**, extraia o arquivo e abra um terminal dentro
da pasta extraída.

## 4. Criar um ambiente virtual (recomendado)

O ambiente virtual mantém as bibliotecas do projeto separadas das do sistema.

```bash
python -m venv .venv
```

Ative o ambiente:

| Terminal | Comando |
|---|---|
| Prompt de Comando (cmd) | `.venv\Scripts\activate.bat` |
| PowerShell | `.venv\Scripts\Activate.ps1` |
| Linux / macOS | `source .venv/bin/activate` |

Com o ambiente ativo, o terminal mostra `(.venv)` no começo da linha. Este
passo é opcional: sem ele, as bibliotecas são instaladas no Python do sistema.

## 5. Instalar as dependências

```bash
python -m pip install -r requirements.txt
```

Isso instala o **matplotlib** e o **networkx**. As demais bibliotecas usadas
(Tkinter, unittest, logging) já fazem parte do Python.

## 6. Verificar a instalação

Rode a suíte de testes automatizados:

```bash
python -m unittest discover -s tests -v
```

O resultado esperado termina com:

```
Ran 41 tests in 0.0XXs

OK
```

## 7. Executar o simulador

```bash
python main.py
```

A janela do simulador abre e o terminal passa a mostrar o **terminal de log**,
com cada passo do algoritmo. Mantenha os dois visíveis lado a lado. Uma cópia
do log é gravada em `logs/simulacao.log`.

Para um teste rápido: aba **Cenários prontos** → **Carregar Cenário C** → na aba
**Simulação**, faça os pedidos P0 → (0,1,0), P1 → (0,0,1), P2 → (1,0,0), depois
clique em **Verificar Deadlock** e em **Recuperar do Deadlock**.

## 8. Problemas comuns

| Problema | Solução |
|---|---|
| `'python' não é reconhecido como um comando` | O Python não está no PATH. No Windows, tente `py` no lugar de `python` (ex.: `py main.py`) ou reinstale marcando "Add python.exe to PATH". |
| `ModuleNotFoundError: No module named 'matplotlib'` (ou `networkx`) | As dependências não foram instaladas no mesmo Python que roda o programa. Rode `python -m pip install -r requirements.txt` com o mesmo comando `python` usado para abrir o simulador (e com o ambiente virtual ativo, se estiver usando um). |
| `ModuleNotFoundError: No module named 'tkinter'` | No Linux: `sudo apt install python3-tk`. No Windows: reinstale o Python mantendo marcada a opção "tcl/tk and IDLE". |
| O PowerShell não deixa ativar o `.venv` | Use o Prompt de Comando com `.venv\Scripts\activate.bat`, ou pule o passo 4. |
| A janela não abre (WSL, servidor ou SSH) | O simulador precisa de uma interface gráfica. Rode-o diretamente no Windows, Linux com desktop ou macOS. |
| Acentos estranhos no terminal | Use o Windows Terminal, o PowerShell ou o terminal do PyCharm/VS Code. O programa já envia o log em UTF-8. |
