from django.db import models

# Create your models here.

class Partido(models.Model):
  sigla = models.CharField(unique=True, max_length=16, blank=False, null=False)
  nome = models.CharField(max_length=128)
  data_criacao = models.DateField(blank=True, null=True)
  data_extincao = models.DateField(blank=True, null=True)


class Parlamentar(models.Model):

  TIPOS = (
    ('D', 'Deputado'),
    ('S', 'Senador'),
  )

  CONDICOES = (
    ('T', 'Titular'),
    ('S', 'Suplente'),
  )

  SEXOS = (
    ('M', 'Masculino'),
    ('F', 'Feminino'),
  )

  id_parlamentar = models.IntegerField(unique=True, null=False, blank=False)

  ide_cadastro = models.IntegerField(blank=True, null=True)
  matricula = models.IntegerField(blank=True, null=True)

  condicao = models.CharField(max_length=64, choices=CONDICOES, default='T')
  nome = models.CharField(max_length=64)
  nome_parlamentar = models.CharField(max_length=64)
  sumario = models.CharField(max_length=4096, blank=True, null=True)
  url_foto = models.URLField(max_length=512, blank=True, null=True)
  sexo = models.CharField(max_length=1, choices=SEXOS, blank=True, null=True)
  uf = models.CharField(max_length=2)
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


  @classmethod
  def senadores(self):
    return Parlamentar.objects.filter(tipo='S').order_by('nome')

  @classmethod
  def deputados(self):
    return Parlamentar.objects.filter(tipo='D').order_by('nome')


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
