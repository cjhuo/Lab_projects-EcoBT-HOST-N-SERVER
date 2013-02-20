#!/usr/bin/env python
import os
import os.path
import sys
import struct
from datetime import datetime, timedelta

dev = '/dev/disk1'
block = 512
outfile = "ecg_data.txt"
wfd = None


class SDCard_Reader:
    def __init__(self, dev, outfile = None):
        self.blocksize = 512
        self.dev = dev
        self.samplerate = 250
        self.readDev = True
        if os.path.isfile(dev):
            self.readDev = False
        if outfile:
            self.outfile = outfile
        else:
            self.outfile = "ecg_data"
        self.ecg_data = {}
        self.ecg_data['V1'] = []
        self.ecg_data['V2'] = []
        self.ecg_data['V3'] = []
        self.ecg_data['V4'] = []
        self.ecg_data['V5'] = []
        self.ecg_data['V6'] = []
        self.ecg_data['LeadI'] = []
        self.ecg_data['LeadII'] = []
        self.ecg_data['LeadIII'] = []
        self.ecg_data['aVR'] = []
        self.ecg_data['aVL'] = []
        self.ecg_data['aVF'] = []
        self.count = 0
        self.file_count = 0

    def read_data(self):
        if self.readDev:
            print "read from SD card"
            self.read_data_from_SD_card(dump_to_file=True)
        else:
            print "read from file"
            self.read_data_from_file()
        return self.ecg_data

    def read_data_from_file(self):
        fd = open(self.dev, 'r')
        for line in fd.readlines():
            fields = line.split()
            if len(fields) == 12:
                fields = map((lambda x: int(x)), fields)
                self.ecg_data['V1'].append(fields[0])
                self.ecg_data['V2'].append(fields[1])
                self.ecg_data['V3'].append(fields[2])
                self.ecg_data['V4'].append(fields[3])
                self.ecg_data['V5'].append(fields[4])
                self.ecg_data['V6'].append(fields[5])
                self.ecg_data['LeadI'].append(fields[6])
                self.ecg_data['LeadII'].append(fields[7])
                self.ecg_data['LeadIII'].append(fields[8])
                self.ecg_data['aVR'].append(fields[9])
                self.ecg_data['aVL'].append(fields[10])
                self.ecg_data['aVF'].append(fields[11])
                self.ecg_dump_last(dump_to_file=False)
            else:
                # timestamp
                ts = line.split(':')
                start = datetime(year=int(ts[0][:4]),
                                 month=int(ts[0][4:6]),
                                 day=int(ts[0][6:8]),
                                 hour=int(ts[0][8:10]),
                                 minute=int(ts[0][10:12]),
                                 second=int(ts[0][12:]))
                end   = datetime(year=int(ts[1][:4]),
                                 month=int(ts[1][4:6]),
                                 day=int(ts[1][6:8]),
                                 hour=int(ts[1][8:10]),
                                 minute=int(ts[1][10:12]),
                                 second=int(ts[1][12:]))
                self.ecg_data['start_time'] = start
                self.ecg_data['end_time'] = end
                print "Record Start: ", start
                print "Record End  : ", end

    def read_data_from_SD_card(self, dump_to_file=False):
        fd = open(self.dev, 'rb')
        fd.seek(1 * self.blocksize, os.SEEK_SET)
        raw = fd.read(40)
        fields = raw.split('|')
        if fields[0] != "Ec0BT ECG":
            print "Not valid EcoBT ECG Reading"
            exit(0)
        (self.lastBLock,) = struct.unpack("<I", fields[1])
        self.ecg_data['start_time'] = self.ecg_timestamp(fields[2])
        self.ecg_data['end_time'] = self.ecg_timestamp(fields[3])
        if dump_to_file:
            fname = self.outfile + "_%d.txt" % self.file_count
            self.wfd = open(fname, 'w')
        fd.seek(2 * self.blocksize, os.SEEK_SET)
        self.count = 0
        record_start = self.ecg_data['start_time']
        while True:
            raw = fd.read(27)
            if (ord(raw[0]) & 0xC0) != 0xC0:
                break
#            for c in raw:
#                print "0x%02X" % ord(c),
#            print ""
            (status,) = struct.unpack(">I", raw[0:3] + chr(0))
#            print "%06X" % status,
            data = []
            for i in range(1, 9):
                idx = i * 3
                (reading,) = struct.unpack(">i", raw[idx:(idx + 3)] + chr(0))
                reading = reading >> 8
                reading = int(reading * 2.86 / 6 / 10) # micorvolt
                if reading > 32767:
                    reading = 32767
                if reading < -32767:
                    reading = -32767
                data.append(reading)
            self.ecg_data['V6'].append(data[0])
            self.ecg_data['LeadI'].append(data[1])
            self.ecg_data['LeadII'].append(data[2])
            self.ecg_data['V2'].append(data[3])
            self.ecg_data['V3'].append(data[4])
            self.ecg_data['V4'].append(data[5])
            self.ecg_data['V5'].append(data[6])
            self.ecg_data['V1'].append(data[7])
            self.ecg_data['LeadIII'].append(data[2] - data[1])
            self.ecg_data['aVR'].append((data[1] + data[2]) / 2)
            self.ecg_data['aVL'].append(data[1] - (data[2] / 2))
            self.ecg_data['aVF'].append(data[2] - (data[1] / 2))
            self.ecg_dump_last(dump_to_file)
            self.count += 1
            if self.count >= self.samplerate * 300:
                start = "%04d%02d%02d%02d%02d%02d" % (record_start.year, record_start.month, record_start.day, record_start.hour, record_start.minute, record_start.second)
                record_start += timedelta(seconds=5)
                end = "%04d%02d%02d%02d%02d%02d" % (record_start.year, record_start.month, record_start.day, record_start.hour, record_start.minute, record_start.second)
                foot = "%s:%s\n" % (start, end)
                self.wfd.write(foot)
                self.wfd.close()
                self.file_count += 1
                self.count = 0
                fname = self.outfile + "_%d.txt" % self.file_count
                self.wfd = open(fname, 'w')

#        print self.count
        if dump_to_file and self.wfd:
            start = "%04d%02d%02d%02d%02d%02d" % (record_start.year, record_start.month, record_start.day, record_start.hour, record_start.minute, record_start.second)
            record_start = self.ecg_data['end_time']
            end = "%04d%02d%02d%02d%02d%02d" % (record_start.year, record_start.month, record_start.day, record_start.hour, record_start.minute, record_start.second)
            foot = "%s:%s\n" % (start, end)
            self.wfd.write(foot)
            self.wfd.close()

    def ecg_timestamp(self, timestamp):
        tmp = []
        for e in timestamp:
            print "%02X" % ord(e)
            tmp.append(ord(e))
        year = 2000 + tmp[0] * 100 + tmp[1]
        mon = ((tmp[2] & 0xF0) >> 4) * 10 + (tmp[2] & 0x0F)
        day = ((tmp[3] & 0xF0) >> 4) * 10 + (tmp[3] & 0x0F)
        hour = ((tmp[5] & 0xF0) >> 4) * 10 + (tmp[5] & 0x0F)
        minute = ((tmp[6] & 0xF0) >> 4) * 10 + (tmp[6] & 0x0F)
        second = ((tmp[7] & 0xF0) >> 4) * 10 + (tmp[7] & 0x0F)
        return datetime(year=year, month=mon, day=day, hour=hour, minute=minute, second=second)

    def ecg_dump_last(self, dump_to_file):
        output = ""
        output += "V1: %8d  " % self.ecg_data['V1'][-1]
        output += "V2: %8d  " % self.ecg_data['V2'][-1]
        output += "V3: %8d  " % self.ecg_data['V3'][-1]
        output += "V4: %8d  " % self.ecg_data['V4'][-1]
        output += "V5: %8d  " % self.ecg_data['V5'][-1]
        output += "V6: %8d  " % self.ecg_data['V6'][-1]
        output += "LeadI: %8d  "   % self.ecg_data['LeadI'][-1]
        output += "LeadII: %8d  "  % self.ecg_data['LeadII'][-1]
        output += "LeadIII: %8d  " % self.ecg_data['LeadIII'][-1]
        output += "aVR: %8d  " % self.ecg_data['aVR'][-1]
        output += "aVL: %8d  " % self.ecg_data['aVL'][-1]
        output += "aVF: %8d  " % self.ecg_data['aVF'][-1]
        fout  = ""
        fout += "%8d  " % self.ecg_data['V1'][-1]
        fout += "%8d  " % self.ecg_data['V2'][-1]
        fout += "%8d  " % self.ecg_data['V3'][-1]
        fout += "%8d  " % self.ecg_data['V4'][-1]
        fout += "%8d  " % self.ecg_data['V5'][-1]
        fout += "%8d  " % self.ecg_data['V6'][-1]
        fout += "%8d  "   % self.ecg_data['LeadI'][-1]
        fout += "%8d  "  % self.ecg_data['LeadII'][-1]
        fout += "%8d  " % self.ecg_data['LeadIII'][-1]
        fout += "%8d  " % self.ecg_data['aVR'][-1]
        fout += "%8d  " % self.ecg_data['aVL'][-1]
        fout += "%8d  " % self.ecg_data['aVF'][-1]
        print output
        if dump_to_file:
            self.wfd.write(fout + "\n")


if __name__ == "__main__":
    reader = SDCard_Reader(sys.argv[1])
    ecg_data = reader.read_data()
