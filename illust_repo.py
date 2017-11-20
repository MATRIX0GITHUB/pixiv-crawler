#! /usr/bin/env python2.7
# -*- coding: utf-8 -*-
# code by </MATRIX>@Neod Anderjon
# =====================================================================
# this python script is built to get a illust all repo images

import urllib2, cookielib, re                                       # crawler depends
import datetime, string, sys
import pllc, priv_lib                                               # local lib

pllc.EncodeDecodeResolve()

# create a class for pixiv dailyRank top
class IllustRepoAll:
    # class include init process
    def __init__(self):
        priv_lib.PrivateLib().__init__()
        # global illust id
        self.illustInputID = raw_input(pllc.SHELLHEAD + 'enter you want to crawl illuster id: ')

    @staticmethod
    def GetInputEssentialInfo(self):
        illustHomeFolder = pllc.SetOSHomeFolder() + self.illustInputID + '/'
        self.workdir = illustHomeFolder
        self.infoPath = illustHomeFolder + 'images.info'
        illustLogFilePath = illustHomeFolder + 'PixivCrawlerLog.log'
        # create illust homefolder
        priv_lib.PrivateLib().MkDir(illustLogFilePath, illustHomeFolder)

        return illustLogFilePath

    # craw illust artwork count
    @staticmethod
    def CheckCrawlTargetCnt(self, logPath):
        cnt_url = pllc.illustHomeURL + self.illustInputID           # get illust artwork count mainpage url
        # build http request
        request = urllib2.Request(cnt_url)
        response = priv_lib.PrivateLib().opener.open(request)
        web_src = response.read().decode("UTF-8", "ignore")

        # mate illust name
        illustNamePattern = re.compile(pllc.illustNameRegex, re.S)
        self.illustName = re.findall(illustNamePattern, web_src)[0][18:][:-1]

        # mate images name
        imagesNamePattern = re.compile(pllc.imagesNameRegex, re.S)
        origName = re.findall(imagesNamePattern, web_src)
        self.imagesName = origName[1:21]

        # mate id and max count parse
        pattern = re.compile(pllc.illustAWCntRegex(self.illustInputID), re.S)
        dataCapture = re.findall(pattern, web_src)

        # cut count from include parse
        nbrPattern = re.compile(pllc.nbrRegex, re.S)
        nbrMate = re.findall(nbrPattern, dataCapture[0])
        maxCnt = string.atoi(nbrMate[1])                            # nbrMate[0] is input id, nbrMate[1] is max count

        # input want image count
        capCnt = string.atoi(raw_input(pllc.SHELLHEAD
                        + 'enter you want to crawl image count(must <= %d, ever page 20 images): ' % maxCnt))
        # count error
        while (capCnt > maxCnt) or (capCnt <= 0):
            capCnt = string.atoi(raw_input(pllc.SHELLHEAD
                        + 'error, input count must <= %d and not 0: ' % maxCnt))
        logContext = "check collect illuster id:" + self.illustInputID + " image(s):%d" % capCnt
        priv_lib.PrivateLib().LogCrawlerWork(logPath, logContext)

        return capCnt

    # craw illust artwork count
    @staticmethod
    def CrawlAllTargetURL(self, nbr, logPath):
        # page request regular:
        # no.1 referer: &type=all request url: &type=all&p=2
        # no.2 referer: &type=all&p=2 request url: &type=all&p=3
        # no.3 referer: &type=all&p=3 request url: &type=all&p=4
        # ...

        # build a mainpage request
        urlTarget = pllc.illustArtworkIndex(self.illustInputID)     # get mainpage all 20 images url
        mainPageHeader = pllc.SetUserAgentForMainPage(urlTarget)
        request = urllib2.Request(url=urlTarget, headers=mainPageHeader)

        # build and install opener
        cookieHandler = urllib2.HTTPCookieProcessor(cookielib.LWPCookieJar())
        opener = urllib2.build_opener(cookieHandler)
        urllib2.install_opener(opener)

        # open webpage, get web src, try two way
        ## response = opener.open(request)
        response = urllib2.urlopen(request, timeout=300)
        ## web_src = response.read().decode("UTF-8", "ignore").encode("GBK", "ignore")
        web_src = response.read().decode("UTF-8", "ignore")
        if response.getcode() == pllc.reqSuccessCode:
            logContext = "mainpage response successed"
        else:
            logContext = "mainpage response timeout, failed"
            exit()                                                  # response fail, exit program
        priv_lib.PrivateLib().LogCrawlerWork(logPath, logContext)

        pattern = re.compile(pllc.imgThumbnailRegex, re.S)          # use regex, find dailyRank art works messages
        urlCapture = re.findall(pattern, web_src)[1:21]             # findall return a tuple include 5 members

        nbrPattern = re.compile(pllc.nbrRegex, re.S)                # cut artwork id list

        artworkIDs = []                                             # images id list
        imgOriginalhttps = []                                       # image original page url
        self.basePages = []                                         # image basic page
        for i in urlCapture:
            vaildWord = i[-47:-19]                                  # cut vaild words
            # init to png, then will change jpg
            build_http = 'https://i.pximg.net/img-original/img/' + vaildWord + '_p0.png'
            # build basic page use to request image
            img_id = re.findall(nbrPattern, vaildWord)[6]           # no.6 member is id
            basePage = pllc.baseWebURL + img_id
            artworkIDs.append(img_id)                               # image id list
            imgOriginalhttps.append(build_http)                     # image url list
            self.basePages.append(basePage)                         # basic page list

        # log images info
        logContext = 'illuster: ' + self.illustName + ' id: ' + self.illustInputID + ' artworks info====>'
        priv_lib.PrivateLib().LogCrawlerWork(logPath, logContext)
        for k, i in enumerate(self.imagesName[:nbr]):
            logContext = 'no.%d image: %s id: %s url: %s' % (k, i, artworkIDs[k], imgOriginalhttps[k])
            priv_lib.PrivateLib().LogCrawlerWork(logPath, logContext)

        return imgOriginalhttps[:nbr]                               # only return need number

    def iraStartCrawler(self):
        # collect essential info
        logFilePath = self.GetInputEssentialInfo(self)
        # log runtime
        starttime = datetime.datetime.now()
        # check website can response crawler
        priv_lib.PrivateLib().CrawlerSignIn(logFilePath)
        # get capture image count
        crawCnt = self.CheckCrawlTargetCnt(self, logFilePath)
        urls = self.CrawlAllTargetURL(self, crawCnt, logFilePath)
        # save images
        priv_lib.PrivateLib().SaveImageBinData(urls, self.basePages, self.workdir, logFilePath)
        # stop log time
        endtime = datetime.datetime.now()
        logContext = "elapsed time: %ds" % (endtime - starttime).seconds
        priv_lib.PrivateLib().LogCrawlerWork(logFilePath, logContext)
        # finish
        priv_lib.PrivateLib().crawlerFinishWork(logFilePath)

# =====================================================================
# code by </MATRIX>@Neod Anderjon
