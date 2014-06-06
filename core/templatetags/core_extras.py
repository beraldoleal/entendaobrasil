from django import template
from django.template.defaultfilters import floatformat
from django.template.defaultfilters import stringfilter
from django.utils.safestring import mark_safe
from django.utils.html import conditional_escape
import re



register = template.Library()

@register.filter
def as_percentage_of(part, whole):
    try:
        return "%.2f%%" % (float(part) / float(whole) * 100)
    except (ValueError, ZeroDivisionError):
        return ""

@register.filter
def condicao(value):
    if value == 'T':
        return 'Titular'
    else:
        return 'Suplente'

@register.filter
def condicao_class(value):
    if value == 'T':
        return 'success'
    else:
        return 'default'

@register.filter
@stringfilter
def mungify(email, text=None, autoescape=None):
    text = text or email
    
    if autoescape:
        email = conditional_escape(email)
        text = conditional_escape(text)

    emailArrayContent = ''
    textArrayContent = ''
    r = lambda c: '"' + str(ord(c)) + '",'

    for c in email: emailArrayContent += r(c)
    for c in text: textArrayContent += r(c)

    result = """<script>
                var _tyjsdf = [%s], _qplmks = [%s];
                document.write('<a
href="&#x6d;&#97;&#105;&#x6c;&#000116;&#111;&#x3a;');
                for(_i=0;_i<_tyjsdf.length;_i++){document.write('&#'+_tyjsdf[_i]+';');}
                document.write('">');
                for(_i=0;_i<_qplmks.length;_i++){document.write('&#'+_qplmks[_i]+';');}
                document.write('</a>');
                </script>""" % (re.sub(r',$', '', emailArrayContent),
                                re.sub(r',$', '', textArrayContent))
    
    return mark_safe(result)

mungify.needs_autoescape = True
