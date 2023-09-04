from urllib.request import urlopen
import re
from html.parser import HTMLParser


class WeatherHTMLParser(HTMLParser):
    inH2 = False
    wasinH2 = False
    inH2_pre = False
    inH3 = False
    wasinH3 = False
    inH3_pre = False
    H2text = ''
    H3text = ''
    H2pretext = ''
    H3pretext = ''
    infoParameters = {}
    headers = []
    dims = []
    data = []

    def handle_starttag(self, tag, attrs):
        if tag == "h2":
            self.inH2 = True
        elif tag == "pre" and self.wasinH3:
            self.inH3_pre = True
        elif tag == "pre" and self.wasinH2:
            self.inH2_pre = True
        if tag == "h3":
            self.inH3 = True

    def handle_endtag(self, tag):
        if tag == "h2":
            self.inH2 = False
            self.wasinH2 = True
        elif tag == "pre" and self.wasinH3:
            self.inH3_pre = False
        elif tag == "pre" and self.wasinH2:
            self.inH2_pre = False
        elif tag == "h3":
            self.inH3 = False
            self.wasinH3 = True

    def handle_data(self, data):
        if self.inH2_pre:
            self.H2pretext = data
        elif self.inH3_pre:
            self.H3pretext = data
        elif self.inH2:
            self.H2text = data
        elif self.inH3:
            self.H3text = data


class DataAcquirer:
    dataInfo = ''
    unparsedHeightData = ''
    unparsedInfo = ''

    def __init__(self, prefixURL, paramString):
        self.URL = prefixURL
        self.paramString = paramString
        self.request = self.URL + self.paramString

    def prepareRequest(self, FVmap):
        req = self.paramString
        for k in FVmap:
            req = req.replace("<<" + str(k) + ">>", str(FVmap[k]))
        self.request = self.URL + req

    def parseRawData(self):
        parser = WeatherHTMLParser()
        parser.feed(self.lastRaw)
        self.dataInfo = parser.H2text
        self.unparsedHeightData = parser.H2pretext
        self.unparsedInfo = parser.H3pretext

    def chunkstring(self, string, length):
        return [string[0 + i:length + i] for i in range(0, len(string), length)]

    def organizeData(self):
        infoP = [p.strip().split(':') for p in self.unparsedInfo.split('\n') if len(p.strip()) > 0]
        self.infoParameters = dict((k.strip(), v.strip()) for (k, v) in infoP)
        dataTable = [e for e in self.unparsedHeightData.replace('.', ',').split('\n') if len(e.strip()) > 0]
        self.headers = dataTable[1].split()
        self.dims = dataTable[2].split()
        self.data = dataTable[4:]
        self.data = [self.chunkstring(e, 7) for e in self.data]
        self.data = [[e.strip() for e in row] for row in self.data]

    def getData(self):
        self.lastRaw = urlopen(self.request).read().decode()
        self.parseRawData()
        self.organizeData()

    def showLastRawData(self):
        print(self.lastRaw)
