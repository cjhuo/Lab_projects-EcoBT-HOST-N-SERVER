from multiprocessing.pool import Pool
import scipy
import scipy.stats
import numpy

threshold = 0.5
tempsize = 40

def get_step_size( template ):
    zeropad    = numpy.zeros( len(template) - 1, numpy.int )
    datapadded = numpy.hstack(( zeropad, template, zeropad ))
    autocorrs = list(
        scipy.stats.pearsonr( template, datapadded[ i:i + len(template) ] )[0]
            for i in range( len(template) * 2 - 1 )
    )
    arr_autocorrs = numpy.array( autocorrs )
    filtered_index = numpy.argwhere( arr_autocorrs > threshold )
    return (filtered_index[-1][0] - filtered_index[0][0])/2

# First coarse searching, and then specific searching
def get_matched_template_index( original_data, template, step_size ):

    maxcorr    = -1
    x1 = []

    for i in range( 0, len(original_data) - len(template), step_size ) :
        crosscorr, pvalue = scipy.stats.pearsonr( template, original_data[i:i+len(template)] )
        if crosscorr > threshold :
            x1.append(i)

    for i in x1 :
        for j in range(max(0, i - step_size), min(i+step_size,len(original_data) - len(template))) :
            crosscorr, pvalue = scipy.stats.pearsonr( template, original_data[j:j+len(template)] )

            if crosscorr > maxcorr:
                maxcorr  = crosscorr
                maxindex = j

    return maxindex

def SearchingSimilarPoint( searchingpoint, peakdata, originaldata, index ):
    template, offset = get_template_and_offset(originaldata, searchingpoint)
    step_size  = get_step_size( template )
    new_offset = offset + ( len(template) / 2 )
    return get_correlation( index, new_offset, template, step_size, peakdata, originaldata)

def get_correlation( index, offset, template, step_size, peakdata, originaldata ):

    RtoR = peakdata[ index + 1 ] - peakdata[ index ]
    original_data = get_original_chunk( template, peakdata[index], RtoR, originaldata )
    matched_index = get_matched_template_index( original_data, template, step_size )
    idx = peakdata[index] - ( ( RtoR + len(template) ) / 2 ) + matched_index + offset
    return idx

def get_original_chunk( template, peakpoint, RtoR, originaldata ):
    startpoint = peakpoint - ( ( RtoR + len(template) ) / 2 )
    endpoint   = peakpoint + ( ( RtoR + len(template) ) / 2 )
    return originaldata[startpoint:endpoint]

def get_template_and_offset(originaldata, searchingpoint):
    startpoint = searchingpoint - ( tempsize / 2 )
    endpoint   = searchingpoint + ( tempsize / 2 )
    offset     = 0
    if startpoint < 0 :
        offset     = startpoint
        startpoint = 0
        endpoint  -= offset

    return originaldata[startpoint:endpoint], offset