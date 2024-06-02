# OBJETIVO DO PROJETO
Agilizar a leitura de processos (publicações) no sistema PJE, ao mesmo tempo abrindo a plataforma online usada no escritório (Astrea, ADVBOX etc), dispensando várias etapas manuais.

# SE VOCÊ USA UM ÚNICO TOKEN

# O QUE O ELE FAZ?

Exemplo: recebo uma intimação do processo 0000776-xx.2019.5.6.0009, desejo ver o conteúdo no PJE. Ao copiar o número do processo script abre (automaticamente) uma aba específica do tribunal (neste caso, o TRT 6), O código faz o login via certificado e abre o processo, tal como o procedimento manual.

Se o número do processo for de outro advogado, ele realiza automaticamente a pesquisa por processos de terceiros (ele identifica se o usuário está habilitado ou não). Neste caso o unico passo manual é completar o Captcha.

Ao mesmo tempo o script abre o Astrea (sistema da Aurum, semelhante a outros sistemas como o ADVBOX) já pesquisando o número no campo de pesquisa, possibilitando o usuário saber a última providência adotada naquele processo, via sistema interno. 

Todas as automações realizadas podem ser modificadas de acordo com a necessidade de cada usuário.

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

# PRÓXIMOS PASSOS
- Possibilitar a cópia com um único clique - (ex: quando clicar no numero, já copiar, iniciando o script)
- Alterar o título da aba
- Resolver captcha automaticamente
- Atualizar repositorio e implementar mudanças remotamente

# SOBRE O DEV
Para cada problema tento achar uma solução. Procuro sempre aprender pela internet (YouTube, ChatGpt, sites). Codando e testando!
Atualmente atuo como advogado na @sgaadv e implemento meus projetos lá
