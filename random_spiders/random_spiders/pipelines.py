# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import os
from contextlib import suppress

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request, Response
from scrapy.pipelines.media import FileInfoOrError, MediaPipeline
from typing import TYPE_CHECKING, Any


class RandomSpidersPipeline:
    def process_item(self, item, spider):
        return item


# Optionally, specify image download settings
IMAGES_THUMBS = {
    'small': (50, 50),
    'big': (270, 270),
}


# Custom directory structure for storing images per brand
class BrandImagesPipeline(ImagesPipeline):

    def file_path(self,
                  request: Request,
                  response: Response | None = None,
                  info: MediaPipeline.SpiderInfo | None = None,
                  *,
                  item: Any = None, ):
        # Extract brand name and use it to create a directory for that brand
        brand_name = item.get('brand', 'unknown')
        brand_directory = brand_name.replace(' ', '_').lower()  # Clean up brand name
        image_name = request.url.split('/')[-1]
        ext = image_name.split('.')[-1]
        name = f"{item['part #']}.{ext}"
        if not name:
            name = image_name
        return os.path.join(brand_directory, name)

    def item_completed(
        self, results: list[FileInfoOrError], item: Any, info: MediaPipeline.SpiderInfo
    ) -> Any:
        result = {}
        with suppress(KeyError, IndexError):
            result = results[0][1]  # Only one image is downloaded

        ItemAdapter(item)['image_path'] = result.get('path', '')
        ItemAdapter(item)['image_url'] = result.get('url', '')
        return item
