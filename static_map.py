import os, os.path as osp
from abc import ABC, abstractmethod
import numpy as np
from io import BytesIO
from PIL import Image
from urllib import request
from matplotlib import cm as cm, pyplot as plt, colors as mplotcolors

class AbstractAPIReader(ABC):

    @abstractmethod
    def read(self):
        pass

class APIStr(AbstractAPIReader):

    def __init__(self, val):
        self.val = val

    def read(self):
        return self.val


class APIFile(AbstractAPIReader):

    def __init__(self, fname):
        self.fname = fname

    def read(self):
        return str(np.load(self.fname))


class GoogleStaticMap:
    def __init__(self, api_key, zoom=17, size="1024x1024",
                 maptype="satellite", mode="RGB"):
        assert isinstance(api_key, AbstractAPIReader)
        self._api_key = api_key.read()
        self._zoom = zoom
        self._size = size
        self._maptype = maptype
        self._mode = mode

    def read(self, lat, lng):
        return request_image_by_lat_lng(
            lat, lng, zoom=self._zoom, size=self._size,
            maptype=self._maptype, api_key=self._api_key, mode=self._mode)[0]

    def show(self, lat, lng):
        plt.imshow(self.read(lat, lng))
        plt.axis("off")
        return self

    def zoom(self, level):
        self._zoom = level
        return self

    def size(self, size):
        self._size = size
        return self

    def maptype(self, type):
        self._maptype = type
        return self

    def store(self, lat, lng, store_dir, fname=None, storage_format="png"):
        image = request_image_by_lat_lng(
            lat, lng, zoom=self._zoom, size=self._size,
            maptype=self._maptype, api_key=self._api_key, mode=self._mode)[0]
        if fname is None:
            image.save(osp.join(store_dir, self._get_fname(lat, lng, storage_format)))
        else:
            image.save(osp.join(store_dir, fname))
        return self

    def save(self, *args, **kwargs):
        return self.store(*args, **kwargs)

    def _get_fname(self, lat, lng, storage_format="png"):
        return "gmap_{}_zm_{}_sz_{}_m_{}_latlng_{:+024.020f}_{:+025.020f}.{}".format(
            self._maptype, self._zoom, self._size, self._mode, lat, lng, storage_format)

    def read_many(self, lat_list, lng_list):
        staticmap_list = []
        for lat, lng in zip(lat_list, lng_list):
            staticmap_list.append(np.asarray(self.read(lat, lng)))
        return np.asarray(staticmap_list)

    def store_many(self, lat_list, lng_list, store_dir,
                   fname_format="default", prefix="", storage_format="png",
                   fname_fn=lambda prefix, idx, fmt: "{}_{:0{len}d}.{fmt}".format(prefix, idx, len=10, fmt=fmt)):
        assert fname_format in ["default", "prefix_index"]
        for idx, (lat, lng) in enumerate(zip(lat_list, lng_list)):
            if fname_format is "default":
                self.store(lat, lng, store_dir, storage_format=storage_format)
            else:
                self.store(lat, lng, store_dir, fname=fname_fn(prefix, idx, storage_format))
        return self

    def save_many(self, *args, **kwargs):
        return self.store_many(*args, **kwargs)

"""
# Ref: https://stackoverflow.com/questions/7490491/capture-embedded-google-map-image-with-python-without-using-a-browser

url = "http://maps.googleapis.com/maps/api/staticmap?center=-30.027489,-51.229248&size=100x100&zoom=18&sensor=false&maptype=satellite&sensor=false"
buffer = BytesIO(request.urlopen(url).read())
image = Image.open(buffer)
plt.imshow(image)
"""
def request_np_image_by_query(query, zoom=18, size="100x100",
                           maptype="satellite", api_key="", mode="RGB"):
    """
    Adapted from: http://drwelby.net/gstaticmaps/
    center= lat, lon or address
    zoom= 0 to 21
    maptype= roadmap, satellite, hybrid, terrain
    language= language code
    visible= locations
    """
    url = "http://maps.googleapis.com/maps/api/staticmap?center={}&size={}&zoom={}&sensor=false&maptype={}&style=feature%3Aall%7Celement%3Alabels%7Cvisibility%3Aoff&key={}".format(
        query, size, zoom, maptype, api_key)
    img = Image.open(BytesIO(request.urlopen(url).read()))
    return np.array(img.convert(mode)), url


def request_np_image_by_lat_lng(lat, lng, zoom=18,
                             size="100x100", maptype="satellite",
                             api_key="", mode="RGB"):
    return request_image_by_query("{},{}".format(lat, lng),
                                  zoom, size, maptype, api_key, mode)

def request_image_by_query(query, zoom=18, size="100x100",
                           maptype="satellite", api_key="", mode="RGB"):
    """
    Adapted from: http://drwelby.net/gstaticmaps/
    center= lat, lon or address
    zoom= 0 to 21
    maptype= roadmap, satellite, hybrid, terrain
    language= language code
    visible= locations
    """
    url = "http://maps.googleapis.com/maps/api/staticmap?center={}&size={}&zoom={}&sensor=false&maptype={}&style=feature%3Aall%7Celement%3Alabels%7Cvisibility%3Aoff&key={}".format(
        query, size, zoom, maptype, api_key)
    img = Image.open(BytesIO(request.urlopen(url).read()))
    return img.convert(mode), url


def request_image_by_lat_lng(lat, lng, zoom=18,
                             size="100x100", maptype="satellite",
                             api_key="", mode="RGB"):
    return request_image_by_query("{},{}".format(lat, lng),
                                  zoom, size, maptype, api_key, mode)
