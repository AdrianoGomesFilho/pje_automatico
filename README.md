# OBJETIVO DO PROJETO (Automação de publicações)
Agilizar a leitura de processos (publicações) no sistema PJE, ao mesmo tempo abrindo a plataforma online usada no escritório (Astrea, ADVBOX etc), dispensando várias etapas manuais.

Vídeo de apresentação do projeto no Instagram [@adrianogomes.adv](https://instagram.com/adrianogomes.adv).

# O QUE ELE FAZ?

Existem 3 tipos de automação
1 - Consulta de terceiros com astrea
2 - Consulta via token unico com astrea
3 - Somente astrea
4 - Somente PJE de terceiros
5 - Somente PJE (token unico) sem astrea

Obs: o Astrea é um sistema de gerenciamento de processos desenvolvido pela Aurum, acessado via navegador.

Motivo: cada automação atende uma necessidade do advogado. A mais completa é a primeira (consulta de terceiros com Astrea), a automação abre o PJE (no respectivo site do tribunal), assina com o token via PJE Office, abre a tela de consulta de terceiros, simultaneamente abre o Astrea (com login) no campo de pesquisa com o número do processo. A consulta de terceiros é mais viável em casos de escritórios que usam diversos tokens (o nosso caso). Atualmente o projeto suporta ações trabalhistas (que atende as necessidades da equipe que atuo) mas pode se adaptado para qualquer área.

# LINGUAGEM USADA
Python e suas bibliotecas (selenium, pyperclip, dotenv) automação via chromedriver

# COMO PODEREI USÁ-LO?
🟢PYTHON - instalação
🟢PIP
    ▪️curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    ▪️py get-pip.py
    ▪️Inclusão no path o script (variáveis do ambiente, do Windows):
    ▪️C:\Users\SEU_USER\AppData\Local\Programas\Python\Python312\Scripts
🟢Selenium - pip install selenium (cmd do windows)
🟢Pyperclip - pip install pyperclip (cmd do windows)
🟢Dotenv - pip install python-dotenv (cmd do windows)

