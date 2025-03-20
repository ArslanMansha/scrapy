import scrapy
import xml.etree.ElementTree as ET


class LowlaundrySpider(scrapy.Spider):
    name = "lowlaundry"
    start_urls = ['https://lowlaundry.com/sitemap.xml']

    def parse(self, response):
        """Default parsing method for URLs from the sitemap"""
        urls = ET.fromstring(response.body).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        for url in urls:
            if 'products_' in url.text:
                yield scrapy.Request(url.text, callback=self.parse_prouct_sitemap)

    def parse_prouct_sitemap(self, response):
        """Parsing method for product sitemaps pages"""
        urls = ET.fromstring(response.body).findall('.//{http://www.sitemaps.org/schemas/sitemap/0.9}loc')
        for url in urls:
            yield scrapy.Request(url.text, callback=self.parse_product_page)

    def parse_product_page(self, response):
        """Parsing method for product pages"""
        # Extract data from each product page
        item = {}
        for p in response.css("div.price-info1>div.price-box").css('p'):
            k = p.css("::attr(class)").get()
            v = p.css("span.price::text").get().strip()
            if not v:
                v = f'{p.css("span.price-currency::text").get()}{p.css("span.price-dollars::text").get()}{p.css("span.price-cents::text").get()}'
            item[k] = v
        desc = "\n".join(response.css("p.MsoNormal::text").getall())
        image = response.css("div.galleria").css("img::attr(src)").get()
        if "placeholder" not in image.lower():
            item['image_urls'] = [image]
        for i, c_o in enumerate(response.css("div.bulleted-callouts__col__label")):
            item[f'bulleted_callout_{i}'] = ''.join(c_o.css(' ::text').getall())
        item['meta_title'] = response.css("title::text").get()
        item['meta_description'] = response.css("meta[name='description']::attr(content)").get()
        item['meta_keywords'] = response.css("meta[name='keywords']::attr(content)").get()
        item['desc'] = desc
        item['url'] = response.url
        item['title'] = (response.css("h1.product-topinfo__product-name::text").get() or "").strip()
        item['ships_from'] = response.css(".loading-after-message ::text").get()
        crumb_info = response.css("div.product-topinfo__product-meta")
        for crumb_div in crumb_info.css("div"):
            k = (crumb_div.css("strong::text").get() or "").strip(": ").lower()
            v = (crumb_div.css("span::text").get() or "").strip()
            item[k] = v
        yield item
