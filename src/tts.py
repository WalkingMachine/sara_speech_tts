#!/usr/bin/python
# Script that handles the communication with the tts system
#
# Author: Maxime St-Pierre <me@maximest-pierre.me>
import roslib
import rospy
import urllib2
import os
import time
roslib.load_manifest("sara_speech_tts")


# function that take a text and language and send them to google to generate an
# mp3 file
def google_tts(text, language="en"):
    print text
    if len(text) >= 100:
        toSay = parseText(text)
    else:
        toSay = [text]

    google_translate_url = "https://translate.google.com/translate_tts"

    opener = urllib2.build_opener()
    opener.addheaders = [(
        'User-agent', 'Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.0)'
    )]

    files = []
    for i, sentence in enumerate(toSay):
        print i, len(sentence), sentence
        response = opener.open(
            google_translate_url + '?q=' + sentence.replace(
                ' ', '%20'
            ) + '&tl={0}'.format(language)
        )
        if not response:
            raise Exception()

        filename = str(i) + 'speech_google.mp3'
        ofp = open(filename, 'wb')
        ofp.write(response.read())
        ofp.close()
        files += [filename]

    generation_end = time.time()
    rospy.loginfo("Downloading audio took {0}s".format(
        generation_end - generation_start))

    filenames = " ".join(files)
    play_start = time.time()
    for filename in files:
        os.system(
            "gst-launch-0.10 filesrc location='{0}' ! mad ! audioconvert ! audioresample ! alsasink".format(
                filename)
        )
    play_end = time.time()
    rospy.loginfo("Playing took {0}s".format(play_end - play_start))


def ping_google():
    failure_codes = [512]
    result = os.system("fping -c1 -t100 www.google.com")
    print result
    if int(result) in failure_codes:
        return False
    else:
        return True


def parseText(text):
    """ returns a list of sentences with less than 100 caracters """
    toSay = []
    punct = [',', ':', ';', '.', '?', '!']  # punctuation
    words = text.split(' ')
    sentence = ''
    for w in words:
        if w[len(w) - 1] in punct:  # encountered a punctuation mark
            if (len(sentence) + len(w) + 1 < 100):  # is there enough space?
                sentence += ' ' + w  # add the word
                toSay.append(sentence.strip())  # save the sentence
            else:
                toSay.append(sentence.strip())  # save the sentence
                toSay.append(w.strip())  # save the word as a sentence
            sentence = ''  # start another sentence
        else:
            if (len(sentence) + len(w) + 1 < 100):
                sentence += ' ' + w  # add the word
            else:
                toSay.append(sentence.strip())  # save the sentence
                sentence = w  # start a new sentence
    if len(sentence) > 0:
        toSay.append(sentence.strip())
    return toSay

if __name__ == "__main__":
    rospy.init_node('sara_speech_tts')
