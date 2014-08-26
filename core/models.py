from django.db import models
from datetime import datetime
import os

settings = os.environ['DJANGO_SETTINGS_MODULE']

# TODO: Replace this to a more pythonic way.
if settings is "entendaobrasil.production":
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

    def foto_principal(self):
        return self.fotos_perfil()[0]

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
