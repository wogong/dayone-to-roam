import re
import json
import yaml
import maya
import click
from typing import *
from pathlib import Path
from nanoid import generate

EMAIL='YOUR_ROAM_EMAIL'
HEADLINE='#dayone'

class DayOneJsonReader:
    def __init__(self, jsonpath: Path) -> None:
        self.jsonpath = jsonpath
        self.jsonobj = None

    def read(self):
        with self.jsonpath.open('r') as f:
            self.jsonobj = json.load(f)

        # Simple validation
        assert tuple(self.jsonobj.keys()) == ('metadata', 'entries')
        assert self.jsonobj.get('metadata').get('version') == '1.0'
        return self

    def __call__(self) -> Dict[str, Union[Dict, List, Any]]:
        if self.jsonobj is not None:
            return self.jsonobj
        else:
            raise AttributeError('Read json file first.')

    @property
    def entries(self):
        return self.jsonobj['entries']


class EntryConverter:
    def __init__(self, entry: Dict[str, Any]) -> None:
        self.metadata = entry
        self.text = self.metadata.pop('text')
        self.converted: Union[str, None] = None
        self.create_time = self._create_time()
        self.edit_time = self._edit_time()
        self.title = self._title()
        self.rrjson = {
            "create-email": EMAIL,
            "create-time": 0,
            "title": '',
            "children": [
                {
                    "string": HEADLINE,
                    "create-email": EMAIL,
                    "create-time": 0,
                    "children": [
                        {
                            "string": '',
                            "create-email": EMAIL,
                            "create-time": 0,
                            "uid": '',
                            "edit-time": 0,
                            "edit-email": EMAIL
                        }
                    ],
                    "uid": '',
                    "edit-time": 0,
                    "edit-email": EMAIL
                }
            ],
            "uid": '',
            "edit-time": 0,
            "edit-email": EMAIL
        }
        assert self.metadata.get('text') is None

    def _creation_date(self) -> str:
        """Format creationDate string using maya, to make datetime string macos friendly"""
        return maya.parse(self.metadata.get('creationDate')).iso8601().replace(':', '')

    def _title(self) -> str:
        """Format creationDate string using maya, to make datetime string macos friendly"""
        month_dict = ["", "January",
                      "February",
                      "March",
                      "April",
                      "May",
                      "June",
                      "July",
                      "August",
                      "September",
                      "October",
                      "November",
                      "December"]
        date = maya.parse(self.metadata.get('creationDate'))
        return month_dict[date.month] + ' ' + str(date.day) + self.suffix(date.day) + ', ' + str(date.year)

    def suffix(self, d):
        return 'th' if 11 <= d <= 13 else {1: 'st', 2: 'nd', 3: 'rd'}.get(d % 10, 'th')

    def _create_time(self) -> int:
        """Format creationDate string using maya, to make datetime string macos friendly"""
        return maya.parse(self.metadata.get('creationDate')).epoch * 1000

    def _edit_time(self) -> int:
        """Format creationDate string using maya, to make datetime string macos friendly"""
        try:
            edit_time = maya.parse(self.metadata.get('modifiedDate')).epoch * 1000
        except:
            edit_time = self.create_time
        return edit_time

    def _format_metadata(self) -> str:
        metadata_string = yaml.dump(self.metadata, allow_unicode=True, default_flow_style=False)
        return metadata_string

    def _replace_image_urls(self):
        image_metadata = self.metadata.get('photos')
        if image_metadata:
            id_to_md5 = {d.get('identifier'): d.get('md5') for d in image_metadata}
            id_to_fileext = {d.get('identifier'): d.get('type') for d in image_metadata}
            for img_id, md5 in id_to_md5.items():
                imageurl = re.compile(f'dayone-moment:\/\/{img_id}')
                if imageurl.search(self.converted) is not None:
                    self.converted = imageurl.sub(f'photos/{md5}.{id_to_fileext.get(img_id, "jpeg")}', self.converted)

    def to_markdown(self, **kwargs) -> Tuple[str, str]:
        if self.text.startswith('#'):
            prefix = ''
        else:
            prefix = '# '
        body = prefix + self.text
        self.converted = f"---\n{self._format_metadata()}\n---\n\n\n{body}\n"
        self._replace_image_urls()
        return (self.creation_date, self.converted)

    def to_rrjson(self, **kwargs) -> Tuple[str, str]:
        if self.text.startswith('#'):
            prefix = ''
        else:
            prefix = '# '
        body = prefix + self.text

        # body
        self.rrjson['children'][0]['children'][0]['string'] = body

        # uid
        self.rrjson['uid'] = generate(size=9)
        self.rrjson['children'][0]['uid'] = generate(size=9)
        self.rrjson['children'][0]['children'][0]['uid'] = generate(size=9)

        # time
        self.rrjson['create-time'] = self.create_time
        self.rrjson['edit-time'] = self.edit_time
        self.rrjson['children'][0]['create-time'] = self.create_time
        self.rrjson['children'][0]['edit-time'] = self.edit_time
        self.rrjson['children'][0]['children'][0]['create-time'] = self.create_time
        self.rrjson['children'][0]['children'][0]['edit-time'] = self.edit_time

        # title
        self.rrjson['title'] = self.title

        #self._replace_image_urls()
        return self.rrjson


@click.command()
@click.argument('jsonpath')
def dayone2rr(jsonpath):
    """Convert *.json exported by DayOne2.app to Roam Research json"""
    reader = DayOneJsonReader(Path(jsonpath))
    entries = reader.read().entries

    converted: List[Dict] = []
    for e in entries:
        try:
            converted.append(EntryConverter(entry=e).to_rrjson())
        except:
            print ('error')
            print (e)

    with open('rrtest.json', "w") as f:
        json.dump(converted, f, ensure_ascii=False)


if __name__ == '__main__':
    dayone2rr()
