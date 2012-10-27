__author__ = 'leetop'
import scipy
import scipy.signal
import numpy
import pylab

class QrsDetectionError(Exception):
    def __init__(self, value):
        self.parameter = value

    def __str__(self):
        return repr(self.parameter)

class Ecg() :
    def __init__(self, ecgdata, infodict):
        self.infodict = infodict
        self._readinfo()
        self.data = numpy.array(ecgdata).transpose()

        if len(self.data)==1:
            self.data = numpy.array([self.data]).transpose()

    def _readinfo(self):
        """Read the info and fill missing values with defaults
        """
        # defaults
        self.name =  ''
        self.age =  0
        self.sex = 'u'
        self.samplingrate = 200

        for variable, key in [
            (self.name, 'name'),
            (self.age, 'age'),
            (self.sex, 'sex'),
            (self.samplingrate, 'samplingrate')]:
            try:
                variable = self.infodict[key]
            except KeyError:
                self._warning("Info does not contain %s, replacing with %s"
                %(key, variable))

    def _warning(self, msg):
        print msg

    def bpfilter(self, ecg):
        Nyq = self.samplingrate / 2

        wn = [5.0/ Nyq, 15.0 / Nyq]
        b,a = scipy.signal.butter(3, wn, btype = 'bandpass')

        return scipy.signal.filtfilt(b,a,ecg)

    def mw_integrate(self, ecg):

        window_length = int(80 * (float(self.samplingrate) / 1000))

        int_ecg = scipy.zeros_like(ecg)
        cs = ecg.cumsum()

        int_ecg[window_length:] = (cs[window_length:] -
                                   cs[:-window_length]) / window_length
        int_ecg[:window_length] = cs[:window_length] / scipy.arange(
            1, window_length + 1)

        return int_ecg

    def qrsDetect(self, qrslead=0):

        if len(self.data.shape) == 1:
            self.raw_ecg = self.data
        else:
            self.raw_ecg = self.data[:,qrslead]

        self.filtered_ecg = self.bpfilter(self.raw_ecg)
        self.diff_ecg  = scipy.diff(self.filtered_ecg)
        self.sq_ecg = (self.diff_ecg)*(self.diff_ecg.transpose())
        self.int_ecg = self.mw_integrate(self.sq_ecg)

        # Construct buffers with last 8 values
        self._initializeBuffers(self.int_ecg)

        peaks = self.peakDetect(self.int_ecg)
        self.checkPeaks(peaks, self.int_ecg)

        # compensate for delay during integration
        self.QRSpeaks = scipy.array(self.QRSpeaks)
        self.QRSpeaks -= 40 * self.samplingrate / 1000

        print "length of qrs peaks and ecg", len(self.QRSpeaks), len(self.raw_ecg)

        return self.QRSpeaks

    def _initializeBuffers(self, ecg):
        srate = self.samplingrate

        self.signal_peak_buffer = [max(ecg[start*srate:start*srate+srate])
                                   for start in range(8)]
        self.noise_peak_buffer = [0] * 8
        self.rr_buffer = [1] * 8
        self._updateThreshold()

    def _updateThreshold(self):
        noise = scipy.mean(self.noise_peak_buffer)
        signal = scipy.mean(self.signal_peak_buffer)
        self.threshold = noise + 0.3125 * (signal - noise)

    def peakDetect(self, ecg):

        all_peaks = [i for i in range(1,len(ecg)-1)
                     if ecg[i-1] < ecg[i] > ecg[i+1]]
        peak_amplitudes = [ecg[peak] for peak in all_peaks]

        final_peaks = []

        minimumRR = self.samplingrate * 0.2

        peak_candidate_index = all_peaks[0]
        peak_candidate_amplitude = peak_amplitudes[0]

        for peak_index, peak_amplitude in zip(all_peaks, peak_amplitudes):

            if peak_index - peak_candidate_index <= minimumRR and peak_amplitude > peak_candidate_amplitude :
                peak_candidate_index = peak_index
                peak_candidate_amplitude = peak_amplitude

            elif peak_index - peak_candidate_index > minimumRR:
                final_peaks.append(peak_candidate_index)
                peak_candidate_index = peak_index
                peak_candidate_amplitude = peak_amplitude

            else:
                pass

        return final_peaks

    def checkPeaks(self, peaks, ecg):

        amplitudes = [ecg[peak] for peak in peaks]
        self.QRSpeaks = []

        for index, peak in enumerate(peaks):
            amplitude = amplitudes[index]

            if amplitude > self.threshold:
                self.acceptasQRS(peak, amplitude)

            elif amplitude > self.threshold/2 and len(self.QRSpeaks) > 0 and len(peaks) > index+1:
                meanrr = scipy.mean(self.rr_buffer)
                lastQRSms = (peak - self.QRSpeaks[-1]) * (1000 / self.samplingrate)
                lastQRS_to_next_peak = peaks[index+1] - self.QRSpeaks[-1]

                if lastQRSms > 360 and lastQRS_to_next_peak > 1.5 * meanrr:
                    self.acceptasQRS(peak, amplitude)

                else:
                    self.acceptasNoise(peak, amplitude)
            else:
                self.acceptasNoise(peak, amplitude)

#            self.QRSpeaks = scipy.array(self.QRSpeaks)

        return

    def acceptasQRS(self, peak, amplitude):

        self.QRSpeaks.append(peak)
        self.signal_peak_buffer.pop(0)
        self.signal_peak_buffer.append(amplitude)

        if len(self.QRSpeaks) > 1:
            self.rr_buffer.pop(0)
            self.rr_buffer.append(self.QRSpeaks[-1] - self.QRSpeaks[-2])

    def acceptasNoise(self, peak, amplitude):
        self.noise_peak_buffer.pop(0)
        self.noise_peak_buffer.append(amplitude)

    def visualize_qrs_detection(self, savefilename = False):
        ecglength = len(self.raw_ecg)
        ten_seconds = 10 * self.samplingrate

        if ecglength > ten_seconds:
            segmentend = ten_seconds
        elif ecglength < ten_seconds:
            segmentend = ecglength

        segmentQRSpeaks = [peak for peak in self.QRSpeaks if peak < segmentend]



        pylab.figure()
        pylab.subplot(611)
        pylab.plot(self.raw_ecg[:segmentend])
        pylab.ylabel('Raw ECG', rotation='horizontal')
        pylab.subplot(612)
        pylab.plot(self.filtered_ecg[:segmentend])
        pylab.ylabel('Filtered ECG',rotation='horizontal')
        pylab.subplot(613)
        pylab.plot(self.diff_ecg[:segmentend])
        pylab.ylabel('Differential',rotation='horizontal')
        pylab.subplot(614)
        pylab.plot(self.sq_ecg[:segmentend])
        pylab.ylabel('Squared differential',rotation='horizontal')
        pylab.subplot(615)
        pylab.plot(self.int_ecg[:segmentend])
        pylab.ylabel('Integrated', rotation='horizontal')
        pylab.subplot(616)
        pylab.hold(True)
        pylab.plot(self.raw_ecg[:segmentend])
#        pylab.stem(segmentQRSpeaks, self.raw_ecg[segmentQRSpeaks], markerfmt='ro', basefmt='', linefmt='')
        testtest = [120, 326, 532, 738, 944, 1150, 1357, 1563, 1769, 1975]
        pylab.stem(testtest, self.raw_ecg[testtest], markerfmt='ro', basefmt='', linefmt='')
        pylab.hold(False)
        pylab.ylabel('QRS peaks', rotation='horizontal')

        if savefilename:
            pylab.savefig(savefilename)
        else:
            pylab.show()

