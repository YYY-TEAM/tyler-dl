# -*- coding: utf-8 -*-

import requests
import lxml.html
from collections import defaultdict
import re
import os
import argparse
import sys
import time

# -- Sidebar with lecture infos on course page:
# - div class="row lecture-sidebar"
# -- div class="col-sm-12 course-section" --> loop elements
# --- div class="section-title" ==> SECTION TITLE
# --- ul class="section-list"
# ---- li class="section-item" --> loop elements
# ----- a class="item" -> href ==> LECTURE LINK
# ------ div class="title-container"
# ------- span class="lecture-icon"
# -------- i class="fa fa-file-text" OR i class="fa fa-youtube-play" ==> TYPE
# ------- span class="lecture-name" ==> NAME

# dict = {
#     'SECTION_TITLE': [
#         {
#             'lecture_title': 'TITLE',
#             'lecture_url': 'URL',
#             'lecture_type': 'TYPE'
#         },
#         {
#             '...': '...'
#         }
#     ]
# }


def get_lecture_list(session, url):
    # Return a dictionary for this course:
    # dict = {
    #     'SECTION_TITLE': [
    #         {
    #             'lecture_title': 'TITLE',
    #             'lecture_url': 'URL',
    #             'lecture_type': 'TYPE'
    #         },
    #         {
    #             '...': '...'
    #         }
    #     ]
    # }

    material = defaultdict(dict)
    base_href = 'https://learn.tylermcginnis.com'

    content = session.get(url)
    doc = lxml.html.fromstring(content.text)
    sidebar = doc.find_class('row lecture-sidebar')[0]
    num = 1
    for section in sidebar.find_class('col-sm-12 course-section'):
        section_title = section.find_class(
            'section-title')[0].text_content().strip()
        section_title = re.sub('[\/:*?"<>|]', '', section_title)
        if num < 10:
            numstr = '0' + str(num)
        else:
            numstr = str(num)
        section_title = numstr + ' - ' + section_title
        material[section_title] = list()

        for section_item in section.find_class('section-item'):
            for link in section_item.find_class('item'):
                temp_dict = defaultdict()

                link.make_links_absolute(base_href, resolve_base_href=True)
                temp_dict['lecture_url'] = link.attrib['href']

                lecture_title = link.find_class(
                    'lecture-name')[0].text_content().strip()
                lecture_title = re.sub(r'\(.*\)', '', lecture_title).strip()
                lecture_title = re.sub('[\/:*?"<>|]', '', lecture_title)
                if ': ' in lecture_title:
                    lecture_title = lecture_title.split(': ', 1)[1]
                temp_dict['lecture_title'] = lecture_title

                lecture_type = link.find_class('lecture-icon')[0]
                if lecture_type.find_class('fa fa-file-text'):
                    lecture_type_index = 'text'
                elif lecture_type.find_class('fa fa-youtube-play'):
                    lecture_type_index = 'video'
                else:
                    lecture_type_index = 'unknown'
                temp_dict['lecture_type'] = lecture_type_index

                material[section_title].append(temp_dict)
        num += 1

    return material


def get_video(session, url, title, dir):
    r = session.get(url, stream=True)

    for line in r.iter_lines():
        if 'data-wistia-id=' in line:
            id = line.split('data-wistia-id=')[1].split(' ')[0].strip("'")
            video_source_url = 'https://fast.wistia.com/embed/medias/' + \
                id + '.json'
            response_videos = requests.get(video_source_url)
            videos = response_videos.json()

            for item in videos['media']['assets']:
                if item['type'] == 'hd_mp4_video' and item['display_name'] == '720p':
                    video_file = item['url'].split('.bin')[0] + '.mp4'
                    filename = os.path.join(dir, title + '.mp4')
                    with open(filename, 'wb') as fout:
                        print 'Downloading ' + title + ' ...'
                        fout.write(requests.get(video_file).content)


def get_text(session, url, title, dir):
    r = session.get(url, stream=True)
    doc = lxml.html.fromstring(r.text)
    # maintext = doc.find_class('lecture-text-container')[0].text_content()
    maintext = doc.find_class(
        'lecture-attachment')[0].text_content().strip().encode('utf-8')
    filename = os.path.join(dir, title + '.txt')
    with open(filename, 'w') as fout:
        print 'Downloading ' + title + ' ...'
        fout.write(maintext)


def parse_args():
    parser = argparse.ArgumentParser(
        description='Download video and text materials from Tyler McGinnis courses. You can chose the course form a menue.')
    parser.add_argument('-u', '--username', type=str,
                        help='Log-in username', required=True)
    parser.add_argument('-p', '--password', type=str,
                        help='Log-in password', required=True)
    parser.add_argument(
        '-o', '--output', help='Directory for storing output files')
    parser.add_argument('--version', action='version', version='%(prog)s 1.0')

    parsed_args = parser.parse_args()

    return parsed_args


def main(args):
    courses = [
        {'id': 1,
         'name': 'Modern Javascript',
         'url': 'https://learn.tylermcginnis.com/courses/51206/lectures/3167266'
         },
        {'id': 2,
         'name': 'React Fundamentals',
         'url': 'https://learn.tylermcginnis.com/courses/50507/lectures/821020'
         },
        {'id': 3,
         'name': 'Redux',
         'url': 'https://learn.tylermcginnis.com/courses/294390/lectures/4577049'
         },
        {'id': 4,
         'name': 'React Router',
         'url': 'https://learn.tylermcginnis.com/courses/147194/lectures/4055234'
         },
        {'id': 5,
         'name': 'React Native',
         'url': 'https://learn.tylermcginnis.com/courses/51211/lectures/1344368'
         },
        {'id': 6,
         'name': 'Universal React',
         'url': 'https://learn.tylermcginnis.com/courses/51208/lectures/2943472'
         }
    ]

    print 'Which course do you want to download?'
    num_courses = []
    for course in courses:
        print str(course.get('id')) + '\t' + course.get('name')
        num_courses.append(course.get('id'))

    while True:
        try:
            chosen_number = int(raw_input('Please type in the number: '))
        except Exception, e:
            print e
        else:
            if chosen_number in num_courses:
                print 'Start downloading course ...'
                break

    urlLogin = 'https://sso.teachable.com/secure/36750/users/sign_in?flow_school_id=36750'
    with requests.Session() as s:
        login = s.get(urlLogin)
        login_html = lxml.html.fromstring(login.text)
        hidden_inputs = login_html.xpath(r'//form//input[@type="hidden"]')
        payload = {x.attrib['name']: x.attrib['value'] for x in hidden_inputs}
        payload['user[email]'] = args.username
        payload['user[password]'] = args.password
        response = s.post(urlLogin, data=payload)

        defaultdir = os.path.expanduser("~")
        if args.output:
            outdir = args.output
        else:
            outdir = defaultdir

        for course in courses:
            if chosen_number == course.get('id'):
                course_url = course.get('url')
                course_name = course.get('name')

        material = get_lecture_list(s, course_url)

        targetdir = os.path.join(outdir, course_name)
        targetdir = os.path.abspath(targetdir)
        if not os.path.exists(targetdir):
            os.makedirs(targetdir)

        for section, section_info in material.iteritems():
            sectiondir = os.path.join(targetdir, section)
            print '## ' + section
            time.sleep(0.5)
            if not os.path.exists(sectiondir):
                os.mkdir(sectiondir)
            for item in section_info:
                lecture_url = item.get('lecture_url')
                lecture_title = item.get('lecture_title')
                lecture_type = item.get('lecture_type')
                time.sleep(0.5)
                if lecture_type == 'video':
                    get_video(s, lecture_url, lecture_title, sectiondir)
                elif lecture_type == 'text':
                    get_text(s, lecture_url, lecture_title, sectiondir)


if __name__ == '__main__':
    args = parse_args()
    main(args)
