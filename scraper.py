import pprint

import requests
from bs4 import BeautifulSoup


def resolve_links_and_comments(table):
    info_list = []
    table_body = table.tbody
    rows_in_table = table_body.find_all('tr')
    for row in rows_in_table:
        try:
            table_data = row.find_all('td')
            yaml_url = table_data[0].find('a').get('href')
            comment = table_data[1].renderContents()
            info_list.append(
                (yaml_url, comment)
            )
        except Exception as e:
            pass
    return info_list


def check_if_table_is_a_subdiv(table_div):
    if table_div.table:
        return table_div.table
    else:
        return ""


def convert_to_raw_url(github_url):
    # https://github.com/dennyzhang/kubernetes-yaml-templates/blob/master/volume/volume-digitalocean.yaml
    # https://raw.githubusercontent.com/dennyzhang/kubernetes-yaml-templates/master/volume/volume-digitalocean.yaml
    new_url = github_url.replace('github.com', 'raw.githubusercontent.com').replace('blob/', '')
    print('Getting the url from' + new_url)
    return new_url


def resolve_file_from_url(file_url):
    code_snippet = requests.get(convert_to_raw_url(file_url))
    soup = BeautifulSoup(code_snippet.content, 'html5lib')
    return soup.get_text()


def resolve_code_block():
    pass


def get_comment(child):
    return child.name == 'p' and len(child.text) > 1


def is_header(child):
    return child.name == 'h2' and len(child.text) > 1


def is_comment(child):
    return child.name == 'p' and len(child.text) > 1


def is_code(child):
    return child.has_attr('class') and 'language-json' in child['class']


def filter_command_codes(child):
    return child.has_attr('class') and 'language-json' in child['class']


class Scraper:
    def __init__(self, url, destination_file_path):
        self.url = url
        self.destination_file_path = destination_file_path

    def scrape(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.content,
                             'html5lib')  # If this line causes an error, run 'pip install html5lib' or install html5lib
        yamls = []
        comments = []
        tables = [i.table for i in soup.find_all('div', 'outline-text-3')]
        tables = filter(None, tables)
        for table in tables:
            for item in resolve_links_and_comments(table):
                yamls.append(item[0])
                comments.append(item[1])
        return yamls, comments

    def execute(self):
        yamls, comments = self.scrape()
        for i in range(len(yamls)):
            print('Yaml File:' + resolve_file_from_url(yamls[i]))
            print(comments[i])
            print('####################################')

    def execute_aws_scraper(self):
        pass

    def scrape_aws(self):
        r = requests.get(self.url)
        soup = BeautifulSoup(r.content,
                             'html5lib')
        commands = []
        comments = []
        properties = {
            "id": "hs_cos_wrapper_module_1588089319145250"
        }
        main_div = soup.find('div', properties)

        # print(main_div)
        children = main_div.findChildren()
        # print([child.has_attr('class') and 'language-json' in child['class'] for child in children])
        filtered = [i.renderContents().decode("utf-8") for i in filter(filter_command_codes, children)]
        print(len(filtered))
        header_found_flag = False
        code_found_flag = False
        comment_found_flag = False

        final_data = {}
        current_header = ''
        current_comment = ''
        for i in range(len(children)):
            if is_header(children[i]):
                current_header = children[i].text
                final_data[current_header] = {}
            # We find a header than keep checking for comment and code until the next header is found
            if is_code(children[i]):
                final_data[current_header][current_comment] = children[i].renderContents().decode("utf-8")
            if is_comment(children[i]):
                current_comment = children[i].text
                final_data[current_header][current_comment] = ''
                # for comment append to comment data structure
        f = open("aws-cli.txt", "w")
        for i, j in final_data.items():
            print('Header = {}'.format(i))
            for k, l in j.items():
                comment = "{}: {}".format(i, k)
                f.write('{} {}\n'.format("#", comment))
                command = ''.join(l)
                f.write(command+'\n')

obj = Scraper("https://www.bluematador.com/learn/aws-cli-cheatsheet", "")
obj.scrape_aws()
# https://www.bluematador.com/learn/aws-cli-cheatsheet
