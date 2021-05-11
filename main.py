import requests
from bs4 import BeautifulSoup as bs
from qbittorrentapi import Client
import os
import json

qb = Client("http://127.0.0.1:8080")
qb.auth_log_in("admin", "adminadmin")
ctr = 0
href2 = ""
select = "div.list-board > ul > li > div.wr-subject.ellipsis > a"
select2 = "div.view-padding > div.view-torrent > table > thead > tr > th > strong"
#analized = open("analized.txt", 'a')
analizeQueue = []
HEADERS = {"Authorization": "Bearer dnCxbrPh9NgjiOmFp5XJtg"}

def buildapiurl(proto="http", host="127.0.0.1", port=8090, action=None):
    if action is None:
        return None
    else:
        return "{0}://{1}:{2}{3}".format(proto, host, port, action)

def submitfile(filepath, data=None):
    global analizeQueue
    if os.path.isdir(filepath):
        for path in os.listdir(filepath):
            path = filepath + "/\"" + path + "\""
            submitfile(path)
    elif os.path.isfile(filepath):
        apiurl = buildapiurl(action="/tasks/create/file")
        with open(filepath, "rb") as sample:
            # multipart_file = {"file": ("temp_file_name", sample)}
            multipart_file = {"file": (os.path.basename(filepath), sample)}
            analizeQueue.append(filepath)
            request = requests.post(apiurl, files=multipart_file, data=data, headers=HEADERS)

def getcuckoostatus():
    apiurl = buildapiurl(action="/cuckoo/status")
    request = requests.get(apiurl, headers=HEADERS)

    jsonreply = json.loads(request.text)
    return jsonreply

def taskslist(limit=None, offset=None):
    baseurl = "/tasks/list"
    if limit is not None:
        baseurl = baseurl+"/"+str(limit)
        if offset is not None:
            baseurl = baseurl+"/"+str(offset)

    apiurl = buildapiurl(action=baseurl)
    request = requests.get(apiurl, headers=HEADERS)
    json.loads(request.text)
    jsonreply = json.loads(request.text)
    return jsonreply

def download(url, file_name):
    with open(file_name, "wb") as file: # open in binary mode
        response = requests.get(url) # get request
        file.write(response.content) # write to file

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
        file = contents['save_path'] + "/\'" + contents['name'] + "/\'"
        if file != '':
            #os.system("cuckoo submit " + "\'" + file + "\'")
            submitfile(file)
            print(file + " submitted")
            #analized.write(contents['name'] + "\t" + contents['hash'])
            qb.torrents.delete(contents['hash'])
"""
    for contents in qb.torrents.info(status_filter="completed"):
        for line in analized.readlines():
            if contents['hash'] == line[1]:
                qb.delete(contents['hash'])
                return
"""
tasklen = 0
for task in taskslist()['tasks']:
    if task['completed_on'] != None:
        tasklen = tasklen + 1

def afterSubmit():
    global tasklen
    global analizeQueue
    tasklen2 = 0
    for task in taskslist()['tasks']:
        if task['completed_on'] != None:
            tasklen2 = tasklen2 + 1
    if tasklen < tasklen2:
        for i in range(0, tasklen2 - tasklen):
            os.system("rm -rf " + "\"" + str(analizeQueue[0]) + "\"")
            print("****" + str(analizeQueue.pop()) + " deleted****")
    tasklen = tasklen2
    if getcuckoostatus()['diskspace']['analyses']['free']/getcuckoostatus()['diskspace']['analyses']['total'] < 0.05:
        os.system("cuckoo clean")


if __name__ == '__main__':
    if "torrents" not in os.listdir():
        os.system("mkdir torrents")
    while 1:
        download_torrent("https://torrentqq85.com/torrent/utl.html?page=", ctr)
        submit()
        afterSubmit()
        ctr = ctr + 1

