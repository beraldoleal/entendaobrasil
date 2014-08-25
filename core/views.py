from django.db.models import Count
from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404
from core.models import *

def camara(request):
  deputados = Parlamentar.deputados()
  partidos = Partido.objects.annotate(num_items=Count('parlamentar__partido')).order_by('-num_items')
  tipos_orgaos = TipoOrgao.objects.all()
  proposicoes = Proposicao.objects.all().order_by('-data_apresentacao')
  homens = deputados.filter(sexo='M').count()
  mulheres = deputados.filter(sexo='F').count()
  template = loader.get_template('camara/index.phtml')
  context = RequestContext(request, {
     'deputados': deputados,
     'tipos_orgaos': tipos_orgaos,
     'partidos': partidos,
     'proposicoes': proposicoes,
     'homens':homens,
     'mulheres':mulheres,
  })
  return HttpResponse(template.render(context))

def deputado(request, id):
  deputado = get_object_or_404(Parlamentar, ide_cadastro=id)
  exercicios = deputado.exercicios()
  template = loader.get_template('camara/deputados/details.phtml')
  context = RequestContext(request, {
     'deputado': deputado,
     'exercicios': exercicios,
  })
  return HttpResponse(template.render(context))

def orgao(request, sigla):
  orgao = get_object_or_404(Orgao, sigla=sigla)
  template = loader.get_template('camara/orgaos/details.phtml')
  context = RequestContext(request, {
     'orgao': orgao,
  })
  return HttpResponse(template.render(context))


def proposicao(request, id):
  proposicao = get_object_or_404(Proposicao, id=id)  
  template = loader.get_template('camara/proposicoes/details.phtml')
  context = RequestContext(request, {
     'proposicao': proposicao,
  })
  return HttpResponse(template.render(context))
