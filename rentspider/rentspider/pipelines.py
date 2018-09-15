# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem
from scrapy.exporters import CsvItemExporter
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from settings import FEED_EXPORT_FIELDS, EXPORT_DIRECTORY_NAME
from constants import AREAS, POSTAL_MAP
from os import mkdir, getcwd, path
from shutil import rmtree

import pathlib
import re
import urllib.parse
import geocoder

class RentspiderPipeline(object):
    def process_item(self, item, spider):
        # Parse rental price
        if item['price']:
            # remove dollar sign
            item['price'] = int(item['price'][1:])
        else:
            raise DropItem('Missing price in %s' % item)

        # Parse Bedrooms, Bathrooms, Sqft
        if item['attributes']:
            for attr in item['attributes']:
                if "BR" in attr:
                    item['bedrooms'] = float(''.join(re.findall('\d+\.*\d*', attr)))
                elif "Ba" in attr:
                    item['bathrooms'] = float(''.join(re.findall('\d+\.*\d*', attr)))
                else:
                    item['sqft'] = int(attr)
            # if no Bedrooms or bathrooms data, then leave blank

        # For Room listings:
        # Parse private_bedroom, private_bathroom
        item['furnished'] = 0
        item['laundry'] = 0
        if item['subattributes']:
            for attr in item['subattributes']:
                # get private BR/Ba info only for room listings
                if spider.name == "rooms":
                    if "private bath" in attr:
                        if "no" in attr:
                            item["private_bathroom"] = 0
                        else:
                            item["private_bathroom"] = 1
                    if "private room" in attr:
                        if "no" in attr:
                            item["private_bedroom"] = 0
                        else:
                            item["private_bedroom"] = 1

                # get furnished info for apartments AND rooms (default = 0)
                if "furnished" in attr and "no" not in attr:
                    item["furnished"] = 1

                # get laundry info for apartments AND rooms (default = 0)
                if ("w/d" in attr) or ("laundry" in attr):
                    if "unit" in attr:
                        item['laundry'] = 3
                    elif "bldg" in attr:
                        item['laundry'] = 2
                    elif "site" in attr and "no" not in attr:
                        item['laundry'] = 1

        # Parse neighbourhood if provided
        if item['neighborhood']:
            item['neighborhood'] = re.sub('[^\s\w/\.]+', '', ''.join(item['neighborhood'])).rstrip().lstrip()

        # Parse Latitude, Longitude, Postal code
        if item['location']:
            location_url = urllib.parse.unquote_plus(item['location'])
            location_query = location_url.split('/')[-1]

            # Parse implementation depend on query style of Google Map URL ("q=loc:" and "@lat,Lng")
            if "loc:" in location_query:
                address = location_query.split("loc:")[1]
                geo_location = geocoder.google(address)
                if geo_location:
                    latitude = geo_location.lat
                    longitude = geo_location.lng
                    item['latitude'] = latitude
                    item['longitude'] = longitude
                    postal = self.get_postal_code(item['latitude'], item['longitude'])
                    if postal:
                        item['postal'] = postal
                    else:
                        raise DropItem('Missing postal code in %s' % item)
                else:
                    raise DropItem('Missing geolocation in %s' % item)
            elif "@" in location_query:
                # "@49.281117,-123.097467,16z" - Remove the @ and convert data to array
                location_attrs = location_query[1:].split(',')
                latitude = location_attrs[0]
                longitude = location_attrs[1]
                item['latitude'] = latitude
                item['longitude'] = longitude
                postal = self.get_postal_code(item['latitude'], item['longitude'])
                if postal:
                        item['postal'] = postal
                else:
                    raise DropItem('Missing postal code in %s' % item)
            else:
                raise DropItem('Missing location in %s' % item)
        else:
            raise DropItem('Missing location in %s' % item)

        return item

    def get_postal_code(self, lat, lng):
        return geocoder.google([lat,lng], method='reverse').postal

class MultiCSVItemPipeline(object):
    def __init__(self):
        dispatcher.connect(self.spider_opened, signal=signals.spider_opened)
        dispatcher.connect(self.spider_closed, signal=signals.spider_closed)

    def spider_opened(self, spider):
        export_dir = spider.name + '_' + EXPORT_DIRECTORY_NAME
        export_path = getcwd() + '/' + export_dir + '/'

        # Replace existing exports
        if path.exists(export_dir):
            rmtree(export_dir)
        mkdir(export_dir)

        self.files = dict([ (name, open(export_path+name+'.csv','w+b')) for name in AREAS ])
        self.exporters = dict([ (name,CsvItemExporter(self.files[name])) for name in AREAS])
        for e in self.exporters.values():
            e.fields_to_export = FEED_EXPORT_FIELDS
        [e.start_exporting() for e in self.exporters.values()]

    def spider_closed(self, spider):
        [e.finish_exporting() for e in self.exporters.values()]
        [f.close() for f in self.files.values()]

    def process_item(self, item, spider):
        area = self.postal_to_area(item['postal'])

        if area in set(AREAS):
            # Only export item if it is located in an area
            self.exporters[area].export_item(item)
        return item

    def postal_to_area(self, postal):
        # Get first 3 character of postal code to identify area
        prefix = postal.split(' ')[0]
        return POSTAL_MAP[prefix]
