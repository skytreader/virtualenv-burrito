# encoding: utf-8
import os
import urllib.request, urllib.error, urllib.parse
import csv
import hashlib
import json


PYPI_JSON_URL = 'https://pypi.org/pypi/%s/json'

PYPI_DOWNLOADS = {
    # filename: md5sum
    'setuptools-46.4.0.zip': 'e2c6c3d64b38efe2e81bcd502cf54dcc',
    'pip-20.1.1.tar.gz': '62fa8775c44b070c5e1a3f44b0b6ccc5',
    'virtualenv-20.0.26.tar.gz': 'f95dea0cdd84d78d231cafbc6f12a035',
    'virtualenvwrapper-4.8.4.tar.gz': 'b257b16b593eabd7e809cc76e63c295f',
}


def eq_(a, b, msg=None):
    if not a == b:
        raise AssertionError(msg or "%r != %r" % (a, b))


def test_tarball_names():
    tarballs = set()
    with open('versions.csv', 'r') as fo:
        reader = csv.reader(fo)
        for name, version, url, digest in reader:
            if name.startswith('_'):
                continue
            tarballs.add(os.path.basename(url))

    eq_(tarballs, set(PYPI_DOWNLOADS.keys()))


def test_shasum():
    with open('versions.csv', 'r') as fo:
        reader = csv.reader(fo)
        for name, version, url, digest in reader:
            if name.startswith('_'):
                continue
            sha1 = hashlib.sha1()
            sha1.update(urllib.request.urlopen(url).read())
            eq_(digest, sha1.hexdigest())


def test_md5_url_exists():
    for ball, md5sum in PYPI_DOWNLOADS.items():
        if ball.endswith('.zip'):
            filename = ball[:-4]
        else:
            # .tar.gz
            filename = ball[:-7]
        package, release = filename.split('-', 1)
        try:
            data = json.load(urllib.request.urlopen(PYPI_JSON_URL % package))
        except urllib.error.HTTPError as e:
            assert False, "Failed to open %s: %s %s" % (url, type(e), e)

        found = False
        release = data['releases'][release]
        for file in release:
            if file['filename'] == ball:
                assert file['md5_digest'] == md5sum
                found = True
                break

        if not found:
            assert False, 'Missing file %s %s' % (ball, md5sum)
