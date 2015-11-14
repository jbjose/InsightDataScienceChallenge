

import argparse
import logging
import json
import time

def get_args():
    """Parge argument list"""

    parser = argparse.ArgumentParser(description='Average degree of tweets per minute')
    parser.add_argument('input_file', help="input file", type=argparse.FileType('r'))
    parser.add_argument('output_file', help="output file", type=argparse.FileType('w'))
    return parser.parse_args()

def clean_tweets(input_fh, output_fh):
    """Remove unicode chars and count tweets with unicode chars"""

    start_time = time.time()

    n_text_with_unicode = 0

    for n_line, line in enumerate(input_fh):
        try:
            tweet = json.loads(line)
            # remove unicode chars
            clean_text = ''.join([c if c not in ['\n','\t'] else ' ' for c in tweet['text'] if ord(c) < 128]).encode('ascii')
            # was there a unicode char?
            if len(clean_text) < len(tweet['text']):
                n_text_with_unicode += 1
            output_fh.write("{0} (timestamp: {1})\n".format(clean_text, tweet['created_at']))
        except KeyError as e:
            # tweet does not contain either text or created_at
            # probably a feed artifact eg {"limit": {"track":5,"timestamp_ms":"1446218985743"} }
            continue
    output_fh.write('\n{0} tweets contained unicode.\n'.format(n_text_with_unicode))

    end_time = time.time()
    logging.info("{0} of {1} tweets with unicode cleaned".format(n_text_with_unicode, n_line))
    logging.info("Elapsed time was {0:.2f} seconds".format(end_time - start_time))

if __name__ == '__main__':
    logging.getLogger().setLevel(logging.DEBUG)

    args = get_args()
    clean_tweets(args.input_file, args.output_file)