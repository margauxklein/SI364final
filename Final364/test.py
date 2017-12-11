import requests


def books_for_search(searchTerm):
	r = requests.get("https://itunes.apple.com/search", params= {"entity" : "ebook", "term" : searchTerm})
	return(r.json()['results'])