from __future__ import division
from django.shortcuts import render
from logseoapp.models import LogSeRank, Kw, Page
from django.db.models import Avg, Count, StdDev
from django.db import connection
from collections import defaultdict
from datetime import datetime,timedelta
import time
import qsstats


def date_select(get_request):
    """ defaults to last month in our db, or uses date select forms """

    if 'start_date' and 'end_date' in get_request:
        start_date = get_request['start_date']
        end_date   = get_request['end_date']
        return start_date,end_date
    else:
        end_date = LogSeRank.objects.values('refdate').order_by('-refdate')[0]
        end_date = end_date['refdate'] # possible we don't have a full month here
        start_date = end_date[:8]+'01' # replace day part of end_date with 01
        return start_date,end_date


def process_time_series(query, start_date, end_date):
    """ process qsstats object into json """

    qss = qsstats.QuerySetStats(query, 'refdate')
    start = datetime.strptime(start_date, '%Y-%m-%d').date()
    end   = datetime.strptime(end_date, '%Y-%m-%d').date()
    time_series = qss.time_series(start, end, 'weeks') # aggregate by weeks (default is days)
    # do some formatting cleanup of qsstats ->convert to epoch time (not dealing with local time!!)
    return [ {"x":time.mktime(e[0].timetuple()), "y":e[1]} for e in time_series ]

def home(request):
    """ retrieve stats for home page """

    #new phrase stuff
    #naive return of 5 latest kws added to db
    phrases_new   = Kw.objects.values('id','phrase','first_seen').order_by('-first_seen')[:5]
    # get the most recent sunday, so we can count back to the first full week in our dataset
    latest_date   = Kw.objects.values('first_seen').filter(first_seen__week_day=1).order_by('-first_seen')[:2]
    now_date      = latest_date[1]['first_seen']
    # this gets our first monday for which we have a full week
    week_ago      = now_date - timedelta(days=6)
    four_wks_ago  = now_date - timedelta(days=28)
    p_count       = Kw.objects.filter(first_seen__range=[week_ago,now_date]).count()
    # time series stuff for the bar chart
    phrase_new_ts = Kw.objects.values('first_seen','phrase')
    qss           = qsstats.QuerySetStats(phrase_new_ts, 'first_seen')
    new_kws_cnt   = qss.time_series(four_wks_ago, now_date,'weeks') # aggregate by weeks (default is days)
    # do some formatting cleanup of qsstats ->convert to epoch time (not dealing with local time!!)
    new_kws_cnt = [ {"x":time.mktime(e[0].timetuple()), "y":e[1]} for e in new_kws_cnt ]


    #missing Kws stuff
    # get last 7 days of dates, get the 7 days of dates bf that, get kws in each set, compare sets
    #last_week_end = LogSeRank.objects.values('refdate').order_by('-refdate')[0]
    #delta = datetime.timedelta(days=7)
    #new_date = last_week_end - delta

    last_week  = LogSeRank.objects.values('refdate','phrase_id','phrase_id__phrase').order_by('-refdate').distinct()[:7]
    wk_bf_last = LogSeRank.objects.values('refdate','phrase_id','phrase_id__phrase').order_by('-refdate').distinct()[7:14]
    # keep all in wk_bf_last if not in last_week
    unique = [{'phrase':x['phrase_id__phrase'],'phrase_id':x['phrase_id']} for x in wk_bf_last if x not in last_week]
    #missing_kws = Kw.objects.values('id','phrase','first_seen').order_by('-last_seen')[:5]
    #kws we haven't seen in one week that we saw in the week prior



    #debug lines
    sql       = connection.queries


    return render(request,'index.html', { 'sql':sql, 'phrases_new':phrases_new, 'unique':unique,'last_week':last_week,
                                          'wk_bf_last':wk_bf_last,'week_ago':week_ago,'latest_date':now_date,
                                          'p_count':p_count,'new_kws_cnt':new_kws_cnt })


def get_ranks(request=None, start_date="", end_date=""):
    """ get rank data for kws, default dates set in date_select() fx """

    start_date,end_date = date_select(request.GET)

    """
    datatable data
    """
    dates    = LogSeRank.objects.values('refdate').distinct()

    ip_count = LogSeRank.objects.values(  'phrase_id','phrase_id__phrase','phrase_id__tags__name'). \
                                 filter(   position__gt = 0,
                                           engine_id__engine__contains = 'Google',
                                           refdate__range=(start_date, end_date)). \
                                 annotate( num_ips=Count('ip', distinct = True),
                                           num_rank=Count('position'),
                                           avg_rank=Avg('position'),
                                           st_rank = StdDev('position'))[:4000] # FUCKING WORKS

    for dict in ip_count:
        num_ratio = dict['num_rank'] / dict['num_ips']
        dict['ratio'] = round(num_ratio, 2)

    phrase_ip = LogSeRank.objects.annotate(num_ips=Count('ip')).aggregate(Avg('num_ips'))

    """
    chart / time series data
    """
    all_phrase  = LogSeRank.objects.values('id','phrase_id','refdate').distinct()

    rank_phrase = LogSeRank.objects.values('id','phrase_id','refdate'). \
                                    filter(   position__gt = 0).distinct()
    all_engine  = LogSeRank.objects.values('id','engine_id','refdate').distinct()

    all_phrase  = process_time_series(all_phrase,start_date,end_date)
    rank_phrase = process_time_series(rank_phrase,start_date,end_date)
    all_engine  = process_time_series(all_engine,start_date,end_date)

    #debug lines
    sql       = connection.queries

    return render(request,'ranks.html', { 'sql':sql,'phrase_ip':phrase_ip,
                                               'start_date':start_date,'end_date':end_date,
                                               'ip_cnts':ip_count, 'dates':dates,
                                               'rank_phrase':rank_phrase,'all_phrase':all_phrase,'all_engine':all_engine})

def get_phrase(request, phrase):
    """ View all objects """
    phrase_name = Kw.objects.values('id','phrase').filter(pk = phrase)
    rankings    = LogSeRank.objects.values('position', 'refdate'). \
                                    filter(phrase_id = phrase, position__gt = 0). \
                                    order_by('refdate')
    pages       = LogSeRank.objects.values(  'page_id__page', 'position', 'refdate'). \
                                    filter(   phrase_id = phrase, position__gt = 0). \
                                    distinct(). \
                                    order_by('page_id__page','refdate')

    #debug lines
    #sql = connection.queries


    return render(request,'phrase.html', { 'phrase_name':phrase_name, 'rankings':rankings, 'pages':pages})



def get_landing_pages(request, start_date="", end_date=""):
    """ get landing pages data """

    start_date,end_date = date_select(request.GET)

    dates         = LogSeRank.objects.values('refdate').distinct()

    landing_pages = LogSeRank.objects.values('page_id', 'page_id__page'). \
                                      filter(refdate__range=(start_date, end_date)). \
                                      distinct()

    gcount        = landing_pages.filter(engine_id__engine__contains = 'Google'). \
                                      annotate(num_google=Count('engine_id'))

    bing_cnt      = landing_pages.filter(engine_id__engine__contains = 'Bing'). \
                                      annotate(num_bing=Count('engine_id'))

    yahoo_cnt     = landing_pages.filter(engine_id__engine__contains = 'Yahoo'). \
                                      annotate(num_yahoo=Count('engine_id'))

    phrase_cnt    = landing_pages.annotate(num_phrase=Count('phrase_id', distinct = True))

    ip_cnt        = landing_pages.annotate(num_ip=Count('ip', distinct = True))


    # http://stackoverflow.com/questions/5501810/join-two-lists-of-dictionaries-on-a-single-key
    d = defaultdict(dict)
    for item in (landing_pages, gcount, bing_cnt, yahoo_cnt, phrase_cnt, ip_cnt):
        for elem in item:
            d[elem['page_id']].update(elem)
    combo = d.values()

    for d in combo:
        num_ratio = d['num_ip'] / d['num_phrase']
        d['ip_per_q'] = round(num_ratio, 2)

    """
    chart / time series data
    """

    t_series = process_time_series(landing_pages,start_date,end_date)

    #debug lines
    sql = connection.queries

    return render(request,'landing_pages.html', { 'sql':sql,'start_date':start_date,'end_date':end_date,
                                                    'dates':dates, 'combo':combo,'t_series':t_series})

def get_page(request, page):
    page_name = Page.objects.values('id','page').filter(pk = page)

    rankings  = LogSeRank.objects.values('position', 'refdate'). \
                                    filter(page_id = page, position__gt = 0). \
                                    order_by('refdate')

    kws       = LogSeRank.objects.values('phrase_id','phrase_id__phrase'). \
                                    filter(   page_id = page). \
                                    distinct(). \
                                    order_by('phrase_id__phrase')

    ip_cnt    = kws.annotate(num_ip=Count('ip', distinct = True))

    gcount    = kws.filter(engine_id__engine__contains = 'Google'). \
                                      annotate(num_google=Count('engine_id'))

    bing_cnt  = kws.filter(engine_id__engine__contains = 'Bing'). \
                                      annotate(num_bing=Count('engine_id'))

    yahoo_cnt = kws.filter(engine_id__engine__contains = 'Yahoo'). \
                                      annotate(num_yahoo=Count('engine_id'))

    d = defaultdict(dict)
    for item in (kws,ip_cnt,gcount,bing_cnt,yahoo_cnt):
        for elem in item:
            d[elem['phrase_id']].update(elem)
    combo = d.values()

    #time_series = process_time_series(ip_cnt,start_date,end_date)
    #debug lines
    sql = connection.queries


    return render(request, 'page.html', { 'sql':sql,'page_name':page_name,'kws':combo,
        'rankings':rankings})

