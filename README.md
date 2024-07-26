# Anodos • Incognito

> Preciso construir um porto-seguro, a safe-point.

Se você quiser colaborar com o projeto, seja bem-vindo para rodar sua própria instância, sugerir mudanças ou então apoiar o projeto com doações via Monero/XMR no endereço de carteira: <MONERO_ADDRESS>


### Initial guide

1. Configure o arquivo `secrets.example.toml`, para o `dynaconf.settings`
2. Inicialize o banco de dados — podemos usar um docker para isso, futuramente
3. Rode `python -m src` e aguarde

> Depois possivelmente o `requirements.txt` pode ser movido para dentro do `pyproject.toml`.


### Status

* **Basic**
    - [ ] Mailing
    - [ ] Mailing with an invite
    - [ ] Scan all non-registered messages and register them in order
    ~~- [ ] Federations (connect to other instancies)~~
    ~~- [ ] Use a personal group with topics and join in multiple rooms~~ 
    - [ ] Enable the tag/name option
    - [ ] Enable the forward-with-sign option
    - [ ] Adicionar uma confirmação se topa entrar na sala
    - [ ] Change the current room size
    - [x] Mimic (replicate) message.edit
    - [x] Mimic (replicate) message.delete
    - [ ] Inline mailing
    - [ ] Inline mailing with an invite to your current room
    ~~- [ ] A Random Monero Address (all-sides) for each user~~
* **Specific features**
    - [ ] A dockerfile (with alpine)
    - [ ] New filter: `copiable` → if document, video, photo, audio or and animation
* **Profiles**
    - [ ] Delete all user messages with a command
    - [x] Delete the user from the database when blocked
* **Rooms**
    - [ ] List the global public rooms 
    - [x] Be able to create private rooms
    - [ ] Add room flood control ("take a breath")
    - [ ] Enable the room.settings or room.rules
    - [ ] Add room inactivity control
* **Notifications**
    - [x] If a user blocks the bot, notify the remaining peers/users 
    - [x] If a user leave the room, notify the remaining peers/users
* **Sanitization**
    - [x] Remove the empty rooms
    - [ ] Remove the blocked users in the room
* **Failure**
    - [ ] Notify the user if the message.edit fail
    - [ ] Notify the user if the message.delete fail

### Disclaimer • Aviso & Manifesto

Se o Telegram realmente fosse a favor da privacidade, ele melhoraria o **Secret Chat** que supostamente é criptografado de ponta-a-ponta. Estranho esse descaso e aparente desinteresse por parte da plataforma, não é?

> Nosso trabalho aqui é tentar trazer uma rede mais protegida para àqueles que a usam, sem discriminação ou violação/abuso.

Mantemos as conversas de um jeito incógnito, tentando ao máximo unir privacidade com anonimato. Mas devemos questionar uma coisa: o Telegram realmente não lê as mensagens mandadas para o bot?! Saiba que: se um bot for banido mesmo com o encaminhamento de mensagem sendo restrito/desabilitado, o Telegram precisou de alguma forma acessar uma mensagem (ou também uma mídia) em um ambiente privado!

### Próximos grandes passos

Nós temos a idea de expandir mais, algo como uma plataforma pronta. E isso irá requerer investimento. Todavia, você também pode usar outras redes, sendo algumas das nossas recomendações:

- Simplex
- Session
- Matrix/Element

Até pensamos em uma idea de federações, até pra dificultar a censura, mas seria preciso um resolvedor e conector para ligar uma instância a outra. Mas você pode fazer algo assim, talvez localmente ou criando seu próprio diretório.

### Manuseio e controle

- As salas (rooms) devem por padrão terem todas as restrições padrões ativas.
- A não-restrição deve ocorrer por parte do usuário e deve ser OPCIONAL. Exemplo: ao optar por habilitar ou não o encaminhamento de suas mensagens, assim ao como optar ou não por ter uma etiqueta de apelido em suas mensagens...

### Recommended settings

Não é preciso muito para rodar sua própria instância. No entanto, até por não usarmos cache no Telegram (algo como copiar as mensagens e usar elas prontas ao invés de sempre montar todas), é bom que tenha uma rápida internet para o envio de mídias (os assets), talvez 100MBs.

### Final comments and considerations

> **Anúncios**
> Nem de flores vive o mundo.
> Se você roda sua instância, um gasto irá ter. Então consideremos a opção de rodar anúncios para usuários não-apoiadores dela, ok? É justo, ao meu ver, afinal, é uma forma de sustentabilizar a rede.
> Exemplo: `if not user.premium and len(user.messages_count) % 100...`

> **Tradução**
> Para internacionalização podemos usar criar algo como um `Capptioner`: por exemplo, messages.en.message & messages.pt.message, or something like this. Se por acaso não existir algo assim — deve existir.

> **Monetário**
> De acordo com os termos de responsabilidade, não é culpa do software/código o que nele é compartilhado, isto é, a moderação é APENAS por parte dos usuários! Ok? Se há dúvida, confira por conta própria e veja que não há alguma forma criada para supervisionar o que é dito.
> Mas não sabemos as formas de censura que podem tentar impor, portanto, como proteção, tente optar por Monero.
> XMR, ou Monero, tem uma intíma ligação com o anonimato e por anos continua sendo resistente à censura.

> **Proteção**
> Talvez a solução para não usar Redis e usar apenas Mongo localmente (com cópia remota reserva) seja por uma senha para acessar o banco e de alguma forma — talvez com um espaço a mais no Bash — passar ela de forma oculta/temporária.

## Contact
Any bugs or something to report, send a e-mail to `anonstry@protonmail.com`