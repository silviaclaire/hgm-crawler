import os
import sys
import re
import requests
from lxml import etree


class HGMCrawler():

    source_url = 'https://www.aisei.co.jp/magazine/'
    save_dir = os.path.expanduser('~') + '/Dropbox/HGM'
    href_ptn = re.compile(r"<a href=\"(\S+)\?")
    dl_url_prefix = 'https://www.aisei.co.jp/hubfs'

    def get_urls(self):
        content = requests.get(self.source_url).text
        tree = etree.HTML(content)

        latest_elm = tree.xpath("//*[@id='coverImg'][1]/a")[0]
        m = self.href_ptn.match(etree.tostring(latest_elm).decode('utf8'))
        latest = [m.group(1)]

        past_elms = tree.xpath("//*[@class='magazineList cf']/li/div/a")
        past = []
        for ele in past_elms:
            m = self.href_ptn.match(etree.tostring(ele).decode('utf8'))
            past.append(m.group(1))

        return latest, past

    def get_all_pdfs(self):
        latest, past = self.get_urls()
        self.download_file(latest + past)
    
    def get_latest_pdfs(self):
        latest, _ = self.get_urls()
        self.download_file(latest)

    def download_file(self, urls : list):
        os.makedirs(self.save_dir, exist_ok=True)
        n_urls = len(urls)

        for i, url in enumerate(urls):
            filename = url[url.rfind('/')+1:]
            filepath = os.path.join(self.save_dir, filename)

            if os.path.exists(filepath):
                print(f'Skipped: {filename} already exists')
                continue

            r = requests.get(self.dl_url_prefix + url)
            with open(filepath, 'wb') as f:
                f.write(r.content)
            print(f'Downloaded: {filename} ({i+1} of {n_urls})')


def help():
    print("""
        options:
        -a, --all       Get all publications
        -l, --latest    Get latest publication only
    """)


if __name__ == "__main__":

    if len(sys.argv) != 2:
        help()
        exit(0)

    if sys.argv[1] == '-a':
        HGMCrawler().get_all_pdfs()
    elif sys.argv[1] == '-l':
        HGMCrawler().get_latest_pdfs()
    else:
        help()
        exit(0)
