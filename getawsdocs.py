#!/usr/bin/env python
"""Download all PDFs from the AWS documentation site."""

from bs4 import BeautifulSoup
import urllib.request
import posixpath
import os
import shutil


def get_services():
    """Create a list of services and make a directory for each."""
    html_page = urllib.request.urlopen("http://aws.amazon.com/documentation/")
    # Parse the documentation home page
    soup = BeautifulSoup(html_page, "html.parser")
    services = []
    # Get all A tags from the parsed page
    for link in soup.findAll('a'):
        try:
            url = link.get('href')
            if url.startswith("/documentation/"):
                # Skip links to self and others
                if not (url.endswith("/documentation/") or
                        url.startswith("/documentation/?nc")):
                    services.append(link.get('href'))
                    # Make directory
                    directory = "." + link.get('href')
                    if not os.path.exists(directory):
                        os.makedirs(directory)
        except:
            continue
    return services


def get_pdfs(services):
    """Download all PDFs from the services URLs."""
    base_url = "http://aws.amazon.com"
    for uri in services:
        # Construct the ful URL for the service page
        url = base_url + uri
        print("\nDownloading PDF's for : " + url + "\n")
        # Parse the HTML page
        try:
            html_page_doc = urllib.request.urlopen(url)
        except:
            continue
        soup_doc = BeautifulSoup(html_page_doc, "html.parser")
        # Get the A tag from the parsed page
        for link in soup_doc.findAll('a'):
            pdf = link.get('href')
            # Check link is a PDF file
            try:
                check = pdf.endswith("pdf")
                if "latest" in pdf:
                    latest = True
                else:
                    latest = False
            except:
                continue
            # Now download if the link is a PDF file
            if check is True and latest is True:
                # We need to work out the file name for saving
                path = urllib.parse.urlsplit(pdf).path
                filename = "." + uri + posixpath.basename(path)
                print("Downloading : " + pdf)
                # Open the URL and retrieve data
                try:
                    web = urllib.request.urlopen(pdf)
                    print("Saving to : " + filename)
                    # Save Data to disk
                    output = open(filename, 'wb')
                    output.write(web.read())
                    output.close()
                except:
                    continue


def rm_empty_dirs(root_dir='documentation'):
    """Remove empty directories."""
    for dirpath, dirs, files in os.walk(root_dir):
        if not dirs and not files:
            os.rmdir(dirpath)


print("Generating list of services...")
services_list = get_services()
print("Downloading PDFs...")
get_pdfs(services_list)
print("Remove services without PDF documentation...")
rm_empty_dirs()
print("Creating ZIP file with all PDFs...")
shutil.make_archive('AWSDocs', 'zip', 'documentation')
print("Finished!")
