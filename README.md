# OBJETIVO DO PROJETO
Agilizar a leitura de processos (publicações) no sistema PJE, ao mesmo tempo abrindo a plataforma online usada no escritório (Astrea, ADVBOX etc), dispensando várias etapas manuais.

# O QUE ELE FAZ?
O usuário, ao copiar o trecho do número do processo (do e-mail, do site do sistema que usa no escritório, ou seja, de qualquer lugar do computador) o script reconhece o padrão de qual tribunal é o processo. Atualmente o script é voltado para uso interno do escritório @sgaadv (Instagram) para a equipe trabalhista.

Exemplo: recebo intimação do processo 0000776-xx.2019.5.6.0009, desejo ver o conteúdo no PJE. Ao copiar o script abre (automaticamente) uma aba específica do tribunal (neste caso, o TRT 6) no Chrome (podendo ser outro navegador, desde que configurado o script). Ele procede com o login via certificado e abre a consulta de terceiros em nova aba. O unico passo manual é completar o Captcha (tal procedimento poderá ser futuramente implementado).  Ao mesmo tempo o script abre o Astrea (sistema da Aurum, semelhante a outros sistemas como o ADVBOX) já pesquisando o número no campo de pesquisa, possibilitando o usuário saber a última providência adotada naquele processo, via sistema interno. Todas as automações realizadas podem ser modificadas de acordo com a necessidade de cada usuário.

**Porque a consulta de terceiros?** - No escritório em que foi implementado (@sgaadv) utilizamos diversos tokens (4), cada processo posssui somente um advogado habilitado e suas especifidades. Tal situação obrigaria a equipe a trocar a todo momento o token. Para driblar isso a consulta de terceiros entra em ação.

**Se é consulta de terceiros, para que certificado?** - A consulta de terceiros (assinada) possibilita ver todo o conteúdo, diferente da consulta pública (sem certificado). Neste caso o advogado vai ter acesso a todo o conteúdo.

# LINGUAGEM USADA
Python e suas bibliotecas (selenium, pyperclip, dotenv) automação via chromedriver
# COMO PODEREI USÁ-LO?
PYTHON - instalação
PIP
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py
    py get-pip.py
    Inclusão no path o script (variáveis do ambiente, do Windows):
    C:\Users\SEU_USER\AppData\Local\Programas\Python\Python312\Scripts
Selenium - pip install selenium (cmd do windows)
Pyperclip - pip install pyperclip (cmd do windows)
Dotenv - pip install python-dotenv (cmd do windows)
# SOBRE O DEV
Sou advogado, e quando me deparo com um problema que pode ser resolvido (ou amenizado) tento realizar um projeto. Procuro sempre aprender pela internet (YouTube, ChatGpt, sites). Codando e testando!
# PRÓXIMOS PASSOS
- Autocopiar número do processo (ex: quando clicar no numero, já copiar, iniciando o script) - possível problema, o script funciona em uma outra janela do browser
- Criar grupos de abas (cada número do processo vai criar uma aba de PJE e uma do Astrea) organizar melhor!
