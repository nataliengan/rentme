# -*- coding: utf-8 -*-
from scrapy.exceptions import DropItem
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
        else:
            # Rooms listing may not have attributes data, so drop item only if the apartment
            # listing lack attributes
            if spider.name == "apartments":
                raise DropItem('Missing attributes in %s' % item)

        # Parse neighbourhood if provided
        if item['neighborhood']:
                item['neighborhood'] = re.sub('[^\s\w/\.]+', '', ''.join(item['neighborhood'])).rstrip().lstrip()

        # Parse Latitude and Longitude
        if item['location']:
            location_url = urllib.parse.unquote_plus(item['location'])
            location_query = location_url.split('/')[-1]

            # parse depending on query style of Google Map URL ("q=loc:" and "@lat,Lng")
            if "loc:" in location_query:
                address = location_query.split("loc:")[1]
                geo_location = geocoder.google(address)
                if geo_location:
                    latitude = geo_location.lat
                    longitude = geo_location.lng
                    item['latitude'] = latitude
                    item['longitude'] = longitude
                    item['latlng'] = 'POINT(%s %s)' % (latitude, longitude)
                else:
                    raise DropItem('Missing geolocation in %s' % item)
            elif "@" in location_query:
                # "@49.281117,-123.097467,16z" - Remove the @ and convert data to array
                location_attrs = location_query[1:].split(',')
                latitude = location_attrs[0]
                longitude = location_attrs[1]
                item['latitude'] = latitude
                item['longitude'] = longitude
                item['latlng'] = 'POINT(%s %s)' % (latitude, longitude)
            else:
                raise DropItem('Missing location in %s' % item)
        else:
            raise DropItem('Missing location in %s' % item)

        # For Room listings:
        # Parse private_bedroom, private_bathroom
        if item['subattributes']:
            for attr in item['subattributes']:
                if "bath" in attr:
                    if "no" in attr:
                        item["private_bathroom"] = 0
                    else:
                        item["private_bathroom"] = 1
                if "room" in attr:
                    if "no" in attr:
                        item["private_bedroom"] = 0
                    else:
                        item["private_bedroom"] = 1

        return item
