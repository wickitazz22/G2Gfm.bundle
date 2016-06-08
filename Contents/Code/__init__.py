######################################################################################
#                                                                                    #
#                           G2G.fm (BY TEHCRUCIBLE) - v0.08                          #
#                                                                                    #
######################################################################################

TITLE = "g2g.fm"
PREFIX = "/video/g2gfm"

ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
ICON_QUEUE = "icon-queue.png"


######################################################################################
def Start():
    """Set global variables"""

    ObjectContainer.title1 = TITLE
    ObjectContainer.art = R(ART)

    DirectoryObject.thumb = R(ICON_COVER)
    DirectoryObject.art = R(ART)

    VideoClipObject.thumb = R(ICON_COVER)
    VideoClipObject.art = R(ART)

    HTTP.CacheTime = CACHE_1HOUR
    HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'

    ValidatePrefs()

######################################################################################
@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():
    """Menu hierarchy"""

    oc = ObjectContainer()
    oc.add(DirectoryObject(
        key=Callback(ShowCategory, title="Movies", category="/movies", href='/movies/index.php?&page=1'),
        title="Movies", thumb=R(ICON_MOVIES)
        ))
    """
    oc.add(DirectoryObject(
        key=Callback(ShowCategory, title="TV Series", category="/tvseries", href='/tvseries/index.php?&page=1'),
        title="TV Series", thumb=R(ICON_SERIES)
        ))
    """
    oc.add(DirectoryObject(
        key=Callback(ShowCategory, title="Latest Videos", category="/latest", href='/index.php?show=latest-topics'),
        title="Latest Videos", thumb=R(ICON_MOVIES)
        ))
    oc.add(DirectoryObject(
        key=Callback(GenreMenu, title="Genres"),
        title="Genres", thumb=R(ICON_LIST)
        ))
    oc.add(PrefsObject(title='Preferences'))

    return oc

######################################################################################
@route(PREFIX + '/validateprefs')
def ValidatePrefs():

    if (Prefs['site_url'] != Dict['site_url']):
        Dict['site_url'] = Prefs['site_url']
        Dict.Save()

    Log.Debug('*' * 80)
    try:
        test = HTTP.Request(Dict['site_url'], cacheTime=0).headers
        Log.Debug('* \"%s\" headers = %s' %(Dict['site_url'], test))
        Dict['domain_test'] = 'Pass'
    except:
        Log.Debug('* \"%s\" is not a valid domain for this channel.' %Dict['site_url'])
        Log.Debug('* Please pick a different URL')
        Dict['domain_test'] = 'Fail'
    Log.Debug('*' * 80)

    Dict.Save()

######################################################################################
def DomainTest():
    """Setup MessageContainer if Dict[\'domain_test\'] failed"""

    if Dict['domain_test'] == 'Fail':
        message = '%s is NOT a Valid Site URL for this channel.  Please pick a different Site URL.'
        return MessageContainer('Error', message %Dict['site_url'])
    else:
        return False

######################################################################################
@route(PREFIX + "/show/category")
def ShowCategory(title, category, href):
    """Creates page url from category and creates objects from that page"""

    if DomainTest() != False:
        return DomainTest()

    oc = ObjectContainer(title1=title)

    html = html_from_url(clean_url(href))

    for m in media_list(html, category):
        oc.add(DirectoryObject(
            key=Callback(EpisodeDetail, title=m['title'], url=m['url'], eid=m['id']),
            title=m['title'],
            thumb=Resource.ContentsOfURLWithFallback(m['thumb'], 'icon-cover.png')
            ))
        """
        if category == "/movies" or category == "/episodes" or category == '/latest':
        else:
            oc.add(DirectoryObject(
                key=Callback(PageEpisodes, title=m['title'], url=m['url']),
                title=m['title'],
                thumb=Resource.ContentsOfURLWithFallback(m['thumb'], 'icon-cover.png')
                ))
        """

    nhref = next_page(html)
    if nhref:
        oc.add(NextPageObject(
            key=Callback(ShowCategory, title=title, category=category, href=nhref),
            title="More...",
            thumb=R(ICON_NEXT)
            ))

    return oc
"""
######################################################################################
@route(PREFIX + "/episode/page")
def PageEpisodes(title, url):
    \"\"\"Checks whether page is episode page or not. If not, display episode list\"\"\"

    oc = ObjectContainer(title1 = title)
    page_data = HTML.ElementFromURL(url)
    eps_list = page_data.xpath("//div[@class='inner']/h3/a")
    season_list = page_data.xpath("//div[@class='titleline']/h2/a")
    if len(season_list) >= 1:
        for each in season_list:
            season_url = BASE_URL + "/forum/" + each.xpath("./@href")[0]
            season_title = title + " " + each.xpath("./text()")[0]

            oc.add(DirectoryObject(
                key = Callback(PageEpisodes, title = season_title, url = season_url),
                title = season_title,
                thumb = R(ICON_SERIES)
                )
            )

    for each in eps_list:
        ep_url = BASE_URL + "/forum/" + each.xpath("./@href")[0]
        ep_title = each.xpath("./text()")[0]

        if ep_title.find("Season Download") < 1:
            oc.add(DirectoryObject(
                key = Callback(EpisodeDetail, title = ep_title.rsplit(" Streaming",1)[0].rsplit(" Download",1)[0], url = ep_url),
                title = ep_title.rsplit(" Streaming",1)[0].rsplit(" Download",1)[0],
                thumb = R(ICON_LIST)
                )
            )

    return oc
"""
######################################################################################
@route(PREFIX + "/episode/detail", eid=int)
def EpisodeDetail(title, url, eid):
    """
    Gets metadata and google docs link from episode page.
    Checks for trailer availablity.
    """

    if DomainTest() != False:
        return DomainTest()

    oc = ObjectContainer(title1=title)

    try:
        html = html_from_url(clean_url(url))
    except Exception as e:
        Log.Critical('* EpisodeDetail Error: %s' %str(e))
        message = 'This media has expired.' if ('HTTP Error' in str(e) and '404' in str(e)) else str(e)
        return MessageContainer('Warning', message)

    ptitle = html.xpath("//title/text()")[0].rsplit(" Streaming",1)[0].rsplit(" Download",1)[0]
    thumb = html.xpath('//img[@id="nameimage"]/@src')
    thumb = (thumb[0] if thumb[0].startswith('http') else clean_url(thumb[0])) if thumb else None

    wpm = html.xpath('//iframe[@id="wpm"]/@src')
    if not wpm:
        return MessageContainer('Warning', 'No Video Source Found.')

    page_text = HTTP.Request(clean_url(wpm[0])).content
    r = Regex(r'[\'\"]\#part(\d+)[\'\"][^\#]+?src\=[\"\']([^\;\'\"]+)').findall(page_text)
    if not r:
        r0 = Regex(r'iframe\s+(?:id\=[\'\"]\w+[\'\"]\s+)?src\=[\"\']([^\;\'\"]+)').search(page_text)
        if r0:
            r = [(u'0', r0.group(1))]
    if r:
        for p, h in sorted(r):
            gphtml = html_from_url(clean_url(h))
            gp_iframe = gphtml.xpath('//iframe/@src')
            if gp_iframe:
                oc.add(VideoClipObject(
                    title='%s-%s' %(p, ptitle) if int(p) != 0 else ptitle,
                    thumb=Resource.ContentsOfURLWithFallback(thumb, 'icon-cover.png'),
                    url=gp_iframe[0]
                    ))

    trailpm = html.xpath('//iframe[@id="trailpm"]/@src')
    if trailpm:
        thtml = html_from_url(clean_url(trailpm[0]))
        yttrailer = thtml.xpath('//iframe[@id="yttrailer"]/@src')
        if yttrailer:
            yttrailer_url = yttrailer[0] if yttrailer[0].startswith('http') else 'https:' + yttrailer[0]
            oc.add(VideoClipObject(url=yttrailer_url, thumb=R(ICON_SERIES), title="Watch Trailer"))

    if len(oc) == 0:
        return MessageContainer('Warning', 'No Media Found')
    else:
        return oc

######################################################################################
@route(PREFIX + "/genre/menu")
def GenreMenu(title):
    """Displays movie genre categories"""

    if DomainTest() != False:
        return DomainTest()

    oc = ObjectContainer(title1=title)

    html = html_from_url(clean_url('/movies/genre.php?showC=27'))
    for m in media_list(html, '/movies', genre=True):
        oc.add(DirectoryObject(
            key=Callback(ShowCategory, title=m['title'], category='/movies', href=m['url']),
            title=m['title'],
            thumb=Resource.ContentsOfURLWithFallback(m['thumb'], 'icon-cover.png')
            ))

    return oc

######################################################################################
def media_list(html, category, genre=False):
    """didn't want to write this over-and-over again"""

    info_list = []
    for each in html.xpath("//td[@class='topic_content']"):
        eid = int(Regex(r'goto\-(\d+)').search(each.xpath("./div/a/@href")[0]).group(1))
        if 'movie' in category:
            url = clean_url("%s/view.php?id=%i" %(category, eid))
        else:
            url = clean_url("/view.php?id=%i" %eid)

        thumb = each.xpath("./div/a/img/@src")[0]
        thumb = thumb if thumb.startswith('http') else clean_url(thumb)

        title = thumb.rsplit("/",1)[1].rsplit("-",1)[0] if genre else each.xpath("./div/a/img/@alt")[0]

        info_list.append({'title': title, 'thumb': thumb, 'url': url, 'id': eid})

    return info_list

######################################################################################
def next_page(html):
    """Seperated out next page code just in case"""

    nhref = False
    next_page_node = html.xpath('//a[contains(@href, "&page=")][text()=">"]/@href')
    if next_page_node:
        nhref = next_page_node[0]

    return nhref

######################################################################################
def html_from_url(url):
    """pull down fresh content when site URL changes"""

    if Dict['site_url'] != Dict['site_url_old']:
        Dict['site_url_old'] = Dict['site_url']
        Dict.Save()
        HTTP.ClearCache()
        HTTP.Headers['Referer'] = Dict['site_url']

    return HTML.ElementFromURL(url)

######################################################################################
def clean_url(href):
    """handle href/URL variations and set corrent Site URL"""

    if href.startswith('http') or href.startswith('//'):
        url = Dict['site_url'] + '/' + href.split('/', 3)[-1]
    else:
        url = Dict['site_url'] + (href if href.startswith('/') else '/' + href)

    return url
