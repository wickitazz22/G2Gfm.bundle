######################################################################################
#                                                                                    #
#                           G2G.fm (BY TEHCRUCIBLE) - v0.08                          #
#                                                                                    #
######################################################################################

TITLE = "g2g.fm"
PREFIX = "/video/g2gfm"
BASE_URL = "http://dayt.se"

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
    HTTP.Headers['Referer'] = 'http://dayt.se/'

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
        key=Callback(ShowCategory, title="Latest Videos", category="/movies", href='/index.php?show=latest-topics'),
        title="Latest Videos", thumb=R(ICON_MOVIES)
        ))
    oc.add(DirectoryObject(
        key=Callback(GenreMenu, title="Genres"),
        title="Genres", thumb=R(ICON_LIST)
        ))

    return oc

######################################################################################
@route(PREFIX + "/show/category")
def ShowCategory(title, category, href):
    """Creates page url from category and creates objects from that page"""

    oc = ObjectContainer(title1=title)

    if href.startswith('http'):
        url = href
    elif href.startswith('//'):
        url = 'http:' + href
    else:
        url = BASE_URL + (href if href.startswith('/') else '/' + href)

    html = HTML.ElementFromURL(url)

    for m in media_list(html, category):
        if category == "/movies" or category == "/episodes":
            oc.add(DirectoryObject(
                key=Callback(EpisodeDetail, title=m['title'], url=m['url'], eid=m['id']),
                title=m['title'],
                thumb=Resource.ContentsOfURLWithFallback(m['thumb'], 'icon-cover.png')
                ))
        else:
            oc.add(DirectoryObject(
                key=Callback(PageEpisodes, title=m['title'], url=m['url']),
                title=m['title'],
                thumb=Resource.ContentsOfURLWithFallback(m['thumb'], 'icon-cover.png')
                ))

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

    oc = ObjectContainer(title1=title)

    try:
        html = HTML.ElementFromURL(url)
    except Exception as e:
        Log.Critical('* EpisodeDetail Error: %s' %str(e))
        message = 'This media has expired.' if ('HTTP Error' in str(e) and '404' in str(e)) else str(e)
        return MessageContainer('Warning', message)

    ptitle = html.xpath("//title/text()")[0].rsplit(" Streaming",1)[0].rsplit(" Download",1)[0]
    thumb = html.xpath('//img[@id="nameimage"]/@src')
    if thumb:
        thumb = thumb[0] if thumb[0].startswith('http') else BASE_URL + thumb[0]
    else:
        thumb = None
    Log.Debug('* thumb = %s' %thumb)

    wpm = html.xpath('//iframe[@id="wpm"]/@src')
    if not wpm:
        return MessageContainer('Warning', 'No Video Source Found.')

    page_text = HTTP.Request(BASE_URL + wpm[0]).content
    r = Regex(r'[\'\"]\#part(\d+)[\'\"][^\#]+src\=[\"\']([^\;\'\"]+)').findall(page_text)
    if r:
        for p, h in sorted(r):
            gphtml = HTML.ElementFromURL(BASE_URL + h)
            gp_iframe = gphtml.xpath('//iframe/@src')
            if gp_iframe:
                oc.add(VideoClipObject(
                    title='%s-%s' %(p, ptitle),
                    thumb=Resource.ContentsOfURLWithFallback(thumb, 'icon-cover.png'),
                    url=gp_iframe[0]
                    ))

    trailpm = html.xpath('//iframe[@id="trailpm"]/@src')
    if trailpm:
        thtml = HTML.ElementFromURL(BASE_URL + trailpm[0])
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

    oc = ObjectContainer(title1=title)
    html = HTML.ElementFromURL(BASE_URL + "/movies/genre.php?showC=27")

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
        url = BASE_URL + category + "/view.php?id=%i" %eid

        thumb = each.xpath("./div/a/img/@src")[0]
        thumb = thumb if 'http' in thumb else BASE_URL + thumb

        if genre:
            title = thumb.rsplit("/",1)[1].rsplit("-",1)[0]
        else:
            title = each.xpath("./div/a/img/@alt")[0]

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
