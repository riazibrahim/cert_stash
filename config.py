import os
import logging
import requests
from lxml.html import fromstring

basedir = os.getcwd()

class Config:
    SQLALCHEMY_DATABASE_URI = os.environ.get('SQLALCHEMY_DATABASE_URI') or 'sqlite:///'+os.path.join(basedir, 'app.db')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FILE_LOGGING_LEVEL = logging.DEBUG
    CONSOLE_LOGGING_LEVEL = logging.INFO
    LOG_FILENAME = 'cert_stash.log'

    # name servers
    NAME_SERVERS = os.environ.get('NAME_SERVERS') or ['8.8.8.8', '1.1.1.1']

    # Crt.sh base urls
    CERTSH_API_URL = os.environ.get('CERTSH_API_URL') or 'https://crt.sh/?q={}&output=json'
    CERTSH_API_ORG_URL = os.environ.get('CERTSH_API_ORG_URL') or 'https://crt.sh/?o={}&output={}'
    CERTSH_API_REQUEST_ID_URL = os.environ.get('CERTSH_API_REQUEST_ID_URL') or 'https://crt.sh/?id={}&output={}'

    # Multiprocessing
    THREAD_COUNT = 2
    USER_AGENT_LIST = [
        "Mozilla/5.0 (Macintosh; U; PPC Mac OS X; fi-fi) AppleWebKit/420+ (KHTML, like Gecko) Safari/419.3",
        "Mozilla/5.0 (Macintosh; U; PPC Mac OS X; de-de) AppleWebKit/125.2 (KHTML, like Gecko) Safari/125.7",
        "Mozilla/5.0 (Macintosh; U; PPC Mac OS X; en-us) AppleWebKit/312.8 (KHTML, like Gecko) Safari/312.6",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; cs-CZ) AppleWebKit/523.15 (KHTML, like Gecko) Version/3.0 Safari/523.15",
        "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16",
        "Mozilla/5.0 (Macintosh; U; PPC Mac OS X 10_5_6; it-it) AppleWebKit/528.16 (KHTML, like Gecko) Version/4.0 Safari/528.16",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; zh-HK) AppleWebKit/533.18.1 (KHTML, like Gecko) Version/5.0.2 Safari/533.18.5",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; sv-SE) AppleWebKit/533.19.4 (KHTML, like Gecko) Version/5.0.3 Safari/533.19.4",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US) AppleWebKit/533.20.25 (KHTML, like Gecko) Version/5.0.4 Safari/533.20.27",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/534.55.3 (KHTML, like Gecko) Version/5.1.3 Safari/534.53.10",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_2) AppleWebKit/536.26.17 (KHTML, like Gecko) Version/6.0.2 Safari/536.26.17",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.75.14 (KHTML, like Gecko) Version/6.1.3 Safari/537.75.14",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_0) AppleWebKit/600.3.10 (KHTML, like Gecko) Version/8.0.3 Safari/600.3.10",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11) AppleWebKit/601.1.39 (KHTML, like Gecko) Version/9.0 Safari/601.1.39",
        "Mozilla/5.0 (Linux; U; Android 1.5; de-de; HTC Magic Build/CRB17) AppleWebKit/528.5+ (KHTML, like Gecko) Version/3.1.2 Mobile Safari/525.20.1",
        "Mozilla/5.0 (Linux; U; Android 2.1-update1; en-au; HTC_Desire_A8183 V1.16.841.1 Build/ERE27) AppleWebKit/530.17 (KHTML, like Gecko) Version/4.0 Mobile Safari/530.17",
        "Mozilla/5.0 (Linux; U; Android 4.2; en-us; Nexus 10 Build/JVP15I) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Safari/534.30",
        "Mozilla/5.0 (Linux; U; Android-4.0.3; en-us; Galaxy Nexus Build/IML74K) AppleWebKit/535.7 (KHTML, like Gecko) CrMo/16.0.912.75 Mobile Safari/535.7",
        "Mozilla/5.0 (Linux; U; Android-4.0.3; en-us; Xoom Build/IML77) AppleWebKit/535.7 (KHTML, like Gecko) CrMo/16.0.912.75 Safari/535.7",
        "Mozilla/5.0 (Linux; Android 4.0.4; SGH-I777 Build/Task650 & Ktoonsez AOKP) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
        "Mozilla/5.0 (Linux; Android 4.1; Galaxy Nexus Build/JRN84D) AppleWebKit/535.19 (KHTML, like Gecko) Chrome/18.0.1025.166 Mobile Safari/535.19",
        "Mozilla/5.0 (iPhone; U; CPU iPhone OS 5_1_1 like Mac OS X; en) AppleWebKit/534.46.0 (KHTML, like Gecko) CriOS/19.0.1084.60 Mobile/9B206 Safari/7534.48.3",
        "Mozilla/5.0 (iPad; U; CPU OS 5_1_1 like Mac OS X; en-us) AppleWebKit/534.46.0 (KHTML, like Gecko) CriOS/19.0.1084.60 Mobile/9B206 Safari/7534.48.3",
        "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Ubuntu/10.10 Chromium/8.0.552.237 Chrome/8.0.552.237 Safari/534.10",
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.7 (KHTML, like Gecko) Ubuntu/11.10 Chromium/16.0.912.21 Chrome/16.0.912.21 Safari/535.7",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.2 (KHTML, like Gecko) Ubuntu/11.04 Chromium/15.0.871.0 Chrome/15.0.871.0 Safari/535.2",
        "Mozilla/5.0 (X11; Linux i686) AppleWebKit/535.1 (KHTML, like Gecko) Ubuntu/10.04 Chromium/14.0.813.0 Chrome/14.0.813.0 Safari/535.1",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Ubuntu/10.10 Chromium/12.0.742.112 Chrome/12.0.742.112 Safari/534.30",
        "Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/534.10 (KHTML, like Gecko) Ubuntu/10.10 Chromium/8.0.552.237 Chrome/8.0.552.237 Safari/534.10",
        "Mozilla/5.0 (Windows; U; Windows NT 5.0; it-IT; rv:1.7.12) Gecko/20050915",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.0.1) Gecko/20020919",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.9.1b2pre) Gecko/20081015 Fennec/1.0a1",
        "Mozilla/5.0 (X11; U; Linux armv7l; en-US; rv:1.9.2a1pre) Gecko/20090322 Fennec/1.0b2pre",
        "Mozilla/5.0 (Android; Linux armv7l; rv:9.0) Gecko/20111216 Firefox/9.0 Fennec/9.0",
        "Mozilla/5.0 (Android; Mobile; rv:12.0) Gecko/12.0 Firefox/12.0",
        "Mozilla/5.0 (Android; Mobile; rv:14.0) Gecko/14.0 Firefox/14.0",
        "Mozilla/5.0 (Mobile; rv:14.0) Gecko/14.0 Firefox/14.0",
        "Mozilla/5.0 (Mobile; rv:17.0) Gecko/17.0 Firefox/17.0",
        "Mozilla/5.0 (Tablet; rv:18.1) Gecko/18.1 Firefox/18.1",
        "Mozilla/5.0 (Android; Mobile; rv:28.0) Gecko/28.0 Firefox/28.0",
        "Mozilla/5.0 (Android; Tablet; rv:29.0) Gecko/29.0 Firefox/29.0",
        "Mozilla/5.0 (Android; Mobile; rv:40.0) Gecko/40.0 Firefox/40.0",
        "Mozilla/5.0 (iPad; CPU iPhone OS 8_3 like Mac OS X) AppleWebKit/600.1.4 (KHTML, like Gecko) FxiOS/1.0 Mobile/12F69 Safari/600.1.4",
        "Mozilla/5.0 (Windows; U; Win98; en-US; rv:1.5) Gecko/20031007 Firebird/0.7",
        "Mozilla/5.0 (Windows; U; Win95; en-US; rv:1.5) Gecko/20031007 Firebird/0.7",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; en-US; rv:1.9.1b3) Gecko/20090305 Firefox/3.1b3 GTB5",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.5; ko; rv:1.9.1b2) Gecko/20081201 Firefox/3.1b2",
        "Mozilla/5.0 (X11; U; SunOS sun4u; en-US; rv:1.9b5) Gecko/2008032620 Firefox/3.0b5",
        "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.8.1.12) Gecko/20080214 Firefox/2.0.0.12",
        "Mozilla/5.0 (Windows; U; Windows NT 5.1; cs; rv:1.9.0.8) Gecko/2009032609 Firefox/3.0.8",
        "Mozilla/5.0 (X11; U; OpenBSD i386; en-US; rv:1.8.0.5) Gecko/20060819 Firefox/1.5.0.5",
        "Mozilla/5.0 (Windows; U; Windows NT 5.0; es-ES; rv:1.8.0.3) Gecko/20060426 Firefox/1.5.0.3",
        "Mozilla/5.0 (Windows; U; WinNT4.0; en-US; rv:1.7.9) Gecko/20050711 Firefox/1.0.5",
        "Mozilla/5.0 (Windows; Windows NT 6.1; rv:2.0b2) Gecko/20100720 Firefox/4.0b2",
        "Mozilla/5.0 (X11; Linux x86_64; rv:2.0b4) Gecko/20100818 Firefox/4.0b4",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.2) Gecko/20100308 Ubuntu/10.04 (lucid) Firefox/3.6 GTB7.1",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b7) Gecko/20101111 Firefox/4.0b7",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:2.0b8pre) Gecko/20101114 Firefox/4.0b8pre",
        "Mozilla/5.0 (X11; Linux x86_64; rv:2.0b9pre) Gecko/20110111 Firefox/4.0b9pre",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.0b9pre) Gecko/20101228 Firefox/4.0b9pre",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:2.2a1pre) Gecko/20110324 Firefox/4.2a1pre",
        "Mozilla/5.0 (X11; U; Linux amd64; rv:5.0) Gecko/20100101 Firefox/5.0 (Debian)",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:6.0a2) Gecko/20110613 Firefox/6.0a2",
        "Mozilla/5.0 (X11; Linux i686 on x86_64; rv:12.0) Gecko/20100101 Firefox/12.0",
        "Mozilla/5.0 (Windows NT 6.1; rv:15.0) Gecko/20120716 Firefox/15.0a2",
        "Mozilla/5.0 (X11; Ubuntu; Linux armv7l; rv:17.0) Gecko/20100101 Firefox/17.0",
        "Mozilla/5.0 (Windows NT 6.1; rv:21.0) Gecko/20130328 Firefox/21.0",
        "Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:22.0) Gecko/20130328 Firefox/22.0",
        "Mozilla/5.0 (Windows NT 5.1; rv:25.0) Gecko/20100101 Firefox/25.0",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:25.0) Gecko/20100101 Firefox/25.0",
        "Mozilla/5.0 (Windows NT 6.1; rv:28.0) Gecko/20100101 Firefox/28.0",
        "Mozilla/5.0 (X11; Linux i686; rv:30.0) Gecko/20100101 Firefox/30.0",
        "Mozilla/5.0 (Windows NT 5.1; rv:31.0) Gecko/20100101 Firefox/31.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:33.0) Gecko/20100101 Firefox/33.0",
        "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0",
        "Mozilla/5.0 (BeOS; U; Haiku BePC; en-US; rv:1.8.1.21pre) Gecko/20090227 BonEcho/2.0.0.21pre",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1.9) Gecko/20071113 BonEcho/2.0.0.9",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.8.1) Gecko/20061026 BonEcho/2.0",
        "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko/2009033017 GranParadiso/3.0.8",
        "Mozilla/5.0 (Macintosh; U; Intel Mac OS X 10.6; en-US; rv:1.9.2) Gecko/20100411 Lorentz/3.6.3 GTB7.0",
        "Mozilla/5.0 (X11; U; Linux i686; it; rv:1.9.3a1pre) Gecko/20091019 Minefield/3.7a1pre",
        "Mozilla/5.0 (Windows; U; Windows NT 5.0; en-US; rv:1.9.3a4pre) Gecko/20100402 Minefield/3.7a4pre",
        "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.2a2pre) Gecko/20090901 Ubuntu/9.10 (karmic) Namoroka/3.6a2pre",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; en-US; rv:1.9.2a1) Gecko/20090806 Namoroka/3.6a1",
        "Mozilla/5.0 (Windows; U; Windows NT 6.1; cs; rv:1.9.2a2pre) Gecko/20090912 Namoroka/3.6a2pre (.NET CLR 3.5.30729)",
        "Mozilla/5.0 (X11; U; Linux x86_64; en-US; rv:1.9.1b3pre) Gecko/20090109 Shiretoko/3.1b3pre",
        "Mozilla/5.0 (Windows; U; Windows NT 6.0; en-US; rv:1.9.1b4pre) Gecko/20090311 Shiretoko/3.1b4pre",
        "Opera/5.11 (Windows 98; U) [en]",
        "Mozilla/4.0 (compatible; MSIE 5.0; Windows 98) Opera 5.12 [en]",
        "Opera/6.0 (Windows 2000; U) [fr]",
        "Mozilla/4.0 (compatible; MSIE 5.0; Windows NT 4.0) Opera 6.01 [en]",
        "Opera/7.03 (Windows NT 5.0; U) [en]",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1) Opera 7.10 [en]",
        "Opera/9.02 (Windows XP; U; ru)",
        "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; en) Opera 9.24",
        "Opera/9.51 (Macintosh; Intel Mac OS X; U; en)",
        "Opera/9.70 (Linux i686 ; U; en) Presto/2.2.1",
        "Opera/9.80 (Windows NT 5.1; U; cs) Presto/2.2.15 Version/10.00",
        "Opera/9.80 (Windows NT 6.1; U; sv) Presto/2.7.62 Version/11.01",
        "Opera/9.80 (Windows NT 6.1; U; en-GB) Presto/2.7.62 Version/11.00",
        "Opera/9.80 (Windows NT 6.1; U; zh-tw) Presto/2.7.62 Version/11.01",
        "Opera/9.80 (Windows NT 6.0; U; en) Presto/2.8.99 Version/11.10",
        "Opera/9.80 (X11; Linux i686; U; ru) Presto/2.8.131 Version/11.11",
        "Opera/9.80 (Windows NT 5.1) Presto/2.12.388 Version/12.14",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/27.0.1453.12 Safari/537.36 OPR/14.0.1116.4",
        "Mozilla/5.0 (Windows NT 6.1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.29 Safari/537.36 OPR/15.0.1147.24 (Edition Next)",
        "Opera/9.80 (Linux armv6l ; U; CE-HTML/1.0 NETTV/3.0.1;; en) Presto/2.6.33 Version/10.60",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.1750.154 Safari/537.36 OPR/20.0.1387.91",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Oupeng/10.2.1.86910 Safari/534.30",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36 OPR/26.0.1656.60",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2376.0 Safari/537.36 OPR/31.0.1857.0",
        "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.85 Safari/537.36 OPR/32.0.1948.25"
    ]

    # PROXY_LIST = [
    #     '187.87.38.28:53281',
    #     '144.76.214.156:1080',
    #     '216.98.9.150:3128',
    #     '80.76.40.227:3128'
    # ]


    PROXY_LIST = {
        'https': '187.87.38.28:53281'
    }