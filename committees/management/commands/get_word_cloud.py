# encoding: utf-8
import csv
import sys
import codecs
from datetime import datetime
from optparse import make_option

from django.core.management.base import BaseCommand, CommandError
import matplotlib.pyplot as plt
from wordcloud import WordCloud, STOPWORDS

from committees.models import ProtocolPart


class Command(BaseCommand):
    args = '<output_file>'
    help = "Get the word cloud image for a specified scope or all"

    option_list = BaseCommand.option_list + (
        make_option('--member-id', dest='member_id', default = 0, type=int,
                    help='get cloud for a member'),
        make_option('--party-id', dest='party_id', default=0, type=int,
                    help='get cloud for a party'),
        make_option('--committee-id', dest='committee_id', default=0, type=int,
                    help='get cloud for a party'),
        make_option('--from-date', dest='fromdate', default='', type=str,
                    help='get data from the given date (yyyy-mm-dd)'),
        make_option('--stop-words', dest='stopwords_fn', default='stopwords.txt', type=str,
                   help='the file of the list of excluded words.')
    )

    def handle(self, *args, **options):
        # get the queryset ready
        qs = ProtocolPart.objects.all()
        if options['member_id']:
            qs = qs.filter(speaker__mk__id=options['member_id'])
        if options['party_id']:
            qs = qs.filter(speaker__mk__current_party__id=options['party_id'])
        if options['committee_id']:
            qs = qs.filter(meeting__committee__id=options['committee_id'])
        if options['fromdate']:
            from_date = datetime.strptime(options['fromdate'], '%Y-%m-%d').date()
            qs = qs.filter(meeting__committee__id=from_date)
        # get the text
        text = [i.body for i in qs]
        text = " ".join(text)
        # get the exclude==stopwords
        stopwords = STOPWORDS.copy()
        try:
            f = codecs.open(options["stopwords_fn"], encoding="utf8")
            for l in f:
                stopwords.add(l[:-1])
            f.close()
        except IOError:
            import pdb; pdb.set_trace()
            pass

        wc = WordCloud(font_path="/usr/share/fonts/truetype/Alef/Alef-Regular.ttf",
                       max_words=1000, stopwords=stopwords, margin=10,
                       random_state=1).generate(text)
        nw = []
        # reverse the words as we're RTL
        for w in wc.words_:
            nw.append((w[0][::-1], w[1]))

        wc.fit_words(nw)

        wc.to_file(args[0])
        # show
        plt.imshow(wc)
        plt.axis("off")
        plt.figure()
        plt.show()
