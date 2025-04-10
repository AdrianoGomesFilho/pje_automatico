![Logo](logowide.png)
# OBJETIVO DO PROJETO
Automação que, ao detectar a cópia de um número de processo, abre automaticamente a página correspondente do PJE e, se desejado, também o sistema utilizado no escritório (atualmente configurado para o Astrea). Voltado no presente momento para PJE trabalhista. Especialmente focado para escritórios que usam vários tokens de vários advogados e possui processos em vários TRTS. O acesso ao processo é mantido sigiloso (ou seja, se você acessar processos de outros advogados o sistema não registra).

Vídeo de apresentação do projeto no Instagram (obs: o programa foi significativamente aprimorado após o vídeo). Pretendo regravar o vídeo futuramente! [@adrianogomes.adv](https://instagram.com/adrianogomes.adv).

# O QUE ELE FAZ?

Ao copiar o número do processo (formato xxxxxxx-xx.xxxx.5.xx.xxxx) o programa dispara, abrindo o PJE e o sistema (site) que o escritório utiliza (ex: Astrea). O usuário pode optar para usar exclusivamente o PJE, Astrea ou ambos.

Melhoria recente: a automação agora permite abrir processos de outros advogados com a mesma visualização dos processos pessoais (tudo isso sem deixar rastros de acesso de terceiros).

# COMO POSSO USAR A AUTOMAÇÃO?
Baixe o arquivo .exe (na pasta "dist"), certifique-se de que o Google Chrome está instalado (e o PJE Office Pro, caso use token), e inicie o programa.
A próxima etapa é preencher as credenciais (obs: não é obrigatório preencher certos dados a depender do método que você deseje usar). Exemplo: desejo abrir os processos no token - não é necessário colocar CPF e senha de login (PDPJ).

É altamente recomendável criar credenciais no login PDPJ (os tribunais já começaram a aderir a este login)

Qualquer dificuldade pode entrar em contato comigo 81992811496📲

# LINGUAGEM USADA
Python e suas bibliotecas, automação via chromedriver

# MOTIVAÇÃO
Criei a automação para me auxiliar (e auxiliar a equipe do escritório) na hora de abrir os processos. Atualmente a justiça usa muitos sistemas (trabalhistas são 24 regionais no total, cada um possuindo 2 graus, o que totaliza 48, somado ao TST que possui 2 - o PJE e o sistema mais antigo). Ao total, um advogado que possua processos espalhados por todo o Brasil precisa fazer malabarismos diariamente para acessar seus processos. Isso é ainda mais agravado quando existem processos de outros advogados associados.





