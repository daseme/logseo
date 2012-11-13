from __future__ import division
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from datetime import timedelta
# logseo utility functions
from utils.view import date_select, client_select, last_full_week
from utils.view import metrics_processing_row1, metrics_processing_row2
from utils.view import bigram_stats, process_time_series, get_datatables_records
from django.contrib.auth.models import User
from logseoapp.models import LogSeRank, Kw, Page, WatchListKw
from django.db.models import Avg, Count, StdDev, Min, Max
from logseoapp.forms import WatchListKwForm, KwNoteFormSet
from collections import defaultdict
from operator import itemgetter
import json
from django.db import connection


@login_required
def home(request, client_id=""):
    """ retrieve stats for home page,
    restricted to last full week (mon-sun) in our data-set """

    # client from form
    client_id = client_select(request.GET)

    # latest week in our db
    latest_sunday, week_ago = last_full_week(client_id)
    two_wks_ago = latest_sunday - timedelta(days=13)

    # row 1 metrics
    metrics_row1 = [{'field':'ip', 'metric_name':'Organic Visitors'},
                    {'field':'engine_id', 'metric_name':'Search Engines'},
                    {'field':'page_id', 'metric_name':'Pages Visited'},
                    {'field':'phrase_id', 'metric_name':'Search Queries'}]
    metrics_row1_dict = metrics_processing_row1(metrics_row1, client_id)

    # row 2 metrics
    metrics_row2 = [{'engine':'', 'position':-1, 'metric_name':'New Queries'},  # all engines
                    {'engine':'Google', 'position':-1, 'metric_name':'New Google Queries'},
                    {'engine':'Google', 'position':0, 'metric_name':'New Google Ranked Queries'},
                    {'engine':'Bing', 'position':-1, 'metric_name':'New Bing Queries'}]
    metrics_row2_dict = metrics_processing_row2(metrics_row2, client_id)

    """
    missing kw data
    """
    last_week      = Kw.objects.values('id', 'phrase') \
                               .filter(last_seen__range=[week_ago, latest_sunday],
                                       client_id=client_id)

    last_week_cnt  = Kw.objects.filter(last_seen__range=[week_ago, latest_sunday],
                                       client_id=client_id).count()

    wk_bf_last     = Kw.objects.values('id', 'phrase') \
                               .filter(last_seen__range=[two_wks_ago, week_ago],
                                       client_id=client_id)

    wk_bf_last_cnt = Kw.objects.filter(last_seen__range=[two_wks_ago, week_ago],
                                       client_id=client_id) \
                               .count()

    # keep all in wk_bf_last if not in last_week
    missing_queries = [{'phrase':x['phrase'], 'phrase_id':x['id']}
                       for x in wk_bf_last
                       if x not in last_week]

    missing_queries_cnt = len(missing_queries)

    missing_queries_txt = """There were %d kws 2 wks ago, and %d kws last week,
                           below are 5 of the %d kws that were missing from the prev wk""" \
                          % (wk_bf_last_cnt, last_week_cnt, missing_queries_cnt)

    """
    bigram data
    """
    bigram_this_wk = bigram_stats(LogSeRank.objects
                                           .values('phrase_id__phrase')
                                           .filter(refdate__range=[week_ago, latest_sunday],
                                                   client_id=client_id)
                                           .annotate(num_ips=Count('ip', distinct=True)))

    bigram_last_wk = bigram_stats(LogSeRank.objects
                                           .values('phrase_id__phrase')
                                           .filter(refdate__range=[two_wks_ago, week_ago],
                                                   client_id=client_id)
                                           .annotate(num_ips=Count('ip', distinct=True)))

    # subtract last weeks word cnt from this weeks word cnt to find diff
    bigram_diff    = {k: int(bigram_this_wk.get(k, 0)) - int(bigram_last_wk.get(k, 0))
                      for k in set(bigram_last_wk) | set(bigram_this_wk)}
    bigram_gainers = sorted(bigram_diff.items(), key=itemgetter(1), reverse=True)
    bigram_losers  = sorted(bigram_diff.items(), key=itemgetter(1), reverse=False)

    # landing pages
    pages_query = LogSeRank.objects \
                           .values('page_id', 'page_id__page') \
                           .annotate(num_ips=Count('ip', distinct=True)) \
                           .filter(client_id=client_id)\
                           .order_by('-num_ips').distinct()

    return render(request, 'dashboard/index.html', {'client_id': client_id,
                                                    'week_ago': week_ago,
                                                    'latest_date': latest_sunday,
                                                    'metrics_row1_dict': metrics_row1_dict,
                                                    'metrics_row2_dict': metrics_row2_dict,
                                                    'missing_queries_txt': missing_queries_txt,
                                                    'missing_queries': missing_queries,
                                                    'bigram_gainers': bigram_gainers,
                                                    'bigram_losers': bigram_losers,
                                                    'pages_query': pages_query})


def home_engine_detail(request, engine, client_id="", ranked=""):
    """ retrieve all search queries for a given search engine """

    # client from form
    client_id = client_select(request.GET)

    # latest week in our db
    latest_sunday, week_ago = last_full_week(client_id)

    # engine name from url

    if engine != 'all':
        metrics = [{'engine':engine, 'position':-1, 'metric_name':"New " + engine + " Queries"}]

    else:
        metrics = [{'engine':'', 'position':-1, 'metric_name':'New Queries'}]

    data = metrics_processing_row2(metrics, client_id)

    return render(request, 'dashboard/engine_detail.html', {'client_id': client_id,
                                                            'week_ago': week_ago,
                                                            'latest_date': latest_sunday,
                                                            'data': data})


def get_queries(request):
    """ get rank data for kws, default dates set in date_select() fx """

    # client from form
    client_id = client_select(request.GET)

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    """
    chart / time series data
    """
    all_phrase = LogSeRank.objects.filter(client_id=client_id)

    all_phrase = process_time_series(all_phrase,
                                     start_date,
                                     end_date,
                                     'refdate',
                                     Count('phrase_id', distinct=True))

    all_phrase_cnt = sum(item['y'] for item in all_phrase)

    all_phrase_avg = round(all_phrase_cnt / len(all_phrase))

    return render(request, 'queries.html', {'client_id': client_id,
                                            'start_date': start_date,
                                            'end_date': end_date,
                                            'first_data_date': first_data_date,
                                            'last_data_date': last_data_date,
                                            'all_phrase': all_phrase,
                                            'all_phrase_cnt': all_phrase_cnt,
                                            'all_phrase_avg': all_phrase_avg})


def get_queries_datatable(request):
    """ produces the datatable section of get_queries """

    # client from form
    client_id = client_select(request.GET)

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    #prepare the params

    #initial querySet
    querySet = LogSeRank.objects \
                        .values('phrase_id', 'phrase_id__phrase') \
                        .filter(refdate__range=(start_date, end_date),
                                client_id=client_id) \
                        .annotate(num_ips=Count('ip', distinct=True),
                                  num_pages=Count('page_id', distinct=True),
                                  num_watchlist=Count('phrase_id__watchlistkw', distinct=True),  # ???
                                  num_engines=Count('engine_id', distinct=True)) \
                        .order_by('phrase_id__phrase')

    #columnIndexNameMap is required for correct sorting behavior
    columnIndexNameMap = {0: 'phrase_id__phrase', 1: 'num_ips', 2: 'num_pages', 3: 'num_engines', 4: 'add'}
    #path to template used to generate json (optional)
    jsonTemplatePath = 'queries_json.txt'

    #call to generic function from utils
    return get_datatables_records(request, querySet, columnIndexNameMap, jsonTemplatePath)


def get_ranks(request, page, start_date="", end_date=""):
    """ get rank data for kws or landing pages, default dates set in date_select() fx """

    # client from form
    client_id = client_select(request.GET)

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    if page == 'queries':
        object_id = 'phrase_id'
        page_name = 'Queries'

    else:
        object_id = 'page_id'
        page_name = 'Pages'

    rank_objects = LogSeRank.objects.filter(position__gt=0, client_id=client_id)

    position_chart = process_time_series(rank_objects,
                                         start_date,
                                         end_date,
                                         'refdate',
                                         Avg('position'))

    all_pos_cnt = round(sum(item['y'] for item in position_chart))

    all_page_avg = round(all_pos_cnt / len(position_chart))

    # for setting domain of chart
    largest_position = max(item['y'] for item in position_chart)

    object_chart  = process_time_series(rank_objects,
                                        start_date,
                                        end_date,
                                        'refdate',
                                        Count(object_id, distinct=True))

    all_page_cnt = round(sum(item['y'] for item in object_chart))

    return render(request, 'ranks.html', {'client_id': client_id,
                                          'start_date': start_date,
                                          'end_date': end_date,
                                          'first_data_date': first_data_date,
                                          'last_data_date': last_data_date,
                                          'largest_position': largest_position,
                                          'page_name': page_name,
                                          'page': page,
                                          'object_chart': object_chart,
                                          'position_chart': position_chart,
                                          'all_page_cnt': all_page_cnt,
                                          'all_page_avg': all_page_avg})


def get_ranks_datatable(request, page):
    """ produces the datatable section of get_ranks """

    # client from form
    client_id = client_select(request.GET)

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    #prepare the params

    if page == 'queries':
        id = 'phrase_id'
        value = 'phrase_id__phrase'

    else:
        id = 'page_id'
        value = 'page_id__page'

    # initial querySet
    # retrieves all search queries and visitors for which we have a rank in the given time-frame
    # does not retrieve a count of all visitors
    # who have come through the search query during the time-frame
    querySet = LogSeRank.objects \
                        .values(id, value) \
                        .filter(position__gt=0,
                                refdate__range=[start_date, end_date],
                                client_id=client_id) \
                        .annotate(num_ips=Count('ip', distinct=True),
                                  num_rank=Count('position'),
                                  avg_rank=Avg('position'),
                                  st_rank=StdDev('position'),
                                  min_rank=Min('position'),
                                  max_rank=Max('position')) \
                        .order_by(value)

    #columnIndexNameMap is required for correct sorting behavior
    columnIndexNameMap = {0: value,
                          1: 'engine_id',
                          2: 'num_ips',
                          3: 'num_rank',
                          4: 'avg_rank',
                          5: 'st_rank',
                          6: 'min_rank'}

    #path to template used to generate json (optional)
    jsonTemplatePath = 'ranks_json.txt'

    #call to generic function from utils
    return get_datatables_records(request, querySet, columnIndexNameMap, jsonTemplatePath)


def get_phrase(request, phrase):
    """ get data on a particular search query """

    # client from form
    client_id = client_select(request.GET)

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    phrase_name = Kw.objects.filter(pk=phrase)

    rank_ts = LogSeRank.objects.filter(phrase_id=phrase, position__gt=0)

    rankings_chart = process_time_series(rank_ts, start_date, end_date, 'refdate', Avg('position'))

    # remove case where y is 0, meaning we found no position > 0, for a given day
    # basically qsstats-magic adds 0 for days in which no values were found
    rankings_chart[:] = [d for d in rankings_chart if d.get('y') != 0]

    # for setting domain of chart
    if len(rankings_chart) > 0:
        largest_position = max(item['y'] for item in rankings_chart)
        all_rank_cnt = sum(item['y'] for item in rankings_chart)
        all_phrase_avg = round(all_rank_cnt / len(rankings_chart))

    else:
        largest_position = 0
        all_rank_cnt = 0
        all_phrase_avg = 0

    ip_ts = LogSeRank.objects.filter(phrase_id=phrase, client_id=client_id)

    ip_chart = process_time_series(ip_ts, start_date, end_date, 'refdate',
                                   Count('ip', distinct=True))

    all_phrase_cnt = sum(item['y'] for item in ip_chart)

    ip_chart = json.dumps(ip_chart, sort_keys=True)

    pages = LogSeRank.objects \
                     .values('page_id', 'page_id__page', 'position', 'refdate') \
                     .filter(phrase_id=phrase,
                             refdate__range=(start_date, end_date)) \
                     .order_by('page_id__page', 'refdate')

    # convert queryset to list and remove ranks of '0' for sparkline
    # NO - the reason i am not eliminating 0 rank from queryset is to get ALL the pages assoc with
    # a phrase, not just ranked, HOWEVER, I don't want to chart ranks of 0, so if a page has only
    # one appearance in the dictionary and a position of zero I want to keep it

    #pages = list(pages)
    #pages = [ e['position'] = 'na' for e in pages if e['position'] = 0 ]

    return render(request, 'phrase.html', {'client_id': client_id,
                                           'start_date': start_date,
                                           'end_date': end_date,
                                           'first_data_date': first_data_date,
                                           'last_data_date': last_data_date,
                                           'ip_chart': ip_chart,
                                           'all_phrase_cnt': all_phrase_cnt,
                                           'all_phrase_avg': all_phrase_avg,
                                           'phrase_name': phrase_name,
                                           'rankings_chart': rankings_chart,
                                           'rank_ts': rank_ts,
                                           'largest_position': largest_position,
                                           'pages': pages})


def get_landing_pages(request, start_date="", end_date=""):
    """ get landing pages data """

    # client from form
    client_id = client_select(request.GET)

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    landing_pages = LogSeRank.objects \
                             .values('page_id', 'page_id__page') \
                             .filter(refdate__range=[start_date, end_date],
                                     client_id=client_id)

    gcount        = landing_pages.filter(engine_id__engine__contains='Google') \
                                 .annotate(num_google=Count('engine_id'))

    bing_cnt      = landing_pages.filter(engine_id__engine__contains='Bing') \
                                 .annotate(num_bing=Count('engine_id'))

    yahoo_cnt     = landing_pages.filter(engine_id__engine__contains='Yahoo') \
                                 .annotate(num_yahoo=Count('engine_id'))

    phrase_cnt    = landing_pages.annotate(num_phrase=Count('phrase_id', distinct=True))

    ip_cnt        = landing_pages.annotate(num_ip=Count('ip', distinct=True))

    # http://stackoverflow.com/questions/5501810/join-two-lists-of-dictionaries-on-a-single-key
    # nice to create a separate function in utils/view.py for this as we use it in get_page as well
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

    all_page = process_time_series(landing_pages,
                                   start_date,
                                   end_date,
                                   'refdate',
                                   Count('page_id', distinct=True))

    all_page_cnt = sum(item['y'] for item in all_page)

    all_page_avg = round(all_page_cnt / len(all_page))

    all_page = json.dumps(all_page, sort_keys=True)

    return render(request, 'landing_pages.html', {'client_id': client_id,
                                                  'start_date': start_date,
                                                  'end_date': end_date,
                                                  'first_data_date': first_data_date,
                                                  'last_data_date': last_data_date,
                                                  'combo': combo,
                                                  'all_page': all_page,
                                                  'all_page_cnt': all_page_cnt,
                                                  'all_page_avg': all_page_avg})


def get_page(request, page):
    """ get data for single landing page """

    # client from form
    client_id = client_select(request.GET)

    start_date, end_date, first_data_date, last_data_date = date_select(request.GET, client_id)

    page_name = Page.objects.filter(pk=page)

    rank_ts  = LogSeRank.objects.filter(page_id=page, position__gt=0)

    rankings_chart = process_time_series(rank_ts, start_date, end_date, 'refdate', Avg('position'))
    # remove case where y is 0, meaning we found no position > 0, for a given day
    # basically qsstats-magic adds 0 for days in which no values were found
    rankings_chart[:] = [d for d in rankings_chart if d.get('y') != 0]

    if len(rankings_chart) > 0:
        largest_position = max(item['y'] for item in rankings_chart)

    else:
        largest_position = 1

    ip_ts = LogSeRank.objects.filter(page_id=page, client_id=client_id)

    ip_chart = process_time_series(ip_ts, start_date, end_date, 'refdate', Count('ip', distinct=True))

    all_page_cnt = sum(item['y'] for item in ip_chart)

    all_rank_cnt = sum(item['y'] for item in rankings_chart)

    all_page_avg = round(all_rank_cnt / len(rankings_chart))

    ip_chart = json.dumps(ip_chart, sort_keys=True)

    kws       = LogSeRank.objects \
                         .values('phrase_id', 'phrase_id__phrase') \
                         .filter(page_id=page,
                                 refdate__range=(start_date, end_date)) \
                         .distinct() \
                         .order_by('phrase_id__phrase')

    ip_cnt    = kws.annotate(num_ip=Count('ip', distinct=True))

    gcount    = kws.filter(engine_id__engine__contains='Google') \
                   .annotate(num_google=Count('engine_id'))

    bing_cnt  = kws.filter(engine_id__engine__contains='Bing') \
                   .annotate(num_bing=Count('engine_id'))

    yahoo_cnt = kws.filter(engine_id__engine__contains='Yahoo') \
                   .annotate(num_yahoo=Count('engine_id'))

    # http://stackoverflow.com/questions/5501810/join-two-lists-of-dictionaries-on-a-single-key
    d = defaultdict(dict)
    for item in (kws, ip_cnt, gcount, bing_cnt, yahoo_cnt):
        for elem in item:
            d[elem['phrase_id']].update(elem)
    combo = d.values()

    return render(request, 'page.html', {'client_id': client_id,
                                         'start_date': start_date,
                                         'end_date': end_date,
                                         'first_data_date': first_data_date,
                                         'last_data_date': last_data_date,
                                         'ip_chart': ip_chart,
                                         'rankings_chart': rankings_chart,
                                         'all_page_cnt': all_page_cnt,
                                         'all_page_avg': all_page_avg,
                                         'largest_position': largest_position,
                                         'page_name': page_name,
                                         'kws': combo})


def get_watchlist(request):
    """ get/create watchlist """

    client_id = client_select(request.GET)
    # user = request.user.id
    watchlist = WatchListKw.objects.filter(owner=request.user.id) \
                                   .values('phrase__phrase', 'watchlistkwnote__note', 'refdate') \
                                   .order_by('-refdate', 'phrase__phrase')

    return render(request, 'watchlist.html', {'client_id': client_id,
                                              'watchlist': watchlist})


def add_watchlist_kw(request):
    """ add form for watchlist kws """

    client_id = client_select(request.GET)

    if request.GET:
        phrase_id = request.GET['phrase_id']
    else:
        phrase_id = request.POST['phrase_id']

    u = User.objects.get(pk=request.user.id)

    form = WatchListKwForm(instance=u)  # A form bound to the POST data
    kw_note_formset = KwNoteFormSet(instance=WatchListKw())

    form.fields['owner'].initial = request.user.id
    # form.fields['phrase'].initial = phrase_id
    form.fields['phrase'].queryset = Kw.objects.filter(pk=phrase_id)
    form.fields['phrase'].initial = phrase_id

    if request.method == 'POST':
        form = WatchListKwForm(request.POST)  # A form bound to the POST data
        kw_note_formset = KwNoteFormSet(instance=WatchListKw())

        if form.is_valid():  # All validation rules pass

            watchlist_kw = form.save(commit=False)
            kw_note_formset = KwNoteFormSet(request.POST, instance=watchlist_kw)

            if kw_note_formset.is_valid():
                watchlist_kw.save()
                kw_note_formset.save()

                return redirect('/watchlist_success/?phrase_id=' + phrase_id)  # Redirect after POST

    return render(request, 'form_watchlist_kw.html', {'client_id': client_id,
                                                      'form': form,
                                                      'phrase_id': phrase_id,
                                                      'kw_note_formset': kw_note_formset})


def watchlist_success(request):

    return render(request, 'watchlist_success.html', {},)
