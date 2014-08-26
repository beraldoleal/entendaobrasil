from django.db import models
from datetime import datetime
from googleapi import search
import os
import time
import urllib
import logging
import wikipedia
import requests

# TODO: Replace this to a more pythonic way.
if os.environ['DJANGO_SETTINGS_MODULE'] == "entendaobrasil.production":
    from entendaobrasil import production as settings
else:
    from entendaobrasil import settings


# Create your models here.

class Base(models.Model):
    class Meta:
        abstract = True

    atualizado = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now=True)
    atualizado_em = models.DateTimeField(auto_now=True)


class TipoOrgao(Base):
    id = models.IntegerField(primary_key=True)
    descricao = models.CharField(max_length=128)

    def __unicode__(self):
        return u"%d %s" % (self.id, self.descricao)


class Orgao(Base):
    id = models.IntegerField(primary_key=True)
    sigla = models.CharField(max_length=128)
    descricao = models.CharField(max_length=2048)
    tipo = models.ForeignKey(TipoOrgao)

    def __unicode__(self):
        return u"%d %s" % (self.id, self.sigla)

    def membros(self):
        return self.cargoorgao_set.filter(data_saida__isnull=True).order_by('cargo')


class Cargo(Base):
    id = models.IntegerField(primary_key=True)
    descricao = models.CharField(max_length=128)

    def __unicode__(self):
        return u"%d %s" % (self.id, self.descricao)


class Partido(Base):
    sigla = models.CharField(unique=True, max_length=16, blank=False, null=False)
    nome = models.CharField(max_length=128)
    data_criacao = models.DateField(blank=True, null=True)
    data_extincao = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return u"%d %s" % (self.id, self.sigla)

    def deputados(self):
        return self.parlamentar_set.filter(tipo='D').order_by('nome')

    def senadores(self):
        return self.parlamentar_set.filter(tipo='S').order_by('nome')


class Parlamentar(Base):
    TIPOS = (
        ('D', 'Deputado'),
        ('S', 'Senador'),
    )

    SEXOS = (
        ('M', 'Masculino'),
        ('F', 'Feminino'),
    )

    ide_cadastro = models.IntegerField(unique=True, blank=True, null=True)
    nome = models.CharField(max_length=64)
    nome_parlamentar = models.CharField(max_length=64)
    sumario = models.CharField(max_length=4096, blank=True, null=True)
    sexo = models.CharField(max_length=1, choices=SEXOS, blank=True, null=True)
    uf = models.CharField(max_length=2)
    profissao = models.CharField(max_length=1024)
    partido = models.ForeignKey(Partido)
    gabinete = models.IntegerField(blank=True, null=True)
    endereco = models.CharField(max_length=512, blank=True, null=True)
    telefone = models.CharField(max_length=64, blank=True, null=True)
    fax = models.CharField(max_length=64, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    site = models.URLField(max_length=512, blank=True, null=True)
    wikipedia = models.URLField(max_length=512, blank=True, null=True)
    data_nascimento = models.DateField(blank=True, null=True)
    tipo = models.CharField(max_length=1, choices=TIPOS)

    def __unicode__(self):
        return u"%d %s" % (self.ide_cadastro, self.nome_parlamentar)

    @classmethod
    def senadores(self):
        return Parlamentar.objects.filter(tipo='S').order_by('nome')

    @classmethod
    def deputados(self):
        return Parlamentar.objects.filter(tipo='D').order_by('nome')

    def get_wikipedia_data(self):
        logging.basicConfig(level=settings.CAMARA_API_LOG_LEVEL)
        logger = logging.getLogger('entendaobrasil.wikipedia')
        query = "%s %s" % (self.tratamento(), self.nome_parlamentar)
        logger.info("Searching wikipedia for %s..." % query)
        try:
            wikipedia.set_lang("pt")
            w = wikipedia.page(query)
            self.wikipedia = w.url
            self.sumario = w.summary[:4090]
            self.save()
        except wikipedia.exceptions.PageError:
            logger.error("%s not found on wikipedia" % query)
            pass
        except wikipedia.exceptions.DisambiguationError:
            logger.error("%s is ambiguous" % query)
            pass
        except requests.exceptions.ConnectionError:
            logger.error("Failed to connect to wikiepedia")
            pass


    def download_photos(self):
        logging.basicConfig(level=settings.CAMARA_API_LOG_LEVEL)
        logger = logging.getLogger('entendaobrasil.download_photo')

        query = "%s %s" % (self.tratamento(), self.nome_parlamentar)
        logger.info("Searching for %s" % query)
        dest_dir = "%s/%s" % (settings.PHOTOS_DIR, self.ide_cadastro)
        if not os.path.exists(dest_dir):
            os.mkdir(dest_dir)

        if len(self.fotos_perfil()) == 5:
            logger.info("Already downloaded, skipping %s" % query)
            return

        try:
            results = search.images(query.encode("UTF-8"), 5)
        except TypeError:
            logger.error("Skipping %s, type error" % query)
            return

        i=1
        for result in results:
            f = "%s/%d.jpg" % (dest_dir, i)
            logger.info("Photo %s..." % f)
            try:
                if not os.path.isfile(f):
                    opener = urllib.urlopen(result['image_url'])
                    if opener.headers.maintype == 'image':
                        open(f, 'wb').write(opener.read())
            except UnicodeEncodeError:
                logger.error("Skipping %s, url with wrong enconde" % query)
            except IOError:
                logger.error("Skipping %s, timeout" % query)
                time.sleep(5)
            i=i+1

    def foto_principal(self):
        fotos = self.fotos_perfil()
        if fotos:
            return fotos[0]
        else:
            return None

    def flag_uf(self):
        return "%sflags/uf/%s.png" % (settings.STATIC_URL, self.uf)

    def fotos_perfil(self):
        path = "%s/photos/deputados/%s/" % (settings.MEDIA_ROOT, self.ide_cadastro)
        try:
            photos = os.walk(path).next()[2]
            return map(lambda x: '%sphotos/deputados/%s/%s' % (settings.MEDIA_URL, self.ide_cadastro, x), photos)
        except StopIteration:
            return []

    def idade(self):
        now = datetime.utcnow()
        diff = now.date() - self.data_nascimento
        return diff.days / 365

    def exercicios(self):
        return self.exercicio_set.all().order_by('-data_inicio')

    def comissoes_atuais(self):
        now = datetime.now()
        return self.cargoorgao_set.filter(data_saida__isnull=True).order_by('-data_entrada')

    def comissoes_passadas(self):
        now = datetime.now()
        return self.cargoorgao_set.filter(data_saida__isnull=False).order_by('-data_entrada')

    def tratamento(self):
        if self.tipo == 'D':
            if self.sexo == 'M':
                return 'Deputado'
            else:
                return 'Deputada'
        else:
            if self.sexo == 'M':
                return 'Senador'
            else:
                return 'Senadora'


class CargoOrgao(Base):
    orgao = models.ForeignKey(Orgao)
    cargo = models.ForeignKey(Cargo, blank=True, null=True)
    parlamentar = models.ForeignKey(Parlamentar, blank=True, null=True)
    data_entrada = models.DateField(blank=True, null=True)
    data_saida = models.DateField(blank=True, null=True)

    def __unicode__(self):
        return u"%d %s %s %s" % (self.id, self.orgao, self.cargo, self.parlamentar)



class Exercicio(models.Model):
    situacao = models.CharField(max_length=64)
    data_inicio = models.DateField(blank=True, null=True)
    data_fim = models.DateField(blank=True, null=True)
    causa_fim = models.CharField(max_length=512)
    parlamentar = models.ForeignKey(Parlamentar)









class TipoProposicao(models.Model):
    def __str__(self):
        return self.descricao


    sigla = models.CharField(max_length=16, unique=True)
    descricao = models.CharField(max_length=128)
    ativa = models.BooleanField(default=False)
    genero = models.CharField(max_length=1)

class SituacaoProposicao(models.Model):
    def __str__(self):
        return self.descricao


    id = models.IntegerField(primary_key=True)
    descricao = models.CharField(max_length=128)
    ativa = models.BooleanField(default=False)


class Proposicao(models.Model):
    id = models.IntegerField(primary_key=True)
    nome = models.CharField(max_length=128)
    tipo = models.ForeignKey(TipoProposicao)
    numero = models.IntegerField()
    ano = models.IntegerField()
    data_apresentacao = models.DateTimeField(blank=True, null=True)
    ementa = models.CharField(max_length=2048)
    explicacao = models.CharField(max_length=2048)
    autor = models.ForeignKey(Parlamentar)
    quantidade_autores = models.IntegerField()
    situacao = models.ForeignKey(SituacaoProposicao)
    genero = models.CharField(max_length=1)
