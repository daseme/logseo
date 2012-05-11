from __future__ import division
from django.views.generic import simple
from django.shortcuts import render_to_response
from logseoapp.models import LogSeRank, Engine, Kw, Page
from django.http import HttpResponse
from django.db.models import Q, Avg, Count, StdDev
from django.db import connection



def get_ranks(request):
    """ View all objects """
    kw_list = []
    #phrases = Kws.objects.filter(Q(phrase__startswith = 'nsac',tags__name__in=["branded"])).values()
    #phrases = Kw.objects.get(phrase = 'nsac')
    phrase_cnt = Kw.objects.kw_count('nsac')

    #ip_count = LogSeRank.objects.ip_count(3518)
    #pc = LogSeRank.objects.filter(engine_id__engine__contains='Google').select_related()  # -> WORKS
    ip_count = LogSeRank.objects.values('phrase_id','phrase_id__phrase','phrase_id__tags__name').filter( position__gt = 0,
            engine_id__engine__contains = 'Google').annotate(num_ips=Count('ip', distinct = True),
                num_rank=Count('position'), avg_rank=Avg('position'), st_rank = StdDev('position'))[:4000] # FUCKING WORKS

    for dict in ip_count:
        num_ratio = dict['num_rank'] / dict['num_ips']
        dict['ratio'] = round(num_ratio, 2)

    phrase_ip = LogSeRank.objects.annotate(num_ips=Count('ip')) \
                  .aggregate(Avg('num_ips'))

    dates       = LogSeRank.objects.values('refdate').distinct()
    sql = connection.queries


    return render_to_response('template.py', { 'sql':sql,
        'count':phrase_cnt, 'xphrase':kw_list,
        'phrase_ip':phrase_ip, 'ip_cnts':ip_count, 'dates':dates})

def get_phrase(request, phrase):
    """ View all objects """
    phrase_name = Kw.objects.values('id','phrase').filter(pk = phrase)
    rankings    = LogSeRank.objects.values('position', 'refdate').filter(phrase_id = phrase, position__gt = 0).order_by('refdate')
    pages       = LogSeRank.objects.values('page_id__page',
            'position', 'refdate').filter(phrase_id = phrase, position__gt = 0).distinct().order_by('page_id__page','refdate') #getting 0 positions now

    sql = connection.queries


    return render_to_response('phrase.py', { 'phrase_name':phrase_name, 'rankings':rankings, 'pages':pages})

def show_object(request):
    """ View all objects """
    kwlist = []
    phrases = Kw.objects.values('phrase').filter(Q(phrase__startswith = 'nsac')).values()
    for phrase in phrases:
        kwlist.append(phrase["phrase"])

    #return render_to_response('template.py', {'thing':kwlist})

def show_ranks(request):
    """ View all objects """
    return simple.direct_to_template(request,
        template="templates/ranks.py",
        extra_context={
            'objects':LogSeRank.objects.filter(tags__name__in=["branded"]).order_by('phrase'),
        })
