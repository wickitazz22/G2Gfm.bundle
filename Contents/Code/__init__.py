######################################################################################
#
#	G2G.fm (BY TEHCRUCIBLE) - v0.01
#
######################################################################################

TITLE = "G2G.fm"
PREFIX = "/video/g2gfm"
ART = "art-default.jpg"
ICON = "icon-default.png"
ICON_LIST = "icon-list.png"
ICON_COVER = "icon-cover.png"
ICON_SEARCH = "icon-search.png"
ICON_NEXT = "icon-next.png"
ICON_MOVIES = "icon-movies.png"
ICON_SERIES = "icon-series.png"
BASE_URL = "http://g2g.fm"

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_COVER)
	DirectoryObject.art = R(ART)
	PopupDirectoryObject.thumb = R(ICON_COVER)
	PopupDirectoryObject.art = R(ART)
	VideoClipObject.thumb = R(ICON_COVER)
	VideoClipObject.art = R(ART)
	
	HTTP.CacheTime = CACHE_1HOUR
	HTTP.Headers['User-Agent'] = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_8_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/31.0.1650.63 Safari/537.36'
	HTTP.Headers['Referer'] = 'http://g2g.fm/'
	
######################################################################################
# Menu hierarchy

@handler(PREFIX, TITLE, art=ART, thumb=ICON)
def MainMenu():

	oc = ObjectContainer()
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="Movies", category = "/movies", page_count = 1), title = "Movies", thumb = R(ICON_MOVIES), summary = "Watch the latest movies in HD from G2G.fm!"))
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="TV Series", category = "/tvseries", page_count = 1), title = "TV Series", thumb = R(ICON_SERIES), summary = "Watch the latest TV series in HD from G2G.fm!"))
	
	return oc

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")	
def ShowCategory(title, category, page_count):

	oc = ObjectContainer(title1 = title)
	page_data = HTML.ElementFromURL(BASE_URL + category + "/index.php?&page=" + str(page_count))

	for each in page_data.xpath("//td[@class='topic_content']"):

		show_url = BASE_URL + category + "/" + each.xpath("./div/a/@href")[0]
		show_title = each.xpath("./div/a/img/@alt")[0]
		show_thumb = each.xpath("./div/a/img/@src")[0]
		show_summary = each.xpath("./div/a/pre/text()")[0]
		
		if category == "/movies":
			oc.add(MovieObject(
				url = show_url,
				title = show_title,
				thumb = show_thumb,
				summary = show_summary
				)
			)

		elif category == "/tvseries":
			oc.add(DirectoryObject(
				key = Callback(PageEpisodes, show_title = show_title, show_url = show_url, show_thumb = show_thumb),
				title = show_title,
				thumb = show_thumb,
				summary = show_summary
				)
			)
	
	oc.add(NextPageObject(
		key = Callback(ShowCategory, title = title, category = category, page_count = int(page_count) + 1),
		title = "More...",
		thumb = R(ICON_NEXT)
			)
		)
	
	return oc

######################################################################################
# Creates an object for every 30 episodes (or part thereof) from a show url

@route(PREFIX + "/pageepisodes")
def PageEpisodes(show_title, show_url, show_thumb):

	oc = ObjectContainer(title1 = show_title)
	page_data = HTML.ElementFromURL(show_url)
	season_list = page_data.xpath("//div[@class='titleline']/h2/a")

	if len(season_list) >= 1:
		for each in season_list:
			season_url = BASE_URL + "/forum/" + each.xpath("./@href")[0]
			season_title = show_title + " " + each.xpath("./text()")[0]
		
			oc.add(DirectoryObject(
				key = Callback(PageEpisodes, show_title = season_title, show_url = season_url, show_thumb = show_thumb),
				title = season_title,
				thumb = R(ICON_LIST)
				)
			)

	for each in page_data.xpath("//div[@class='inner']/h3/a"):
		ep_url = BASE_URL + "/forum/" + each.xpath("./@href")[0]
		ep_title = each.xpath("./text()")[0]
		if ep_title.find("Season Download") < 1:
		
			oc.add(MovieObject(
					url = ep_url,
					title = ep_title.rsplit(" Streaming",1)[0].rsplit(" Download",1)[0],
					thumb = show_thumb
					)
				)
	
	return oc