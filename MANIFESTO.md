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