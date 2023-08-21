from tqdm import tqdm

import time

import os

import requests
from lxml import html
from urllib.parse import urljoin, urlparse

def is_valid(url):
    """
    Checks whether `url` is a valid URL.
    """
    parsed = urlparse(url)
    return bool(parsed.netloc) and bool(parsed.scheme)

def get_all_images(url):
    """
    Returns all image URLs on a single `url`
    """
    # make the HTTP request and retrieve response

    # Get the full html code
    #
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Trailer/99.3.7322.23'
    }
    response = requests.get(url, headers=headers)
    html_content = response.text

    # construct the parser
    tree = html.fromstring(html_content)
    urls = []

    # get the Figures Elements form the ListView Page
    figures = tree.xpath('//figure')

    for figure in figures:
        #get all anchor tags in figure
        anchors = figure.xpath('.//a[@class="showcase__link js-detail-data-link"]')
        for anchor in anchors:
            #get link from that anchor to the image
            url_to_img = anchor.get('href')
            if not url_to_img:
                continue

            # Visit the Webpage
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Safari/537.36 Trailer/99.3.7322.23'
            }
            response = requests.get(url_to_img, headers=headers)
            html_content = response.text

            #get whole html of that new sitew
            tree_final_page = html.fromstring(html_content)

            #looking for all img tags on that webpage
            all_img = tree_final_page.xpath('//img[@class="thumb"]')

            # loop through that list of img
            for img in all_img:
                #save here the src-attr-val ...
                img_class_final_url = (img.get('src') or
                                       img.get('data-src') or
                                       img.get('data-original'))
                if not img_class_final_url:
                    # if img does not contain src attribute, just skip
                    continue

                # and put the "base-link" in fron of it
                img_class_final_url = urljoin(url, img_class_final_url)

                #check fro validation and put them in the list of images
                if is_valid(img_class_final_url) and img_class_final_url not in urls:
                    urls.append(img_class_final_url)

    print("urls found: ", urls)
    return urls




def download(url, pathname):
    # if path doesn't exist, make that path dir
    if not os.path.isdir(pathname):
        os.makedirs(pathname)
    # download the body of response by chunk, not immediately
    response = requests.get(url, stream=True)

    # get the total file size
    file_size = int(response.headers.get("Content-Length", 0))

    # get the file name
    filename = os.path.join(pathname, url.split("/")[-1])

    # progress bar, changing the unit to bytes instead of iteration (default by tqdm)
    progress = tqdm(response.iter_content(1024), f"Downloading {filename}", total=file_size, unit="B", unit_scale=True,
                    unit_divisor=1024)

    try:
        with open(filename, "wb") as f:
            print("Downloading Data ...")
            for data in progress.iterable:
                # write data read to the file
                f.write(data)
                # update the progress bar manually
                progress.update(len(data))
    except:
        print(f"Download failed . . .")


def main(url, path):
    # get all images
    imgs = get_all_images(url)
    for img in imgs:
        # for each img, download it
        download(img, path)


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="This script downloads all images from a web page")
    # parser.add_argument("url", help="https://lexica.art/")
    # parser.add_argument("-p", "--path",
    #        help="The Directory you want to store your images, default is the domain of URL passed")

    args = parser.parse_args()
    # url = args.url
    # path = args.path


    index = 1
    while index != 200:
        print("Scanning Webpage", index, ". . .")
        main(f"https://de.freepik.com/search?format=search&page={index}&query=AI+Food",
             r"C:\Users\wired\OneDrive\Desktop\Scrapped\Food")
        index += 1





