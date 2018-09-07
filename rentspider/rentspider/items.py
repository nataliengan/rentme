# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class ApartmentItem(scrapy.Item):
    # url = scrapy.Field()
    price = scrapy.Field()
    attributes = scrapy.Field()
    subattributes = scrapy.Field()
    neighborhood = scrapy.Field()
    location = scrapy.Field()

    bedrooms = scrapy.Field()
    bathrooms = scrapy.Field()
    sqft = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    postal = scrapy.Field()
    pass

class RoomItem(scrapy.Item):
    # url = scrapy.Field()
    price = scrapy.Field()
    attributes = scrapy.Field()
    subattributes = scrapy.Field()
    neighborhood = scrapy.Field()
    location = scrapy.Field()

    private_bedroom = scrapy.Field()
    private_bathroom = scrapy.Field()
    sqft = scrapy.Field()
    latitude = scrapy.Field()
    longitude = scrapy.Field()
    postal = scrapy.Field()
    pass
