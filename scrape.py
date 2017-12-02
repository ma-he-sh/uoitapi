import mechanize
import cookielib
from bs4 import BeautifulSoup
import html2text
import re
import requests
from lxml import html
import requests
import json
import hashlib

#mycampus login url
url = 'https://uoit.ca/mycampus/'

#login request
def login(name, passw, date):

    #spawn a browser
    br = mechanize.Browser()
    cj = cookielib.LWPCookieJar()
    br.set_cookiejar(cj)

    br.open(url)

    soup = BeautifulSoup(br.response().read(), 'lxml')
    html = str(soup)

    #handling the responses
    resp = mechanize.make_response(
        html, [("Content-Type", "text/html")], br.geturl(), 200, "OK"
    )

    br.set_response(resp)
    br.select_form('cplogin')

    #print br

    br.set_handle_equiv(True)
    br.set_handle_redirect(True)
    br.set_handle_referer(True)
    br.set_handle_robots(False) 
    br.form.set_all_readonly(False)

    #login into the mycampus
    br.form.new_control('password', 'pass', {'value': passw})
    br.form.new_control('text', 'user', {'value': name})
    br.form.fixup()
    resp = br.submit()

    
    data = br.response().read()
    soup = BeautifulSoup(data, 'lxml')
    title = soup.find('title')

    if title.text == 'Login Successful':
        br.open('http://portal.mycampus.ca/cp/home/next')
        br.open('http://portal.mycampus.ca/cp/ip/login?sys=sct&url=https://ssbp.mycampus.ca/prod_uoit/twbkwbis.P_GenMenu?name=bmenu.P_RegMnu2')
        br.open('https://ssbp.mycampus.ca/prod_uoit/twbkwbis.P_GenMenu?name=bmenu.P_RegMnu2')

        for link in br.links():
            if (link.text == 'Select Term'):
                print 'found'
                request = br.click_link(link)
                response = br.follow_link(link)

                # submit term
                br.select_form(nr=0)
                br.form.new_control('text', 'term_in', {'value': date})
                br.form.fixup()
                resp = br.submit()
        
        return br, True
    else:
        return br, False

#get student detaile schedule
def get_detsch(user_name, user_pass, strdate):
    #login to uoit mycampus
    br, logged = login(user_name, user_pass, strdate)

    if(logged):
        # goto Student Schedule
        for link in br.links():
            # print link.text
            if (link.text == 'Student Detail Schedule'):
                print 'found'
                request = br.click_link(link)
                response = br.follow_link(link)

        # save file content
        data = br.response().read()

        soup = BeautifulSoup(data, 'lxml')

        # initialize json file
        json_data = {}
        json_data['userid'] = user_name

        # init course data
        course_data = []

        # init var
        course = term = crn = status = instructor = credits = ""

        #go through the tables collecting data
        for tb in soup.findAll('table', {'class': 'bordertable'}):
            
            # get #num captions
            caption = tb.find('caption', {'class': 'captiontext'})

            #print caption.string

            if caption.string == 'Scheduled Meeting Times':
                row = tb.findAll('td', {'class': 'dbdefault'})

                length = len(row)

                schedule = []
                for i in range(0, length):

                    if(i % 7 == 0):
                        sche = {
                            "time": row[i + 1].string.strip(),
                            "days": row[i + 2].string.strip(),
                            "loc": row[i + 3].string.strip(),
                            "date_range": row[i + 4].string.strip(),
                            "sch_type": row[i + 5].string.strip(),
                            "instructor": ''
                        }
                        schedule.append(sche)
                
                course_data.append({"course": course,
                                    "term": term,
                                    "crn": crn,
                                    "instructor": instructor,
                                    "credits": credits,
                                    "schedule": schedule})
            
            else:
                row = tb.findAll('td', {'class': 'dbdefault'})
                course = caption.string.strip()
                term = row[0].string.strip()
                crn = row[1].string.strip()
                status = row[2].string.strip()
                credits = row[4].string.strip()
                instructor = row[3].string.strip('\n')
                if instructor == u'\u00a0':
                    instructor = instructor.replace(u"\u00A0", "TBA")
                

            #save the json file
        json_data['course_data'] = course_data
        savefile = json.dumps(json_data, indent=4)

        return savefile

    else:
        return None