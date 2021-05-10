import requests
from bs4 import BeautifulSoup as bs
from qbittorrentapi import Client
import os

qb = Client("http://127.0.0.1:8080")
qb.auth_log_in("admin", "adminadmin")
ctr = 80
href2 = ""
select = "div.list-board > ul > li > div.wr-subject.ellipsis > a"
select2 = "div.view-padding > div.view-torrent > table > thead > tr > th > strong"
analized = open("analized.txt", 'a')

def download(url, file_name):
    with open(file_name, "wb") as file:   # open in binary mode
        response = requests.get(url)               # get request
        file.write(response.content)      # write to file

def download_torrent(main, ctr):
    main = main + str(ctr)
    req = requests.get(main)
    html = req.text

    soup = bs(html, 'html.parser')
    href = soup.find_all("a", class_="font-13 en")
    for a in href:
        url = a.attrs['href']
        req = requests.get(url)
        if req.status_code != 200:
            continue
        html2 = req.text

        soup2 = bs(html2, 'html.parser')
        if soup2.select_one(select2):
            name2 = soup2.select_one(select2).get_text()
        else:
            break

        href2 = soup2.find("a", class_="btn-torrent").attrs['href']
        link2 = "https://torrentqq84.com" + href2
        print(link2)
        req2 = requests.get(link2)
        if req2.text == '':
            continue
        torrent = name2 + ".torrent"
        print(torrent)
        if requests.get(link2).status_code != 200:
            continue
        download(link2, torrent)
        if torrent != None:
            qb.torrents.add(torrent_files=torrent)
            os.system("mv \"" + torrent + "\" torrents/\"" + torrent + "\"")
            print(name2 + " download start")
        submit()
def submit():
    for contents in qb.torrents.info(status_filter="completed"):
        print(contents)
        file = contents['save_path'] + contents['name']
        if file != '':
            os.system("cuckoo submit " + "\'" + file + "\'")
            print(file + " submitted")
            analized.write(contents['name'] + "\t" + contents['hash'])
            qb.torrents.delete(contents['hash'])
            #### before anal, it will be deleted. so need to get info that fin anal from cuckoo
            ### maybe taskID can help this case
            os.system("rm -rf " + "\'" + file + "\'")
            print(file + "deleted")
    for contents in qb.torrents.info(status_filter="completed"):
        for line in analized.readlines():
            if contents['hash'] == line[1]:
                qb.delete(contents['hash'])
                return

if __name__ == '__main__':
    download_torrent("https://torrentqq85.com/torrent/utl.html?page=", ctr)
    ctr = ctr + 1
    while href2 != None:
        download_torrent("https://torrentqq85.com/torrent/utl.html?page=", ctr)
        ctr = ctr + 1

