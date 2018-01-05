#!/usr/bin/python

import matplotlib.pyplot as plt
import numpy
import pandas
from matplotlib.pyplot import hist
import pylab
import scipy.stats
from scipy.stats import pearsonr, spearmanr

def rsquared(x, y):
    """ Return R^2 where x and y are array-like."""
    slope, intercept, r_value, p_value, std_err = scipy.stats.linregress(x, y)
    return r_value**2
def rmse(predictions, targets):
    return numpy.sqrt(((predictions - targets) ** 2).mean())

def printstat(x, r):    
    rsy = numpy.array(df[r+'_syllable_count'])
    rwo = numpy.array(df[r+'_word_count'])
    rse = numpy.array(df[r+'_sentence_count'])

    xsy = numpy.array(df[x+'_syllable_count'])
    xwo = numpy.array(df[x+'_word_count'])
    xse = numpy.array(df[x+'_sentence_count'])
    
    print "AvgE:\t [syllables]: %g, \t [words]: %g,\t [sentences]: %g" % (
                                numpy.mean(abs(rsy - xsy)),
                                numpy.mean(abs(rwo - xwo)),
                                numpy.mean(abs(rse - xse)) )
    print "R2:\t [syllables]: %g, \t [words]: %g,\t [sentences]: %g" % (
                                rsquared(rsy,xsy),
                                rsquared(rwo,xwo),
                                rsquared(rse,xse) )
    print "RMSE:\t [syllables]: %g, \t [words]: %g,\t [sentences]: %g" % (
                                rmse(rsy,xsy),
                                rmse(rwo,xwo),
                                rmse(rse,xse) )
    print "Corr:\t [syllables]: %g, \t [words]: %g,\t [sentences]: %g" % (
                                numpy.corrcoef(rsy,xsy)[0, 1],
                                numpy.corrcoef(rwo,xwo)[0, 1],
                                numpy.corrcoef(rse,xse)[0, 1] )
    print "Slope:\t [syllables]: %g, \t [words]: %g,\t [sentences]: %g" % (
                                numpy.polyfit(xsy,rsy,1)[0],
                                numpy.polyfit(xwo,rwo,1)[0],
                                numpy.polyfit(xse,rse,1)[0] )
    print "Offset:\t [syllables]: %g, \t [words]: %g,\t [sentences]: %g" % (
                                numpy.polyfit(xsy,rsy,1)[1],
                                numpy.polyfit(xwo,rwo,1)[1],
                                numpy.polyfit(xse,rse,1)[1] )


df = pandas.read_csv("data.csv")

print "---- TED test length = %s -----" % len(df)

print "---- Results for %s vs %s -----" % ('wcc', 'wci')
printstat('wcc', 'wci')

print "---- Results for %s vs %s -----" % ('cww', 'wci')
printstat('cww', 'wci')

print "---- Results for %s vs %s -----" % ('scn', 'wci')    # scn computes syllables only!
rsy = numpy.array(df['wci_syllable_count'])
xsy = numpy.array(df['scn_syllable_count'])
print "AvgE:\t [syllables]: %g" % (numpy.mean(abs(rsy - xsy)))
print "R2:\t [syllables]: %g" % (rsquared(rsy,xsy))
print "RMSE:\t [syllables]: %g" % (rmse(rsy,xsy))
print "Corr:\t [syllables]: %g" % (numpy.corrcoef(rsy,xsy)[0, 1])
print "Slope:\t [syllables]: %g" % (numpy.polyfit(xsy,rsy,1)[0])
print "Offset:\t [syllables]: %g" % (numpy.polyfit(xsy,rsy,1)[1])



#===============================================================================
# Histogram -- talk length
#===============================================================================
plt.figure(num=None, figsize=(5, 5), dpi=100, facecolor='w', edgecolor='k')
plt.hist(numpy.array(df['length']), 50, color='g')
plt.xlabel('Talk length [min]')
plt.ylabel('Frequency')
plt.savefig('img/gt__hist_length.png', bbox_inches='tight')

#===============================================================================
# Histogram -- counters abs syllables
#===============================================================================
plt.figure(num=None, figsize=(10, 10), dpi=100, facecolor='w', edgecolor='k')
plt.subplot(2,2,1)
plt.hist(numpy.array(df['wci_syllable_count']), 50, color='r')
plt.xlabel('Syllables, real [count]')
plt.ylabel('Frequency')
plt.title("WCI")
plt.subplot(2,2,2)
plt.hist(numpy.array(df['wcc_syllable_count']), 50, color='r')
plt.xlabel('Syllables, real [count]')
plt.ylabel('Frequency')
plt.title("WCC")
plt.subplot(2,2,3)
plt.hist(numpy.array(df['scn_syllable_count']), 50, color='r')
plt.xlabel('Syllables, real [count]')
plt.ylabel('Frequency')
plt.title("SCN")
plt.subplot(2,2,4)
plt.hist(numpy.array(df['cww_syllable_count']), 50, color='r')
plt.xlabel('Syllables, real [count]')
plt.ylabel('Frequency')
plt.title("CWW")
plt.savefig('img/gt__hist_abs_syllables.png', bbox_inches='tight')

#===============================================================================
# Histogram -- counters abs words
#===============================================================================
plt.figure(num=None, figsize=(10, 10), dpi=100, facecolor='w', edgecolor='k')
plt.subplot(2,2,1)
plt.hist(numpy.array(df['wci_word_count']), 50, color='g')
plt.xlabel('Words, real [count]')
plt.ylabel('Frequency')
plt.title("WCI")
plt.subplot(2,2,2)
plt.hist(numpy.array(df['wcc_word_count']), 50, color='g')
plt.xlabel('Words, real [count]')
plt.ylabel('Frequency')
plt.title("WCC")
plt.subplot(2,2,4)
plt.hist(numpy.array(df['cww_word_count']), 50, color='g')
plt.xlabel('Words, real [count]')
plt.ylabel('Frequency')
plt.title("CWW")
plt.savefig('img/gt__hist_abs_words.png', bbox_inches='tight')

#===============================================================================
# Histogram -- counters abs sentences
#===============================================================================
plt.figure(num=None, figsize=(10, 10), dpi=100, facecolor='w', edgecolor='k')
plt.subplot(2,2,1)
plt.hist(numpy.array(df['wci_sentence_count']), 50, color='b')
plt.xlabel('Sentences, real [count]')
plt.ylabel('Frequency')
plt.title("WCI")
plt.subplot(2,2,2)
plt.hist(numpy.array(df['wcc_sentence_count']), 50, color='b')
plt.xlabel('Sentences, real [count]')
plt.ylabel('Frequency')
plt.title("WCC")
plt.subplot(2,2,3)
plt.hist(numpy.array(df['cww_pause_count']), 50, color='m')
plt.xlabel('Sentences, real [count]')
plt.ylabel('Frequency')
plt.title("CWW PAUSES")
plt.subplot(2,2,4)
plt.hist(numpy.array(df['cww_sentence_count']), 50, color='b')
plt.xlabel('Sentences, real [count]')
plt.ylabel('Frequency')
plt.title("CWW")
plt.savefig('img/gt__hist_abs_sentences.png', bbox_inches='tight')




#===============================================================================
# Histogram -- rate in syllables
#===============================================================================
plt.figure(num=None, figsize=(10, 10), dpi=100, facecolor='w', edgecolor='k')
plt.subplot(2,2,1)
plt.hist(numpy.array(df['wci_syllable_count']/df['length']), 50, color='r')
plt.xlabel('Rate, real [syllable/min]')
plt.ylabel('Frequency')
plt.title("WCI")
plt.subplot(2,2,2)
plt.hist(numpy.array(df['wcc_syllable_count']/df['length']), 50, color='r')
plt.xlabel('Rate, real [syllable/min]')
plt.ylabel('Frequency')
plt.title("WCC")
plt.subplot(2,2,3)
plt.hist(numpy.array(df['scn_syllable_count']/df['length']), 50, color='r')
plt.xlabel('Rate, real [syllable/min]')
plt.ylabel('Frequency')
plt.title("SCN")
plt.subplot(2,2,4)
plt.hist(numpy.array(df['cww_syllable_count']/df['length']), 50, color='r')
plt.xlabel('Rate, real [syllable/min]')
plt.ylabel('Frequency')
plt.title("CWW")
plt.savefig('img/gt__hist_rate_in_syllables.png', bbox_inches='tight')

#===============================================================================
# Histogram -- rate in words
#===============================================================================
plt.figure(num=None, figsize=(10, 10), dpi=100, facecolor='w', edgecolor='k')
plt.subplot(2,2,1)
plt.hist(numpy.array(df['wci_word_count']/df['length']), 50, color='g')
plt.xlabel('Rate, real [word/min]')
plt.ylabel('Frequency')
plt.title("WCI")
plt.subplot(2,2,2)
plt.hist(numpy.array(df['wcc_word_count']/df['length']), 50, color='g')
plt.xlabel('Rate, real [word/min]')
plt.ylabel('Frequency')
plt.title("WCC")
plt.subplot(2,2,4)
plt.hist(numpy.array(df['cww_word_count']/df['length']), 50, color='g')
plt.xlabel('Rate, real [word/min]')
plt.ylabel('Frequency')
plt.title("CWW")
plt.savefig('img/gt__hist_rate_in_words.png', bbox_inches='tight')

#===============================================================================
# Histogram -- rate in sentences
#===============================================================================
plt.figure(num=None, figsize=(10, 10), dpi=100, facecolor='w', edgecolor='k')
plt.subplot(2,2,1)
plt.hist(numpy.array(df['wci_sentence_count']/df['length']), 50, color='b')
plt.xlabel('Rate, real [sentence/min]')
plt.ylabel('Frequency')
plt.title("WCI")
plt.subplot(2,2,2)
plt.hist(numpy.array(df['wcc_sentence_count']/df['length']), 50, color='b')
plt.xlabel('Rate, real [sentence/min]')
plt.ylabel('Frequency')
plt.title("WCC")
plt.subplot(2,2,3)
plt.hist(numpy.array(df['cww_pause_count']/df['length']), 50, color='m')
plt.xlabel('Rate, real [sentence/min]')
plt.ylabel('Frequency')
plt.title("CWW PAUSES")
plt.subplot(2,2,4)
plt.hist(numpy.array(df['cww_sentence_count']/df['length']), 50, color='b')
plt.xlabel('Rate, real [sentence/min]')
plt.ylabel('Frequency')
plt.title("CWW")
plt.savefig('img/gt__hist_rate_in_sentences.png', bbox_inches='tight')

#===============================================================================
# Histogram -- word complexity
#===============================================================================
plt.figure(num=None, figsize=(10, 10), dpi=100, facecolor='w', edgecolor='k')
plt.subplot(2,2,1)
plt.hist(numpy.array(numpy.array(df['wci_syllable_count'])/df['wci_word_count']), 50, color='g')
plt.xlabel('Word complexity [syllable/word]')
plt.ylabel('Frequency')
plt.title("WCI")
plt.subplot(2,2,2)
plt.hist(numpy.array(numpy.array(df['wcc_syllable_count'])/df['wcc_word_count']), 50, color='g')
plt.xlabel('Word complexity [syllable/word]')
plt.ylabel('Frequency')
plt.title("WCC")
plt.subplot(2,2,4)
plt.hist(numpy.array(numpy.array(df['cww_syllable_count'])/df['cww_word_count']), 50, color='g')
plt.xlabel('Word complexity [syllable/word]')
plt.ylabel('Frequency')
plt.title("CWW")
plt.savefig('img/gt__hist_word_complexity.png', bbox_inches='tight')



#===============================================================================
# Histogram -- scores
#===============================================================================
plt.figure(num=None, figsize=(10, 10), dpi=100, facecolor='w', edgecolor='k')
plt.subplot(2,2,1)
plt.hist(numpy.array(df['cww_flesch_reading_ease']), 50, color='r')
plt.xlabel('Real [score]')
plt.ylabel('Frequency')
plt.title("FRE")
plt.subplot(2,2,2)
plt.hist(numpy.array(df['cww_flesch_kincaid_grade_level']), 50, color='r')
plt.xlabel('Real [score]')
plt.ylabel('Frequency')
plt.title("FKGL")
plt.subplot(2,2,3)
plt.hist(numpy.array(df['cww_gunning_fog_index']), 50, color='r')
plt.xlabel('Real [score]')
plt.ylabel('Frequency')
plt.title("GFI")
plt.subplot(2,2,4)
plt.hist(numpy.array(df['cww_forecast_grade_level']), 50, color='r')
plt.xlabel('Real [score]')
plt.ylabel('Frequency')
plt.title("FGL")
plt.savefig('img/gt__hist_comprehension_scores.png', bbox_inches='tight')

