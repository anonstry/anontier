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


### 2.0.0 & Manifesto

Mantemos as conversas de um jeito incógnito, tentando ao máximo unir privacidade com anonimato. Mas devemos questionar uma coisa: o Telegram realmente não lê as mensagens mandadas para o bot?! Saiba que: se um bot for banido mesmo com o encaminhamento de mensagem sendo restrito/desabilitado, o Telegram precisou de alguma forma acessar uma mensagem (ou também uma mídia) em um ambiente privado!

Se o Telegram realmente fosse a favor da privacidade, ele melhoraria o **Secret Chat**, que supostamente é criptografado de ponta-a-ponta... Estranho esse descaso e aparente desinteresse por parte da plataforma, não é? **Não parece algo desapercebido**, e sim negligência proprosital. Por isso buscamos alternativas.

Nós temos a idea de expandir mais, algo como uma plataforma indie. E isso irá requerer investimento. Todavia, você também pode usar outras redes, sendo algumas das nossas recomendações:
- Simplex
- Session
- Matrix/Element

Até pensamos em uma idea de **federações**, até pra dificultar a censura, mas seria preciso um resolvedor para uma interligação entre instância a outra. Mas você pode fazer algo assim, talvez localmente ou criando seu próprio diretório. Sem dúvidas vai precisar de um certo entendimento com bancos de dados também. Inclusive, sinta-se à vontade para melhorar o modelo em uso atual, desde que planeje as migrações.

~~As salas devem por padrão terem todas as restrições padrões desativas. A restrição deve ocorrer por parte do usuário e deve ser OPCIONAL a partipação ou não-partipação dos demais.~~

~~Talvez a solução para não usar Redis e usar apenas Mongo localmente (com cópia remota reserva) seja por uma senha para acessar o banco e de alguma forma — talvez com um espaço a mais no Bash — passar ela de forma oculta/temporária.~~
~~De acordo com os termos de responsabilidade, não é culpa do software/código o que nele é compartilhado, isto é, a moderação é APENAS por parte dos usuários! Ok? Se há dúvida, confira por conta própria e veja que não há alguma forma criada para supervisionar o que é dito. Mas não sabemos as formas de censura que podem tentar impor às instâncias, portanto, como proteção, tente optar por Monero.~~
~~_XMR, ou Monero, tem uma intíma ligação com o anonimato e por anos continua sendo resistente à censura._~~

Para internacionalização podemos usar criar algo como um `Capptioner` (um gerenciador de legendas), por exemplo, messages.en.message & messages.pt.message, or something like this.

##### ~~Anúncios~~
_Nem de flores vive o mundo._
~~Se você roda sua instância, um gasto irá ter. Então consideremos a opção de rodar anúncios para usuários não-apoiadores dela, ok? É justo, ao meu ver, afinal, é uma forma de sustentabilizar a rede. Por exemplo: `if not user.premium and len(user.messages_count) % 100...`~~


### Support

Any bugs or something to report, send a e-mail to `anonstry@protonmail.com`

Se você quiser colaborar com o projeto, seja bem-vindo para rodar sua própria instância, sugerir mudanças ou então apoiar o projeto com doações via Monero/XMR no endereço de carteira: _`843zPnwtKfUZsYDTGj5vbv9tX7yTdbBjBgNuiCF5xAmeWqbPqEs769FbyJNi5qCStz5cnvJwgtppdamCKgfPWWmB6R67W7Z`_


### Mapa de funcionalidades

* **Basic**
    - [x] Mailing
    - [ ] Mailing with an invite
    - [ ] Scan all non-registered messages and register them in order
    - [ ] ~~Federations (connect to other instancies)~~
    - [ ] ~~Use a personal group with topics and join in multiple rooms~~ 
    - [ ] Enable the tag/name option
    - [ ] Enable the forward-with-sign option
    - [ ] Confirmation before joining in a custom room
    - [ ] Change the current room size
    - [x] Mimic (replicate) message.edit
    - [x] Mimic (replicate) message.delete
    - [ ] Inline mailing
    - [ ] Inline mailing with an invite to your current room
    - [ ] ~~A Random Monero Address (all-sides) for each user~~
    - [x] Remove the empty rooms
    - [x] Remove the blocked users in the room
    - [x] A dockerfile (with alpine)
    - [x] New filter: `copiable` → if document, video, photo, audio or and animation
    - [ ] Delete all user messages with a command
    - [x] Delete the user from the database when blocked

* **Rooms**
    - [ ] List the global public rooms 
    - [x] Be able to create private rooms
    - [ ] Add room flood control ("take a breath")
    - [ ] Enable the room.settings or room.rules
    - [ ] Add room inactivity control

* ~~**Notifications** (removed)~~
    - [ ] ~~Notify the user if the message.edit fail~~
    - [ ] ~~Notify the user if the message.delete fail~~
    - [ ] ~~If a user blocks the bot, notify the remaining peers/users~~
    - [ ] ~~If a user leave the room, notify the remaining peers/users~~
