#!/usr/bin/python3

from bs4 import BeautifulSoup
from requests import get
from requests.exceptions import RequestException
from contextlib import closing
import sys, os

headers = {
	"User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/67.0.3396.79 Safari/537.36"
}

def make_url_metro(song_title, artist_name):
	return 'http://www.metrolyrics.com/' + song_title.replace(' ', '-') + '-lyrics-' + artist_name.replace(' ', '-')

def make_url_az(song_title, artist_name):
	return f'https://www.azlyrics.com/lyrics/{artist_name}/{song_title}.html'


def simple_get(url):
	try:
		with closing(get(url, headers=headers)) as resp:
			# print(resp.status_code, resp.history)
			if resp.status_code == 200:
				if not resp.history:
					return resp.content
				elif resp.history[0].status_code == 301:
					return resp.content
				else:
					print('Redirection -> 302: lyrics not found!')
					return None
			else:
				print('Err -> 404: lyrics not found!')
				return None

	except RequestException:
		print('Internet connection is needed to download the lyrics')
		return None


def lyricsFinderMetro(song_title, artist_name):
	url = make_url_metro(song_title.strip(), artist_name.strip())
	raw_html = simple_get(url)
	if raw_html is None:
		print('lyrics Not Found.')
		return None

	html = BeautifulSoup(raw_html, 'html.parser')
	
	lyrics = ''

	for p in html.select('p'):
		s = [str(i) for i in p.contents]
		s = ''.join(s)
		s = s.replace('<br/>', '<br><br>')
		if p.has_attr('class') and p['class'][0] == 'verse':
			lyrics += '♪ \033[1;32;40m {} ♪ \n\n'.format(p.text)

	return lyrics

def lyricsFinderAz(song_title, artist_name):
	song_title = song_title.replace("'", "")
	song_title = ''.join(song_title.strip().lower().split())
	artist_name = ''.join(artist_name.strip().lower().split())
	print(song_title, artist_name)
	url = make_url_az(song_title, artist_name)
	raw_html = simple_get(url)
	if raw_html is None:
		print('lyrics Not Found.')
		return None

	html = BeautifulSoup(raw_html, 'html.parser')

	lyrics = ''
	for div in html.select('div'):
		if not div.has_attr('class'):
			lyrics = '♪♪♪ \033[1;32;40m {} ♪♪♪'.format(str(div.text))
	return lyrics



def lyrics_file_check(fname):

	try:
		with open(fname, 'r') as f:
			# print(f.read())
			for line in f:
				print(line)
		return True

	except FileNotFoundError:
		return False

if __name__ == '__main__':
	if not os.path.exists('downloaded_lyrics'):
		os.makedirs('downloaded_lyrics')
	dir_path = os.path.dirname(os.path.realpath(__file__))
	fname = f'{dir_path}/downloaded_lyrics/' + sys.argv[1] + '-' + sys.argv[2] + '.txt'

	if len(sys.argv) != 3:
		print("Usage: python3 song_title artist_name")
		sys.exit()
	if not lyrics_file_check(fname):
		azlyrics = lyricsFinderAz(sys.argv[1], sys.argv[2])
		if azlyrics:
			print(azlyrics)
			f = open(fname, 'w')
			f.write(azlyrics)
		else:
			metrolyrics = lyricsFinderMetro(sys.argv[1], sys.argv[2])
			if metrolyrics:
				print(metrolyrics)
				f = open(fname, 'w')
				f.write(metrolyrics)
			else:
				sys.exit()