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
                                
                # out of for
                #if icount == 1:
                #    sys.exit()

    #else:
    #    print('precicnet data website not there')
    #    # we don't have this precient for this year         

                    

            
            #import sys
            #sys.exit()

        #import sys
        #sys.exit()
    else:
        print('Web site does not exist, or is a PDF') 
    
import sys
sys.exit()

# webparsing numbers
startSmall=0
startLarge=0

names = []
sires = []
dams = []
sexes = []
years = []
siblings = []
countries = []

# find number of doggos listed
w = 'http://www.cardiped.net/browseDogs.php?start='+\
    str(int(startSmall))+\
    '&p_f='+\
    str(int(startLarge))+\
    '&sortBy=name&alpha=a'
# parse
page = requests.get(w)
soup = bs4.BeautifulSoup(page.text, 'html.parser')
soup = str(soup)

# figuring out from webpage how many doggos
x = soup.split('Displaying')[1]
x = x.split('</b>')[0]
x = x.split('of ')[1]
numberOfDoggos = int(x)

while startSmall < numberOfDoggos:
    w = 'http://www.cardiped.net/browseDogs.php?start='+\
        str(int(startSmall))+\
        '&p_f='+\
        str(int(startLarge))+\
        '&sortBy=name&alpha=a'
    print(w)
    
    # parse
    page = requests.get(w)
    soup = bs4.BeautifulSoup(page.text, 'html.parser')
    soup = str(soup)

    # split by details
    splitSoup = soup.split('<a href="details.php?id=')
    # ignore top
    splitSoup = splitSoup[1:]
    # take out last bit from last one
    x = splitSoup[-1]
    y = x.split('</table>')
    splitSoup[-1] = y[0]

    
    # loop and append
    for s in splitSoup:
        #print(s)
        #print('---')

        # navigate to details page
        myid = s.split('">')[0]
        w_details = 'http://www.cardiped.net/details.php?id=' + str(myid)
        page_details = requests.get(w_details)
        soup_details = bs4.BeautifulSoup(page_details.text, 'html.parser')
        soup_details = str(soup_details)
        # name
        name = ((soup_details.split('Registered Name:')[1]).split('<td>')[1]).split('</td>')[0]
        # Dad
        sire = ((soup_details.split('Sire:')[1]).split('<td>')[1]).split('</td>')[0]
        #   listed?
        if len(sire) > 0:
            sire = (sire.split('>')[1]).split('<')[0]
        else:
            sire = ''
        # Mom
        dam = ((soup_details.split('Dam:')[1]).split('<td>')[1]).split('</td>')[0]
        if len(dam) > 0:
            dam = (dam.split('>')[1]).split('<')[0]
        else:
            dam = ''
        # Sex
        sex = ((soup_details.split('Sex:')[1]).split('<td>')[1]).split('</td>')[0]
        # Birthday
        dob = ((soup_details.split('Date of Birth:')[1]).split('<td>')[1]).split('</td>')[0]
        # listed?
        if len(dob.split()) > 0:
            #  just grab year
            year = dob.split()[-1]
        else:
            year = ''
        # nationality
        country = ((soup_details.split('Country of Birth:')[1]).split('<td>')[1]).split('</td>')[0]
        # siblings
        # do we have them listed?
        if len(soup_details.split('Siblings:')) > 1:
            sibs =  ((soup_details.split('Siblings:')[1])).split('</td>')[0]
            sibs = sibs.split('">')[1:]
            # loop and update
            for i in range(len(sibs)):
                sibs[i] = sibs[i].split('<')[0]
        else:
            sibs = []
                
        names.append(name)
        sires.append(sire)
        dams.append(dam)
        sexes.append(sex)
        years.append(year)
        siblings.append(sibs)
        countries.append(country)

        
            
    startSmall += 20
    if startSmall%100 == 0:
        startLarge += 100




# now, save this dataset
def replaceWeird(st):
    sto = st.replace("'","")
    sto = st.replace('"','')
    sto = st.replace("'",'')
    return sto

# loop through things and replace any weirdos
for i in range(len(names)):
    names[i] = replaceWeird(names[i])
    dams[i] = replaceWeird(dams[i])
    sires[i] = replaceWeird(sires[i])
    sexes[i] = replaceWeird(sexes[i])
    years[i] = replaceWeird(years[i])
    countries[i] = replaceWeird(countries[i])
    for j in range(len(siblings[i])):
        siblings[i][j] = replaceWeird(siblings[i][j])



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
    
