from multiprocessing.pool import Pool
import scipy
import scipy.stats
import numpy

threshold = 0.6
tempsize = 50

def get_step_size( template ):
    zeropad    = numpy.zeros( (12,tempsize-1), numpy.int )
    datapadded = numpy.hstack(( zeropad, template, zeropad ))

    reshapedtemplate = template.reshape(1,tempsize*12)[0].tolist()
    autocorrs = list()

    for i in range(tempsize*2 -1) :
        reshapedpadded = datapadded[:, i:i + tempsize].reshape(1,12*tempsize)[0].tolist()

        autocorrs.append(scipy.stats.pearsonr(reshapedtemplate,reshapedpadded)[0])

#    autocorrs = list(
#        scipy.stats.pearsonr( template.reshape(1,12*tempsize), datapadded[ : , i:i + tempsize ].reshape(1,12*tempsize) )[0]
#            for i in range( len(template) * 2 - 1 )
#    )

    arr_autocorrs = numpy.array( autocorrs )
    filtered_index = numpy.argwhere( arr_autocorrs > threshold )
    return max(1,(filtered_index[-1][0] - filtered_index[0][0])/2)

# First coarse searching, and then specific searching
def get_matched_template_index( original_data, template, step_size ):

    maxcorr  = -1
    candidatelist = []

    reshapedtemp = template.reshape(1,tempsize*12)[0].tolist()

    for i in range( 0, original_data.shape[1] - tempsize, step_size ) :
        reshapeddata = original_data[:, i:i + tempsize].reshape(1,12*tempsize)[0].tolist()
        crosscorr = scipy.stats.pearsonr( reshapedtemp, reshapeddata )[0]
        if crosscorr > threshold :
            candidatelist.append(i)

    for i in candidatelist :
        for j in range(max(0, i - step_size), min(i + step_size, original_data.shape[1] - tempsize)) :
            reshapeddata = original_data[:, j:j+tempsize].reshape(1, 12*tempsize)[0].tolist()
            crosscorr = scipy.stats.pearsonr( reshapedtemp, reshapeddata )[0]

            if crosscorr > maxcorr:
                maxcorr  = crosscorr
                maxindex = j

    if len(candidatelist) == 0 :
        maxindex = -1

    return maxindex

def get_templateParam( searchingpoint, originaldata ):
    template, offset = get_template_and_offset( originaldata, searchingpoint )
    step_size  = get_step_size( template )
    new_offset = offset + ( tempsize / 2 )
    return template, new_offset, step_size

def get_correlation( selectionMode, offset, template, step_size, peakdata, originaldata, index):

    RtoR = peakdata[ index + 1 ] - peakdata[ index ]

    original_data = get_original_chunk( selectionMode, peakdata[index], RtoR, originaldata )
    matched_index = get_matched_template_index( original_data, template, step_size )

    if matched_index != -1 :
        if selectionMode == 'Q' :
            idx = peakdata[index] - ( ( RtoR + tempsize/2 ) / 2 ) + matched_index + offset
        elif selectionMode == 'T' :
            idx = peakdata[index] - (tempsize / 2) + matched_index + offset
    else :
        idx = -1
    return idx

def get_original_chunk( selectionMode, peakpoint, RtoR, originaldata ):
    if selectionMode == 'Q' :
        startpoint = peakpoint - ( ( RtoR + tempsize/2 ) / 2 )
        endpoint   = peakpoint + tempsize/2
    elif selectionMode == 'T' :
        startpoint = peakpoint - tempsize/2
        endpoint   = peakpoint + ( ( RtoR + tempsize/2 ) / 2 )

    return originaldata[:, startpoint:endpoint]

def get_template_and_offset(originaldata, searchingpoint):
    startpoint = searchingpoint - ( tempsize / 2 )
    endpoint   = searchingpoint + ( tempsize / 2 )
    offset     = 0
    if startpoint < 0 :
        offset     = startpoint
        startpoint = 0
        endpoint  -= offset

    return originaldata[:, startpoint:endpoint], offset