import functools
from pathlib import Path
from tkinter.ttk import Separator
from typing import Dict
import bs4
from pydantic import BaseModel
import requests
import re
import textwrap

from sympy import content
from tabulate import tabulate

def strip_links(func):
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        result = re.sub(r'\[(\d+| citation needed )\]', '', result, 0, re.MULTILINE)
        if result.strip():
            return result
        return ''
    return wrapper

class WikiParser:
    def __init__(self):
        pass

    @staticmethod
    def get_text(element) -> str:
        result = re.sub(r'\s+',' ', element.get_text(strip=True, separator=" "))
        if result.strip():
            return result
        return ''

    @strip_links
    def parse_p(self, element: bs4.element.Tag) -> str:
        if element.find('span', {'class':'tooltip-metadata'}):
            return ''
        return self.get_text(element)+'\n'

    @strip_links
    def parse_h(self, element: bs4.element.Tag) -> str:
        return '#'*int(element.name[1])+' '+re.sub(r'\[.*?\]','',self.get_text(element))+'\n'

    @strip_links
    def parse_ul(self, element: bs4.element.Tag) -> str:
        content = ''

        for child in element.children:
            if isinstance(child, bs4.element.Tag):
                inner_children = list(child.children)

                if isinstance(inner_children[-1], bs4.element.Tag) and inner_children[-1].name == 'ul':
                    segment = self.parse_ul(inner_children[-1])

                    segment = textwrap.indent(segment, '\t')

                    content += '- '+' '.join([self.get_text(ele) for ele in inner_children[:-1]])+'\n'
                    content += segment
                elif isinstance(inner_children[0], bs4.element.Tag):
                    if inner_children[0].name in ['p', 'a']:
                        content += '- '+self.get_text(child)+'\n'
                elif isinstance(inner_children[0], bs4.element.NavigableString) and self.get_text(inner_children[0]):
                    content += '- '+self.get_text(child)+'\n'

        return content
    
    @strip_links
    def parse_ol(self, element: bs4.element.Tag) -> str:
        content = ''
        print(element)

        index = 1
        for child in element.children:
            if isinstance(child, bs4.element.Tag):
                inner_children = list(child.children)

                if isinstance(inner_children[-1], bs4.element.Tag) and inner_children[-1].name == 'ol':
                    segment = self.parse_ol(inner_children[-1])

                    segment = textwrap.indent(segment, '\t')

                    content += f'{index}. '+' '.join([self.get_text(ele) for ele in inner_children[:-1]])+'\n'
                    content += segment
                    index += 1
                elif isinstance(inner_children[0], bs4.element.Tag):
                    if inner_children[0].name in ['p', 'a']:
                        content += f'{index}. '+self.get_text(child)+'\n'
                        index += 1
                elif isinstance(inner_children[0], bs4.element.NavigableString) and self.get_text(inner_children[0]):
                    content += f'{index}. '+self.get_text(child)+'\n'
                    index += 1

        return content

    def parse_table(self, element: bs4.element.Tag) -> str:
        tables = []

        for tr in element.find_all('tr'):
            ths = list(tr.find_all('th'))
            tds = list(tr.find_all('td'))
            if ths:
                tables.append({'headers':[self.get_text(th) for th in ths], 'data': []})
            else:
                if len(tables) == 0:
                    tables.append({'headers':'', 'data':[]})
                tables[-1]['data'].append([self.get_text(td) for td in tds])
        
        return '\n\n'.join([tabulate(table['data'], table['headers'], tablefmt='pipe') for table in tables])+'\n'
    
    def parse_tabbertab(self, element: bs4.element.Tag, indent=0) -> str:
        content = f'####{"#"*indent} {element.attrs['data-title']}\n'

        inner_tabber = element.find('div', {'class':'tabber'})

        if inner_tabber:
            return content + self.parse_tabber(inner_tabber, indent=indent+1)
        else:
            return content + self.parse_table(element.find('table'))

    
    def parse_tabber(self, element: bs4.element.Tag, indent=0) -> str:
        segments = []

        for tab in element.find_all('div', {'class': 'tabbertab'}):
            segments.append(self.parse_tabbertab(tab, indent=indent))
        
        return '\n'.join(segments)+'\n'

    def parse_infobox(self, element: bs4.element.Tag) -> str:
        content = f"## {self.get_text(element.find('div', {'class':'title'}))} Infobox\n"

        segments = []

        for group in element.find_all('div', {'class':'group'}):
            header = group.find('div', {'class':'header'})

            if header:
                if self.get_text(header) == 'Official Drop Tables':
                    continue

                data = []
                is_table = True

                for div in group.children:
                    if isinstance(div, bs4.element.Tag):
                        if 'row' in div.attrs['class']:
                            label = div.find('div', {'class':'label'})
                            value = self.get_text(div.find('div', {'class':'value'}))
                            if label:
                                data.append([
                                    self.get_text(label),
                                    value,
                                ])
                            else:
                                is_table = False
                                data = value
                        elif 'header' in div.attrs['class']:
                            data = []
                            is_table = True

                if is_table:
                    segment = tabulate(data, tablefmt='pipe')+'\n'
                else:
                    segment = data + '\n'

                if segment.strip():
                    segments.append(
                        f"### {self.get_text(header)}\n"
                        +segment
                    ) 

        content += '\n' + '\n'.join(segments) +'\n'

        content += '## End Infobox\n'

        return content

    def replace_polarity(self, soup: bs4.BeautifulSoup) -> bs4.BeautifulSoup:
        for img in soup.find_all('img', {'class':'mw-file-element'}):
            match = re.match(r'^/images/(.*?)_Pol.*$', img.attrs['src'])
            if match:
                polarity:str = match.group(1).lower()
                img.replace_with(f'[{polarity}]')
        return soup
    
    def parse_url(self, url: str) -> str:
        return self.parse_html(html = requests.get(url).content)

    def parse_html(self, html: str) -> str:
        soup = bs4.BeautifulSoup(html, 'html5lib')
        return self.parse_soup(soup)

    def parse_soup(self, soup: bs4.BeautifulSoup) -> str:
        soup = self.replace_polarity(soup)
        html_content = soup.find('div', attrs={'class': 'mw-parser-output'})
        segments = []
        last_heading = ''
        for element in html_content.children:
            if isinstance(element, bs4.element.Tag):
                segment = ''
                heading = False
                if element.name == 'p':
                    segment = self.parse_p(element)
                elif element.name.startswith('h'):
                    heading = True
                    segment = self.parse_h(element)
                elif element.name == 'ul':
                    segment = self.parse_ul(element)
                elif element.name == 'ol':
                    segment = self.parse_ol(element)
                elif element.name == 'table':
                    ignore = ['template-quote-table', 'navbox']
                    valid = True
                    if 'class' in element.attrs:
                        for ig in ignore:
                            if ig in element.attrs['class']:
                                valid = False
                    if valid:
                        segment = self.parse_table(element)
                elif element.name == 'div':
                    if 'class' in element.attrs:
                        if 'tabber' in element.attrs['class']:
                            segment = self.parse_tabber(element)
                        elif 'infobox' in element.attrs['class']:
                            segment = self.parse_infobox(element)
                    else:
                        if table:=element.find('table'):
                            segment = self.parse_table(table)

                if segment:
                    if last_heading != '':
                        if heading:
                            last_heading = segment
                            segment = ''
                        else:
                            segment = last_heading+'\n'+segment
                            last_heading = ''
                    else:
                        if heading:
                            last_heading = segment
                            segment = ''

                if segment:
                    segments.append(segment)

        return '\n'.join(segments)


if __name__ == '__main__':
    print(WikiParser().parse_url("https://wiki.warframe.com/w/Volt%2FPrime"), end='')