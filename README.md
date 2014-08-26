LEIAME
======

O projeto 'entendaobrasil' pretende ser uma plataforma aberta e colaborativa
para importação e exibição dos dados públicos do Brasil.

Inicialmente com foque nas casas parlamentares (Câmara dos Deputados e Senado
federal) utilizando as APIs das respectivas casas. O portal pretende possuir
textos e vídeos explicativos sobre a política no Brasil.

O arquivo de configuração padrão irá iniciar o banco de dados em
`/tmp/db.sqlite3`. Por favor, mude o arquivo `entendaobrasil/settings.py` para
alterar as configuração de banco de dados.


Instalação
----------

    $ mkdir /usr/src/entendaobrasil/
    $ cd /usr/src/entendaobrasil/
    $ git clone git@github.com:beraldoleal/entendaobrasil.git .
    $ pip install requirements.txt

Importação Inicial
------------------

    $ export PYTHONPATH=dir:$PYTHONPATH
    $ export DJANGO_SETTINGS_MODULE=entendaobrasil.settings
    $ python manage.py syncdb
    $ python scripts/import.py
    $ python utils/deputados_fotos.py

Para mais detalhes veja o arquivo `IMPORTACAO.md`.

Executando
----------

    $ python manage.py runserver
