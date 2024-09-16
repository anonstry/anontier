# Anodos • Incognito

_Um porto-seguro para troca de mensagens._

> Nosso trabalho aqui é tentar trazer uma rede mais protegida sem discriminação ou violação/abuso.


### Inicialização

Você não precisa utilizar o `requirements.txt`!  Você pode usar o `pipx` (python3-pipx) e usar o comando `pipx install hatch` para iniciarmos. Uma vez tendo o hatch, basta seguir o passo a passo a baixo.

1. Tenha o MongoDB rodando e configure o link em `settings.toml`
2. Configure suas credenciais no arquivo: `secrets.example.toml`
3. E por último rode `hatch run python -m src` e veja o funcionameno

#### Recommended settings
Não é preciso muito para rodar sua própria instância. No entanto, até por não usarmos cache no Telegram (algo como copiar as mensagens e usar elas prontas ao invés de sempre montar todas), é bom que tenha uma rápida internet para o envio de mídias (os assets), talvez 100MBs.


### Support

Any bugs or something to report, send a e-mail to `anonstry@protonmail.com`

Se você quiser colaborar com o projeto, seja bem-vindo para rodar sua própria instância, sugerir mudanças ou então apoiar o projeto com doações via Monero/XMR no endereço de carteira: _`843zPnwtKfUZsYDTGj5vbv9tX7yTdbBjBgNuiCF5xAmeWqbPqEs769FbyJNi5qCStz5cnvJwgtppdamCKgfPWWmB6R67W7Z`_