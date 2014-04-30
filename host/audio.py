#!/bin/env python

from multiprocessing import Process
import pyaudio
import wave
import pydub

class WaveRecorder(Process):
    def __init__(self, output_name="output.wav", record_time=60, chunk=1024, aformat=pyaudio.paInt16,
                 channels=2, rate=44100, device=None):
        super(WaveRecorder, self).__init__()
        self.chunk = chunk
        self.aformat = aformat
        self.channels = channels
        self.rate = rate
        self.record_time = record_time
        self.output_name = output_name
        self.pa = pyaudio.PyAudio()
        self.selected_dev = self.findDeviceByName(device)
        self.stop = False

        self.frames = []
        self.stream = None

    def run(self):
        print("haha")
        self.setup()

        for i in range(int(self.rate / self.chunk * self.record_time)):
            data = self.stream.read(self.chunk)
            self.frames.append(data)
        self.stream.stop_stream()
        self.stream.close()
        self.pa.terminate()

    def findDeviceByName(self, device_name=None):
        select = 0
        if device_name:
            info = self.pa.get_host_api_info_by_index(0)
            numdevices = info.get('deviceCount')
            for i in range(numdevices):
                if self.pa.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels') > 0:
                    dev_name = self.pa.get_device_info_by_host_api_device_index(0, i).get('name')
                    if dev_name == device_name:
                        select = i
                        break
        return select

    def setup(self):
        self.stream = self.pa.open(format=self.aformat,
                                   channels=self.channels,
                                   rate=self.rate,
                                   input=True,
                                   input_device_index=self.selected_dev,
                                   frames_per_buffer=self.chunk)

class MP3Encoder(Process):
    def __init__(self):
        super(MP3Encoder, self).__init__()

    def run(self):
        pass


if __name__ == "__main__":
    wr = WaveRecorder(device="Built-in Microph")
    wr.start()
    wr.join()
