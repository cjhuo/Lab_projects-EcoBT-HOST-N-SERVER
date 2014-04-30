#!/bin/env python
import pyaudio
import wave
import threading
from pydub import AudioSegment

class WavRecorder(threading.Thread):
    def __init__(self, record_time=10, chunk=1024, aformat=pyaudio.paInt16, channels=2, rate=44100, device=None):
        threading.Thread.__init__(self)
        self.chunk = chunk
        self.aformat = aformat
        self.channels = channels
        self.rate = rate
        self.record_time = record_time
        self.out_name = "output.wav"
        self.preferred_dev = device
        self.stop = False
        self.pa = pyaudio.PyAudio()

        self.selected_dev = self.findDeviceByName(self.preferred_dev)

        self.frames = []
        self.stream = None

    def findDeviceByName(self, name=None):
        select = 0
        if name:
            info = self.pa.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            for i in range(numdevices):
                if self.pa.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
                    dev_name = self.pa.get_device_info_by_host_api_device_index(0, i).get('name')
                    if dev_name == name:
                        select = i
                        break
        return select

    def run(self):
        self.stream = self.pa.open(format=self.aformat,
                                   channels=self.channels,
                                   rate=self.rate,
                                   input=True,
                                   input_device_index=self.selected_dev,
                                   frames_per_buffer=self.chunk)
        print "*** recording"
        self.frames = []
        for i in range(int(self.rate / self.chunk * self.record_time)):
            data = self.stream.read(self.chunk)
            self.frames.append(data)
        print "*** done"
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

        wf = wave.open(self.out_name, 'wb')
        wf.setnchannels(self.channels)
        wf.setsampwidth(self.pa.get_sample_size(self.aformat))
        wf.setframerate(self.rate)
        wf.writeframes(b''.join(self.frames))
        wf.close()

class MP3Encoder(threading.Thread):
    def __init__(self, fname):
        threading.Thread.__init__(self)
        self.fname = fname

    def run(self):
        recording = AudioSegment.from_wav(self.fname)
        recording.export("output.mp3", format="mp3")


if __name__ == "__main__":
    r = WavRecorder(record_time=10, device="Built-in Microph")
    r.start()
    r.join()
    m = MP3Encoder("output.wav")
    m.start()
    m.join()
