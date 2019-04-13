# base page: https://champaigncountyclerk.com/elections/results/history
# for web scraping
import requests, bs4
import httplib2

# were are we saving data?
saveFilejson = '/Users/jillnaiman1/champaignElection/election_results.json'

#-----------------------------------------------------------

# for debugging
import sys

w = 'https://champaigncountyclerk.com/elections/results/history'
# see what we have available
# parse
page = requests.get(w)
soup = bs4.BeautifulSoup(page.text, 'html.parser')
soup = str(soup)

# cull
soup2 = soup.split('The following are archived election results for Champaign County')[1]

# split into precents
#soup3 = soup2.split('Precinct Results')


# look for precent ids
soup3 = soup2.split('/elections/results/precinct?ID=')
# loop and grab
soup3 = soup3[1:]
precentNums = []
for s in soup3:
    precentNums.append( s.split('">')[0] )

import re
#>>> re.split('; |, |\*|\n',a)

from datetime import datetime

dates = []
precincts = []
regVoters = []
totalBallotsCast = []
namesOfCandidatesCityCouncil = []
namesOfCandidatesMayor = []
ballotsCastCityCouncil = []
ballotsCastMayor = []
percentagesCastCityCouncil = []
percentagesCastMayor = []
# At Large or At-Large are the champaign wide ones
# mayor?

import re

#electionResults = { 

icount = 0

# go to individual webpages
for p in precentNums:
    # construct w
    #  this is checking to see that there are results for this
    #  particular election date
    w = 'https://champaigncountyclerk.com/elections/results/precinct?ID=' + p
    request = requests.get(w)
    if request.status_code == 200:
        soup = bs4.BeautifulSoup(request.text, 'html.parser')
        soup = str(soup)

        # split by precent links
        soup2 = soup.split('City of Champaign')

        # take out top and bottom
        soup2 = soup2[1:]
        soup2 = soup2[:-1]

        # grab all links for the city of Champaign
        for s2 in soup2:
            w2 = (s2.split('href="')[1]).split('">')[0]
            # whole link
            w2 = 'https://champaigncountyclerk.com/elections/results/' + w2

            # go to this sub website - this is the actual
            #  data page
            #  check it exists too
            request2 = requests.get(w2)
            if request2.status_code == 200:
                soup3 = bs4.BeautifulSoup(request2.text, 'html.parser')
                soup3 = str(soup3)

                # check for elections we want (not primaries)
                # and we want elections where city council was chosen
                # and now we have a tag for *not* general elections either
                continuing = False
                if re.search('General Election', soup3, re.IGNORECASE):
                    continuing = False # nope
                if re.search('Consolidated Election', soup3, re.IGNORECASE):
                    continuing = True
                # search for councel member elections
                if re.search('at large', soup3, re.IGNORECASE):
                    continuing = True
                if re.search('at-large', soup3, re.IGNORECASE):
                    continuing = True
                if not continuing: break

                print('On site: '+ w2)
                
                # split by several delimiters depending on year
                #   ... because of course
                # figure out end characters
                endCharSplit = '\r\n'
                endChar = '\r\n\r\n'
                if soup3.find(endCharSplit) == -1:
                    endCharSplit = '\n'
                    
                xs = re.split(endCharSplit,soup3)

                # this is now the page for individual election results
                icount += 1

                # loop and grab important things
                istart1 = 100000000
                inLoop1 = False
                endLoop1 = False
                inLoop2 = False
                endLoop2 = False
                dateCheck = False
                preCheck = True
                for i,x in enumerate(xs):
                    # has election date?
                    if x.find('RUN TIME') != -1:
                        y = x.split('RUN TIME')[1]
                        if y.find('AM') != -1:
                            d = (y.split('AM')[1]).split()
                        else:
                            d = (y.split('PM')[1]).split()

                        d2 = d[0] +' ' + d[1] + d[2]
                        print('Date of election: ', d2)
                        #s = "8 March, 2017"
                        dt = datetime.strptime(d2, '%B %d,%Y')
                        dates.append(dt)
                        dateCheck = True

                    # this makes sure the date doesn't get over written
                    #  when we grab precincts
                    if dateCheck and preCheck:
                        if re.search('City of Champaign',x,re.IGNORECASE):
                            precincts.append(int(x.split()[-1]))
                            preCheck = False
                    if x.find('REGISTERED VOTERS') != -1:
                        regVoters.append(int(x.split()[-1]))
                    if x.find('BALLOTS CAST - TOTAL') != -1:
                        totalBallotsCast.append(int(x.split()[-1]))
                        istart1 = i
                        # istart1 controls the fact that we only want to
                        #  start looking for mayors/candidates when we've got the
                        #  total infos (and not before)
                    if i > istart1: # now into actual votes
                        # look for openings of where mayor or
                        #  city council is stored
                        if re.search('at large', x, re.IGNORECASE) or re.search('at-large',x,re.IGNORECASE):
                            if not inLoop1:
                                inLoop1 = True
                                namesOfCandidatesMayor.append([])
                                ballotsCastMayor.append([])
                                percentagesCastMayor.append([])
                            # second loop for results of city council stuffs
                            if inLoop1 and endLoop1:
                                inLoop2 = True
                                inLoop1 = False
                                namesOfCandidatesCityCouncil.append([]) ### HERE: THIS IS GETTING OVER WRITTEN
                                ballotsCastCityCouncil.append([])
                                percentagesCastCityCouncil.append([])

                        if inLoop1 and (not endLoop1) and (not inLoop2): #mayor
                            # look for dots
                            if x.find('. ') != -1:
                                y = x.split('. ')
                                name = y[0]
                                nums = y[-1]
                                # check if name or total or votes
                                if not (re.search('Total',name,re.IGNORECASE) or \
                                        re.search('Votes',name,re.IGNORECASE) ):
                                    namesOfCandidatesMayor[-1].append(name.lstrip())
                                    percentagesCastMayor[-1].append(nums.split()[-1])
                                    ballotsCastMayor[-1].append(nums.split()[0])
                            # are we at the end of the loop
                            if x.find('\r\n\r\n') != -1:
                                endLoop1 = True
                            # for other ones
                            if i < len(xs)-1:
                                if xs[i+1].find('Council Member') != -1: # for earlier years
                                    endLoop1 = True

                            # look for under votes
                            if re.search('Under Votes',x,re.IGNORECASE): endLoop1=True

                            #if endLoop1: print('end of loop1')
                        if inLoop2 and endLoop1 and not endLoop2: # city council
                            # look for dots
                            if x.find('. ') != -1:
                                y = x.split('. ')
                                name = y[0]
                                nums = y[-1]
                                # check if name or total or votes
                                if not (re.search('Total',name,re.IGNORECASE) or \
                                        re.search('Votes',name,re.IGNORECASE) ):
                                    namesOfCandidatesCityCouncil[-1].append(name.lstrip())
                                    percentagesCastCityCouncil[-1].append(nums.split()[-1])
                                    ballotsCastCityCouncil[-1].append(nums.split()[0])
                            # are we at the end of the loop?
                            if x.find('\r\n\r\n') != -1:
                                endLoop2 = True
                            # for earlier years
                            if i<len(xs)-1:
                                if len(xs[i+1]) == 0: endLoop2 = True
                                
    else:
        print('Web site does not exist, or is a PDF') 


# for AJ => make unique list of folks
print_file = False
if print_file:
    listCityCouncil = []
    listMayor = []
    for l in namesOfCandidatesCityCouncil:
        for n in l:
            listCityCouncil.append(n)

    for l in namesOfCandidatesMayor:
        for n in l:
            listMayor.append(n)


    import numpy as np
    listCityCouncil_u = np.unique(np.array(listCityCouncil))
    listMayor_u = np.unique(np.array(listMayor))

    #print
    for n in listMayor_u:
        print(n)

    for n in listCityCouncil_u:
        print(n)
    
import sys
sys.exit()

# output
# save to json
import json

v = []
for i in range(len(names)):
    v.append( {"name":names[i], "dam":dams[i], "sire":sires[i], "sex":sexes[i],
               "year":years[i], "countries":countries[i], "siblings":siblings[i] } )

# dump to file
f = open(saveFilejson,'w')
f.write(json.dumps(v,indent=2))
f.close()
    
