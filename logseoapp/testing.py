from __future__ import division
from collections import defaultdict
import itertools
import operator
from itertools import *

diction = [{'phrase_id': 3518L, 'num_ips': 233, 'num_rank': 287, 'avg_rank': 1.101}, {'phrase_id': 3518L, 'num_ips': 233, 'num_rank': 287, 'avg_rank': 1.101}]

for dict in diction:
    num_ratio = dict['num_rank'] / dict['num_ips']
    dict['ratio'] = num_ratio
#print diction


datas = [{'page_id__page': u'/about-us/', 'position': 1}, {'page_id__page': u'/', 'position': 1}, {'page_id__page': u'/', 'position': 0}, {'page_id__page': u'/about-us/', 'position': 0}, {'page_id__page': u'/about-us/', 'position': 2}, {'page_id__page': u'/take-action/', 'position': 1}, {'page_id__page': u'/blog/', 'position': 1}, {'page_id__page': u'/blog/', 'position': 0}, {'page_id__page': u'/publications/grassrootsguide/farm-bill-programs-and-grants/', 'position': 0}, {'page_id__page': u'/publications/', 'position': 0}, {'page_id__page': u'/publications/grassrootsguide/farm-bill-programs-and-grants/', 'position': 1}, {'page_id__page': u'/blog/', 'position': 3}, {'page_id__page': u'/blog/', 'position': 2}, {'page_id__page': u'/our-work/fbcampaign/', 'position': 4}, {'page_id__page': u'/category/2012-farm-bill/', 'position': 0}, {'page_id__page': u'/take-action/', 'position': 0}, {'page_id__page': u'/our-work/', 'position': 0}, {'page_id__page': u'/', 'position': 2}, {'page_id__page': u'/publications/grassrootsguide/farm-bill-programs-and-grants/', 'position': 4}]


#whatiwant = [{'page_id__page': u'/about-use/', 'position': [1, 0, 2]}, {'page_id__page': u'/', 'position': [1,0,2]}]


datas.sort(key=operator.itemgetter('page_id__page'))
print datas
myList = itertools.groupby(datas, operator.itemgetter('page_id__page'))
print "\n"
for e in myList:
    print "asdf",e[1][0]






