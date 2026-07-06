import argparse
import pathlib
from urllib.parse import urlparse, unquote

from bs4 import BeautifulSoup
import requests

VERSION = 0.1

parser = argparse.ArgumentParser(
		prog='khinsider-dl',
		description='downloads khinsider files',
		)

parser.add_argument('url', help='The URL to khinsider song or album')
parser.add_argument('-o', '--outputdir', help='Where you want to store the downloaded music', default='.')

# TODO issue with format:
# stuff like: https://downloads.khinsider.com/game-soundtracks/album/off-macos-windows-gamerip-2008
# has mp3 & ogg... but mp3 is the most common for all songs. sometimes there is flac.
# FOR NOW... let's just comment out format option
#parser.add_argument('-f', '--format', help='formats: mp3, all. \'all\' downloads all avaliable formats', choices=['mp3', 'all'], default='mp3')

args = parser.parse_args()

headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

root_site = 'https://downloads.khinsider.com'

def parse_song_page(url):
	r = requests.get(url, headers=headers)
	

def download_song_link(url):
	# since this site does give some random hash in the url
	# to the direct file link 
	# we have to directly go to the song page each download.

	r = requests.get(url, headers=headers)
	# parse the actual audio files.
	if r.status_code == 200:
		# Now we scrape the song page for Mp3 or whatever format exists.
		soup = BeautifulSoup(r.text, 'html.parser')
		mp3_file = soup.find('audio')
		mp3_file_link = mp3_file['src']
		# TODO use pathlib to make the output dir safe & sane
		#with open('{args.outputdir}{mp3_file_link}') as f:
		with requests.get(mp3_file_link, stream=True) as mp3_response:
			mp3_response.raise_for_status()
			print(f"Downloading: {mp3_file_link}")
			#with open(f'./output{mp3_file_link.split('/', 1)[1]}', 'wb') as f:
			parsed_mp3_url = urlparse(mp3_file_link)
			mp3_url_path = parsed_mp3_url.path
			mp3_url_path = unquote(mp3_url_path) # fix encoding with spaces
			mp3_filename = pathlib.Path(mp3_url_path).name
			output_dir = pathlib.PurePath(args.outputdir).joinpath(mp3_filename)
			with open(output_dir, 'wb') as f:
				for chunk in mp3_response.iter_content(chunk_size=8192):
					f.write(chunk)
			

def main():
	r = requests.get(args.url, headers=headers)
	print(f'HTTP Code: {r.status_code}')
	soup = BeautifulSoup(r.text, 'html.parser')

	print(f"KHInsider-dl Version {VERSION}")
	print("Note: Only supports Album Pages & Downloading as MP3 (For now...)")

	page_is_song = False
	page_is_album = False

	# check if an album page
	songlist_table = soup.find('table', id='songlist')
	album_song_links = []
	if songlist_table:
		print("Guessing this page is an album page since we found a songlist...")
		page_is_album = True
		# now let's parse the album
		for td in songlist_table.find_all('td', class_='playlistDownloadSong'):
			a_tag = td.find('a', href=True)
			if a_tag:
				album_song_links.append(f'{root_site}{a_tag['href']}')
		#print(album_song_links)
		#album_list.append(i.find_all('href'))
		
	for link in album_song_links:
		download_song_link(link)
	

if __name__ == '__main__':
	main()



