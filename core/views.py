from django.http import HttpResponse
from django.template import RequestContext, loader
from django.shortcuts import get_object_or_404
from core.models import Parlamentar, Partido

def parlamentares(request):
  template = loader.get_template('parlamentares/index.phtml')
  context = RequestContext(request, {
  })
  return HttpResponse(template.render(context))

def deputados(request):
  parlamentares = Parlamentar.deputados()
  homens = parlamentares.filter(sexo='M').count()
  mulheres = parlamentares.filter(sexo='F').count()
  template = loader.get_template('parlamentares/deputados/index.phtml')
  context = RequestContext(request, {
     'parlamentares': parlamentares,
     'homens':homens,
     'mulheres':mulheres,
  })
  return HttpResponse(template.render(context))

def deputado(request, id):
  deputado = get_object_or_404(Parlamentar, id_parlamentar=id)
  template = loader.get_template('parlamentares/deputados/details.phtml')
  context = RequestContext(request, {
     'deputado': deputado,
  })
  return HttpResponse(template.render(context))

def senador(request, id):
  senador = get_object_or_404(Parlamentar, id_parlamentar=id)
  template = loader.get_template('parlamentares/senadores/details.phtml')
  context = RequestContext(request, {
     'senador': senador,
  })
  return HttpResponse(template.render(context))


def senadores(request):
  parlamentares = Parlamentar.senadores()
  homens = parlamentares.filter(sexo='M').count()
  mulheres = parlamentares.filter(sexo='F').count()
  template = loader.get_template('parlamentares/senadores/index.phtml')
  context = RequestContext(request, {
     'parlamentares': parlamentares,
     'homens':homens,
     'mulheres':mulheres,
  })
  return HttpResponse(template.render(context))


def partidos(request):
  partidos = Partido.objects.filter(data_extincao__isnull=True)
  partidos = partidos.order_by('sigla')
  template = loader.get_template('partidos/index.phtml')
  context = RequestContext(request, {
     'partidos': partidos,
  })
  return HttpResponse(template.render(context))
