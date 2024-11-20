# OBJETIVO DO PROJETO (Automação de publicações)
Agilizar a leitura de processos (publicações) no sistema PJE, ao mesmo tempo abrindo a plataforma online usada no escritório (Astrea, ADVBOX etc), dispensando várias etapas manuais.

Vídeo de apresentação do projeto no Instagram [@adrianogomes.adv](https://instagram.com/adrianogomes.adv).

# O QUE ELE FAZ?

Existem 3 tipos de automação
1 - Consulta de terceiros com astrea (consulta terceiros 2.0)
2 - Consulta de terceiros sem astrea (consulta terceiros 2.0 sem astrea.py)
3 - Somente astrea (astrea only.py)

Motivo: cada automação atende uma necessidade do advogado. Pessoalmente entendo que o "somente astrea" atende melhor no momento, pois muitas intimações já possuem o teor do que se trata, bastando lançar no sistema (Astrea) o que for necessário (mais rápida e menos passível de erros). Entretanto, para quem gosta de abrir simultaneamente o PJE e o sistema (Astrea), para ter segurança de ler o processo, a "consulta terceiros 2.0" atende bem, apesar da automação ser mais "lenta" e passível de erros.

Exemplo: recebo uma intimação do processo 0000776-xx.2019.5.6.0009, desejo ver o conteúdo no PJE. Ao copiar o número do processo script abre (automaticamente) uma aba específica do tribunal (neste caso, o TRT 6), O código faz o login via certificado e abre o processo, tal como o procedimento manual. O script realiza automaticamente a pesquisa por processos de terceiros. Neste caso o unico passo manual é selecionar o grau (instância) e completar o Captcha.
Ao mesmo tempo o script abre o seu sistema de gestão (Astrea, ADVBOX etc) e já faz a pesquisa do número do processo.
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

