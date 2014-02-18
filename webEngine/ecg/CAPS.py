from multiprocessing.pool import Pool
import scipy
import scipy.stats
import numpy

threshold = 0.5
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
def get_matched_template_index( original_data, template, correlationVal, indicator ):

    maxcorr  = -1
    candidatelist = []
    nSelected = numpy.flatnonzero(numpy.array(indicator)).shape[0]
    reshapedtemp = template.reshape(1,tempsize * nSelected)[0].tolist()

    arr_corr = []
    for i in range( 0, original_data.shape[1] - tempsize) :
        reshapeddata = original_data[:, i:i + tempsize].reshape(1,nSelected*tempsize)[0].tolist()
        crosscorr = scipy.stats.pearsonr( reshapedtemp, reshapeddata )[0]
        arr_corr.append(crosscorr)

        if maxcorr<crosscorr :
            maxcorr = crosscorr
            maxindex = i
        if crosscorr > threshold :
            candidatelist.append(i)

    if (len(candidatelist) == 0)|( maxcorr<correlationVal) :
        maxindex = -1

    return maxindex

def get_templateParam( searchingpoint, originaldata, indicator ):

    print('Making template and calculate template parameters from selected point...')

    template, offset = get_template_and_offset(originaldata, searchingpoint, indicator)
#    step_size  = get_step_size( template )
    new_offset = offset + ( tempsize / 2 )

    print('Completed to calculate template parameters...')

    return template, new_offset #step_size

def get_correlation( selectionMode, offset, template, peakdata, originaldata, correlationVal, indicator, index):

    RtoR = peakdata[ index + 1 ] - peakdata[ index ]

    original_data = get_original_chunk( selectionMode, peakdata[index], RtoR, originaldata, indicator )
    matched_index = get_matched_template_index( original_data, template, correlationVal, indicator )

    if matched_index != -1 :
        if selectionMode == 'Q' :
#            idx = peakdata[index] - ( ( RtoR + tempsize/2 ) / 2 ) + matched_index + offset
            idx = peakdata[index] + matched_index
        elif selectionMode == 'T' :
#            idx = peakdata[index] - (tempsize / 2) + matched_index + offset
            idx = peakdata[index] + matched_index
    else :
        idx = -1
    return idx

def get_original_chunk( selectionMode, peakpoint, RtoR, originaldata, indicator ):

#    if selectionMode == 'Q' :
#        startpoint = peakpoint - ( ( RtoR + tempsize/2 ) / 2 )
#        endpoint   = peakpoint + tempsize/2
#    elif selectionMode == 'T' :
#        startpoint = max(0, peakpoint - tempsize/2)
#        endpoint   = peakpoint + RtoR

    startpoint = peakpoint - tempsize/2
    endpoint = peakpoint + RtoR + tempsize/2
    selectedchannel = numpy.flatnonzero(numpy.array(indicator))

    return originaldata[selectedchannel, startpoint:endpoint]

def get_template_and_offset(originaldata, searchingpoint, indicator):
    startpoint = searchingpoint - ( tempsize / 2 )
    endpoint   = searchingpoint + ( tempsize / 2 )
    offset     = 0

    if startpoint < 0 :
        offset     = startpoint
        startpoint = 0
        endpoint  -= offset
    selectedchannel = numpy.flatnonzero(numpy.array(indicator))
    return originaldata[selectedchannel, startpoint:endpoint], offset