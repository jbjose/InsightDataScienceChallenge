import argparse
import logging
import json
from itertools import combinations
from datetime import datetime
import time

def get_args():
    """Parge argument list"""

    parser = argparse.ArgumentParser(description='Average degree of tweets per minute')
    parser.add_argument('input_file', help="input file", type=argparse.FileType('r'))
    parser.add_argument('output_file', help="output file", type=argparse.FileType('w'))
    return parser.parse_args()

def process_avg_deg(input_fh, output_fh):
    """Read file-like input object and write to output object"""

    start_time = time.time()
    current_window = []

    for n_line, line in enumerate(input_fh):
        tweet = json.loads(line)

        current_tweet_edges = []

        try:
            # date format is 'Fri Oct 30 15:32:55 +0000 2015'
            # TODO %d is a 0-padded day; using %e (space-padded); need to check what it is
            # TODO Not sure about the +0000 timezone offset; hardcoding it for now
            current_tweet_ts = datetime.strptime(tweet['created_at'], '%a %b %d %H:%M:%S +0000 %Y')

            if len(tweet['entities']['hashtags']) > 1: # Needs at least 2 hashtags
                current_tweet_hashtags = set(
                    ''.join([c for c in ht['text']
                        .lower() if ord(c) < 128])
                        .encode('ascii')
                    for ht in tweet['entities']['hashtags']
                )
                # need to make the list of hashtags unique in case the tweet contained dupe hashtags (of same or diff case)
                current_tweet_edges = list(combinations(current_tweet_hashtags, 2))

        except KeyError: # could not find entities or entities/tweet
            pass # and continue to print prior avg degree to output

        current_window = [(ts,edges) for ts,edges in current_window if (current_tweet_ts - ts).total_seconds() <= 60]
        # The tweets are meant to come in sequentially
        # Could optimize this list comprehension by just iterating through the list till the first instance of <= 60
        # Testing indicates performance of going through the whole minute of tweets is acceptable
        # Flag as future potential area for optimization
        # for i,(ts,_) in enumerate(current_window):
        #     if (current_tweet_ts - ts).total_seconds() <= 60:
        #         current_window = current_window[i:]

        if current_tweet_edges:
            current_window.append((current_tweet_ts, current_tweet_edges))

        # Get all unique edges
        node_connection_counts = {}
        current_window_edges = []
        for _,edges in current_window:
            current_window_edges.extend(edges)
        current_window_edges = set(current_window_edges)
        for node1, node2 in current_window_edges:
            node_connection_counts[node1] = node_connection_counts.get(node1,0) + 1
            node_connection_counts[node2] = node_connection_counts.get(node2,0) + 1

        try:
            output_fh.write('{0:.2f}\n'.format(sum(node_connection_counts.values())/float(len(node_connection_counts))))
        except ZeroDivisionError:
            output_fh.write('0.00\n')

    end_time = time.time()
    logging.info("{} tweets processed.".format(n_line))
    logging.info("Elapsed time was {0:.2f} seconds".format(end_time - start_time))

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)

    args = get_args()
    process_avg_deg(args.input_file, args.output_file)