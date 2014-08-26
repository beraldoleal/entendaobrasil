LEIAME
======

O projeto 'entendaobrasil' pretende ser uma plataforma aberta e colaborativa
para importação e exibição dos dados públicos do Brasil.

Inicialmente com foque nas casas parlamentares (Câmara dos Deputados e Senado
federal) utilizando as APIs das respectivas casas. O portal pretende possuir
textos e vídeos explicativos sobre a política no Brasil.

Este sistema também se utiliza de Mashup_(web_application hybrid), para obter
dados da Wikipedia e fotos do Google Images.

O arquivo de configuração padrão irá iniciar o banco de dados em
`/tmp/db.sqlite3`. Por favor, mude o arquivo `entendaobrasil/settings.py` para
alterar as configuração de banco de dados.

Instalação
----------

Esta instalação é aconselhável para ambientes de produção (MySQL + Apache).
Para configurar um ambiente de desenvolvimento, por favor, veja o arquivo
`HACKING.md`.

    $ sudo mkdir /var/www/entendaobrasil
    $ sudo git clone git@github.com:beraldoleal/entendaobrasil.git /var/www/entendaobrasil/
    $ sudo chown -R www-data. /var/www/entendaobrasil/
    $ sudo pip install requirements.txt

Configuração
------------

O arquivo settings padrão utiliza sqlite armazenado no diretório `/tmp/`. Para
utilizar MySQL e configurar opções de produção, copie o arquivo settings:

    $ cd /var/www/entendaobrasil/entendaobrasil/
    $ cp settings.py production.py

Configure o `production.py` de acordo com suas necessidades.

Para configurar o apache, você precisa ter o apache instalado com suporte ao
módulo wsgi.

   $ cd /etc/apache2/sites-available/
   $ sudo cp /var/www/entendaobrasil/entendaobrasil/apache.conf entendaobrasil.org.conf
   # a2ensite entendaobrasil.org
   # service apache2 reload

Copie os arquivos estáticos:

   $ python manage.py collectstatic


Importação Inicial
------------------

    $ export PYTHONPATH=dir:$PYTHONPATH
    $ export DJANGO_SETTINGS_MODULE=entendaobrasil.production
    $ python manage.py syncdb
    $ python scripts/import.py
    $ python utils/deputados_fotos.py

Para mais detalhes veja o arquivo `IMPORTACAO.md`.

Executando
----------

    $ python manage.py runserver

