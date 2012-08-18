from __future__ import division
from utils.view import *
from django.shortcuts import render
from logseoapp.models import LogSeRank, Kw, Page, Client
from logseoapp.forms import ClientChoice
from django.db.models import Avg, Count, StdDev
from django.db import connection
from collections import defaultdict
from operator import itemgetter

def home(request, client_id=""):
    """ retrieve stats for home page,
    restricted to last full week (mon-sun) in our data-set """

    form = ClientChoice()

    # client from form
    client_id = client_select(request.GET)

    # client name
    client = Client.objects.values('name').filter(pk=client_id)

    # latest week in our db
    latest_sunday,week_ago = last_full_week(client_id)
    two_wks_ago    = latest_sunday - timedelta(days=13)

    # row 1 metrics
    metrics_row1 = [{'field':'ip','metric_name':'Organic Visitors'},
                    {'field':'engine_id','metric_name':'Search Engines'},
                    {'field':'page_id','metric_name':'Pages Visited'},
                    {'field':'phrase_id','metric_name':'Search Queries'}]
    metrics_row1_dict = metrics_processing_row1(metrics_row1,client_id)

    # row 2 metrics
    metrics_row2 = [{'engine':'','position':-1,'metric_name':'New Queries'}, # all engines
                    {'engine':'Google','position':-1,'metric_name':'New Google Queries'},
                    {'engine':'Google','position':0,'metric_name':'New Google Ranked Queries'},
                    {'engine':'Bing','position':-1,'metric_name':'New Bing Queries'}]
    metrics_row2_dict = metrics_processing_row2(metrics_row2,client_id)

    """
    missing kw data
    """
    last_week      = Kw.objects.values('id','phrase').filter(last_seen__range=[week_ago,latest_sunday],
                                                             client_id=client_id)
    last_week_cnt  = Kw.objects.filter(last_seen__range=[week_ago,latest_sunday],
                                       client_id=client_id).count()
    wk_bf_last     = Kw.objects.values('id','phrase').filter(last_seen__range=[two_wks_ago,week_ago],
                                                             client_id=client_id)
    wk_bf_last_cnt = Kw.objects.filter(last_seen__range=[two_wks_ago,week_ago],
                                       client_id=client_id).count()

    # keep all in wk_bf_last if not in last_week
    unique         = [{'phrase':x['phrase'],'phrase_id':x['id']} for x in wk_bf_last if x not in last_week]
    unique_cnt     = len(unique)

    """
    bigram data
    """
    bigram_this_wk = bigram_stats(LogSeRank.objects.values('phrase_id__phrase'). \
                                               filter(refdate__range=[week_ago,latest_sunday],
                                                      client_id=client_id). \
                                               annotate(num_ips=Count('ip', distinct = True)))

    bigram_last_wk = bigram_stats(LogSeRank.objects.values('phrase_id__phrase'). \
                                               filter(refdate__range=[two_wks_ago,week_ago],
                                                      client_id=client_id). \
                                               annotate(num_ips=Count('ip', distinct = True)))

    # subtract last weeks word cnt from this weeks word cnt to find diff
    bigram_diff    = { k:int(bigram_this_wk.get(k,0)) - int(bigram_last_wk.get(k,0))
                      for k in set(bigram_last_wk) | set(bigram_this_wk) }
    bigram_gainers = sorted(bigram_diff.items(), key=itemgetter(1), reverse=True)
    bigram_losers  = sorted(bigram_diff.items(), key=itemgetter(1), reverse=False)


    #debug lines
    sql             = connection.queries


    return render(request,'dashboard/index.html', {
                                          'sql':sql,
                                          'form':form,
                                          'metrics_row1_dict':metrics_row1_dict,
                                          'metrics_row2_dict':metrics_row2_dict,
                                          'client':client,
                                          'unique':unique,
                                          'last_week':last_week,
                                          'wk_bf_last':wk_bf_last,
                                          'week_ago':week_ago,
                                          'latest_date':latest_sunday,
                                          'last_week_cnt':last_week_cnt,
                                          'wk_bf_last_cnt':wk_bf_last_cnt,
                                          'unique_cnt':unique_cnt,
                                          'bigram_gainers':bigram_gainers,
                                          'bigram_losers':bigram_losers })


def get_ranks(request=None, start_date="", end_date=""):
    """ get rank data for kws, default dates set in date_select() fx """

    form = ClientChoice()

    start_date,end_date = date_select(request.GET)
    dates    = LogSeRank.objects.values('refdate').distinct()

    """
    datatable data
    """
    ip_count = LogSeRank.objects.values(  'phrase_id','phrase_id__phrase'). \
                                 filter(   position__gt = 0,
                                           engine_id__engine__contains = 'Google',
                                           refdate__range=(start_date, end_date)). \
                                 annotate( num_ips=Count('ip', distinct = True),
                                           num_rank=Count('position'),
                                           avg_rank=Avg('position'),
                                           st_rank = StdDev('position')). \
                                 order_by('phrase_id__phrase') # FUCKING WORKS


    for dict in ip_count:
        num_ratio = dict['num_rank'] / dict['num_ips']
        dict['ratio'] = round(num_ratio, 2)

    phrase_ip   = LogSeRank.objects.annotate(num_ips=Count('ip')).aggregate(Avg('num_ips'))

    """
    chart / time series data
    """
    all_phrase    = LogSeRank.objects.values('id','phrase_id','refdate').distinct()

    rank_phrase   = LogSeRank.objects.values('phrase_id','refdate').filter(position__gt = 0).distinct()

    ranks_ts  = LogSeRank.objects.values('position','refdate'). \
                                  filter(position__gt = 0, refdate__range=[start_date,end_date])

    avg_position = process_time_series(ranks_ts,start_date,end_date,'refdate',Avg('position'))

    # make ranks negative so lower ranks show higher on the chart
    avg_position = [ {"x":e['x'], "y":e['y']*-1} for e in avg_position ]
    all_phrase   = process_time_series(all_phrase,start_date,end_date)
    rank_phrase  = process_time_series(rank_phrase,start_date,end_date)



    #debug lines
    sql       = connection.queries

    return render(request,'ranks.html', { 'sql':sql,
                                          'form':form,
                                          'phrase_ip':phrase_ip,
                                          'start_date':start_date,
                                          'end_date':end_date,
                                          'ip_cnts':ip_count,
                                          'dates':dates,
                                          'rank_phrase':rank_phrase,
                                          'all_phrase':all_phrase,
                                          'avg_position':avg_position})

def get_phrase(request, phrase):
    """ get data on a particular kw query

    """

    start_date,end_date = date_select(request.GET)
    dates    = LogSeRank.objects.values('refdate').distinct()


    phrase_name = Kw.objects.values('id','phrase').filter(pk = phrase)

    ranking_ts    = LogSeRank.objects.values('position', 'refdate'). \
                                    filter(position__gt = 0,
                                           phrase_id = phrase,
                                           refdate__range=(start_date, end_date)). \
                                    order_by('refdate')
    rankings   = process_time_series(ranking_ts,start_date,end_date,'refdate',Avg('position'))

    pages       = LogSeRank.objects.values('page_id__page', 'position', 'refdate'). \
                                    filter(position__gt = 0,
                                           phrase_id = phrase,
                                           refdate__range=(start_date, end_date)). \
                                    distinct(). \
                                    order_by('page_id__page','refdate')

    #debug lines
    #sql = connection.queries


    return render(request,'phrase.html', { 'dates':dates,
                                           'start_date':start_date,
                                           'end_date':end_date,
                                           'phrase_name':phrase_name,
                                           'rankings':rankings,
                                           'pages':pages})



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

    return render(request,'landing_pages.html', { 'sql':sql,
                                                  'start_date':start_date,
                                                  'end_date':end_date,
                                                  'dates':dates,
                                                  'combo':combo,
                                                  't_series':t_series})

def get_page(request, page):
    """ get specific page data """

    start_date,end_date = date_select(request.GET)

    dates     = LogSeRank.objects.values('refdate').distinct()

    page_name = Page.objects.values('id','page').filter(pk = page)

    rankings  = LogSeRank.objects.values('position', 'refdate'). \
                                    filter(page_id = page, position__gt = 0,refdate__range=(start_date, end_date)). \
                                    order_by('refdate')

    kws       = LogSeRank.objects.values('phrase_id','phrase_id__phrase'). \
                                    filter(page_id = page, refdate__range=(start_date, end_date)). \
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


    return render(request, 'page.html', { 'sql':sql,
                                          'dates':dates,
                                          'start_date':start_date,
                                          'end_date':end_date,
                                          'page_name':page_name,
                                          'kws':combo,
                                          'rankings':rankings})

