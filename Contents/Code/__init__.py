######################################################################################
#
#	G2G.fm (BY TEHCRUCIBLE) - v0.02
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
ICON_QUEUE = "icon-queue.png"
BASE_URL = "http://g2g.fm"

######################################################################################
# Set global variables

def Start():

	ObjectContainer.title1 = TITLE
	ObjectContainer.art = R(ART)
	DirectoryObject.thumb = R(ICON_COVER)
	DirectoryObject.art = R(ART)
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
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="Movies", category = "/movies", page_count = 1), title = "Movies", thumb = R(ICON_MOVIES), summary = "Watch the latest movies in HD!"))
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="TV Series", category = "/tvseries", page_count = 1), title = "TV Series", thumb = R(ICON_SERIES), summary = "Watch the most popular TV series in HD!"))
	oc.add(DirectoryObject(key = Callback(ShowCategory, title="Latest Episodes", category = "/episodes", page_count = 1), title = "Latest Episodes", thumb = R(ICON_SERIES), summary = "See the most recently aired episodes!"))
	oc.add(DirectoryObject(key = Callback(Bookmarks, title="My Bookmarks"), title = "My Bookmarks", thumb = R(ICON_QUEUE), summary = "View your bookmarked videos."))
	oc.add(InputDirectoryObject(key=Callback(Search), title = "Search", prompt = "Search for what?", thumb = R(ICON_SEARCH)))
	
	return oc

######################################################################################
# Creates page url from category and creates objects from that page

@route(PREFIX + "/showcategory")	
def ShowCategory(title, category, page_count):

	oc = ObjectContainer(title1 = title)
	page_data = HTML.ElementFromURL(BASE_URL + category + "/index.php?&page=" + str(page_count))

	for each in page_data.xpath("//td[@class='topic_content']"):
		url = BASE_URL + category + "/" + each.xpath("./div/a/@href")[0]
		title = each.xpath("./div/a/img/@alt")[0]
		thumb = each.xpath("./div/a/img/@src")[0]
		summary = each.xpath("./div/a/pre/text()")[0].split("\r\n\r\n")[-2].replace("\n", " ")
		
		if category == "/movies" or category == "/episodes":
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png'),
				summary = summary
				)
			)

		if category == "/tvseries":
			oc.add(DirectoryObject(
				key = Callback(PageEpisodes, title = title, url = url),
				title = title,
				thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png'),
				summary = summary
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
# Checks whether page is episode page or not. If not, display episode list

@route(PREFIX + "/pageepisodes")
def PageEpisodes(title, url):

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
				thumb = R(ICON_SERIES),
				summary = "Watch " + season_title + " of " + title + " in HD now from G2G.fm!"
				)
			)

	for each in eps_list:
		ep_url = BASE_URL + "/forum/" + each.xpath("./@href")[0]
		ep_title = each.xpath("./text()")[0]
	
		if ep_title.find("Season Download") < 1:
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = ep_title.rsplit(" Streaming",1)[0].rsplit(" Download",1)[0], url = ep_url),
				title = ep_title.rsplit(" Streaming",1)[0].rsplit(" Download",1)[0],
				thumb = R(ICON_LIST),
				summary = "Watch " + ep_title.rsplit(" Streaming",1)[0].rsplit(" Download",1)[0] + " now in HD from G2G.fm!"
				)
			)

	return oc
	
######################################################################################
# Gets metadata and google docs link from episode page. Checks for trailer availablity.

@route(PREFIX + "/episodedetail")
def EpisodeDetail(title, url):
	
	oc = ObjectContainer(title1 = title)
	page_data = HTML.ElementFromURL(url)
	title = page_data.xpath("//title/text()")[0].rsplit(" Streaming",1)[0].rsplit(" Download",1)[0]
	thumb = page_data.xpath("//blockquote[@class='postcontent restore']//div/img/@src")[0]

	#load recursive iframes to find google docs url
	first_frame_url = page_data.xpath("//blockquote/div/iframe/@src")[0]
	first_frame_data = HTML.ElementFromString(HTTP.Request(first_frame_url, headers={'referer':url}))
	second_frame_url = first_frame_data.xpath("//iframe/@src")[0]
	second_frame_data = HTML.ElementFromString(HTTP.Request(second_frame_url, headers={'referer':first_frame_url}))
	final_frame_url = second_frame_data.xpath("//iframe/@src")[0]
	
	oc.add(VideoClipObject(
		url = final_frame_url,
		thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png'),
		title = title,
		summary = "Watch " + title + " now in HD from G2G.fm!"
		)
	)

	if len(page_data.xpath("//iframe[@class='restrain']/@src")) > 0:	
		trailer_url = page_data.xpath("//iframe[@class='restrain']/@src")[0].split("?",1)[0].replace("//www.youtube.com/embed/", "http://www.youtube.com/watch?v=")
		oc.add(VideoClipObject(
			url = trailer_url,
			thumb = R(ICON_SERIES),
			title = "Watch Trailer",
			summary = "Watch the trailer for " + title + " now on YouTube."
			)
		)
	
	#provide a way to add to favourites list
	oc.add(DirectoryObject(
		key = Callback(AddBookmark, title = title, url = url),
		title = "Bookmark Video",
		summary = "You can add " + title + " to your Bookmarks list, to make it easier to find later.",
		thumb = R(ICON_QUEUE)
		)
	)	
	
	return oc
	
######################################################################################
# Loads bookmarked shows from Dict.  Titles are used as keys to store the show urls.

@route(PREFIX + "/bookmarks")	
def Bookmarks(title):

	oc = ObjectContainer(title1 = title)
	
	for each in Dict:
		url = Dict[each]
		page_data = HTML.ElementFromURL(url)
		title = each
		thumb = page_data.xpath("//blockquote[@class='postcontent restore']/div/img/@src")[0]
		
		oc.add(DirectoryObject(
			key = Callback(EpisodeDetail, title = title, url = url),
			title = title,
			thumb = Resource.ContentsOfURLWithFallback(url = thumb, fallback='icon-cover.png'),
			summary = "Watch " + title + " now in HD from G2G.fm!"
			)
		)
	
	#add a way to clear bookmarks list
	oc.add(DirectoryObject(
		key = Callback(ClearBookmarks),
		title = "Clear Bookmarks",
		thumb = R(ICON_QUEUE),
		summary = "CAUTION! This will clear your entire bookmark list!"
		)
	)
	
	return oc
	
######################################################################################
# Adds a show to the bookmarks list using the title as a key for the url
	
@route(PREFIX + "/addbookmark")
def AddBookmark(title, url):
	
	Dict[title] = url
	Dict.Save()
	return ObjectContainer(header=title, message='This show has been added to your bookmarks.')
	
######################################################################################
# Clears the Dict that stores the bookmarks list
	
@route(PREFIX + "/clearbookmarks")
def ClearBookmarks():

	Dict.Reset()
	return ObjectContainer(header="My Bookmarks", message='Your bookmark list will be cleared soon.')
	
######################################################################################
# Takes query and sets up a http request to return and create objects from results

@route(PREFIX + "/search")	
def Search(query):
		
	oc = ObjectContainer(title1 = query)
	
	for each in HTML.ElementFromURL("http://g2g.fm/tvseries/search.php?q=" + query).xpath("//blockquote/ol/span/b/a"):
		if len(each.xpath("./text()")[0].strip()) > 0:
			title = each.xpath("./text()")[0]
			url = BASE_URL + "/tvseries/" + each.xpath("./@href")[0]
		
			oc.add(DirectoryObject(
				key = Callback(PageEpisodes, title = title, url = url),
				title = title
				)
			)
	
	for each in HTML.ElementFromURL("http://g2g.fm/movies/search.php?q=" + query).xpath("//blockquote/ol/span/b/a"):
		if len(each.xpath("./text()")[0].strip()) > 0:
			title = each.xpath("./text()")[0]
			url = BASE_URL + "/movies/" + each.xpath("./@href")[0]
		
			oc.add(DirectoryObject(
				key = Callback(EpisodeDetail, title = title, url = url),
				title = title
				)
			)
	
	#check for zero results and display error
	if len(oc) < 1:
		Log ("No shows found! Check search query.")
		return ObjectContainer(header="Error", message="Nothing found! Try something less specific.") 
	
	return oc