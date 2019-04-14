# base page: https://champaigncountyclerk.com/elections/results/history
# for web scraping
import requests, bs4
import httplib2

# were are we saving data?
saveFilejson = '/Users/jillnaiman1/champaignElection/data/election_results.json'

#-----------------------------------------------------------

# for debugging
import sys
import re
from datetime import datetime

# main page:
w = 'https://champaigncountyclerk.com/elections/results/history'
# see what we have available
# parse
page = requests.get(w)
soup = bs4.BeautifulSoup(page.text, 'html.parser')
soup = str(soup)

# cull to champaign precincts
soup2 = soup.split('The following are archived election results for Champaign County')[1]

# look for precent ids
soup3 = soup2.split('/elections/results/precinct?ID=')
# loop and grab
soup3 = soup3[1:]
precentNums = []
for s in soup3:
    precentNums.append( s.split('">')[0] )

    
# for to store!
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


#icount = 0 # for debugging

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
                #icount += 1 # for debugging

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
                    if re.search('BALLOTS CAST - TOTAL',x,re.IGNORECASE):
                        totalBallotsCast.append(int(x.split()[-1]))
                        istart1 = i
                        # istart1 controls the fact that we only want to
                        #  start looking for mayors/candidates when we've got the
                        #  total infos (and not before)
                    if i > istart1: # now into actual votes
                        # look for openings of where mayor or
                        #  city council is stored
                        if re.search('at large', x, re.IGNORECASE) or re.search('at-large',x,re.IGNORECASE) \
                           or re.search('Mayor CITY',x,re.IGNORECASE):
                            if not inLoop1:
                                inLoop1 = True
                                namesOfCandidatesMayor.append([])
                                ballotsCastMayor.append([])
                                percentagesCastMayor.append([])
                            # second loop for results of city council stuffs
                            if inLoop1 and endLoop1:
                                inLoop2 = True
                                inLoop1 = False
                                namesOfCandidatesCityCouncil.append([]) 
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
                            
                            # look for under votes -> sometimes we need this instead as the
                            #  end loop thing
                            if re.search('Under Votes',x,re.IGNORECASE): endLoop1=True

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
                # end of for loop
                if endLoop1 == False:
                    # this never got called
                    print('never called inloop 1')
                    print(w2)
                    sys.exit()
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

    print('----')

    for n in listCityCouncil_u:
        print(n)


# lets format!
import numpy as np
d2 = np.unique(dates)
dates = np.array(dates)
precincts = np.array(precincts)
regVoters = np.array(regVoters)
totalBallotsCast = np.array(totalBallotsCast)
namesOfCandidatesMayor = np.array(namesOfCandidatesMayor)
namesOfCandidatesCityCouncil = np.array(namesOfCandidatesCityCouncil)
ballotsCastMayor = np.array(ballotsCastMayor)
ballotsCastCityCouncil = np.array(ballotsCastCityCouncil)
percentagesCastMayor = np.array(percentagesCastMayor)
percentagesCastCityCouncil = np.array(percentagesCastCityCouncil)
electionOut = []
for i,d in enumerate(d2):
    mask = dates == d
    # precinct
    ps = precincts[mask]
    # voters per precinct
    rVoters = regVoters[mask]
    # ballots cast per precinct
    bCast = totalBallotsCast[mask]
    # grab candidates for mayor
    m = namesOfCandidatesMayor[mask]
    bm = ballotsCastMayor[mask]
    pm = percentagesCastMayor[mask]
    cc = namesOfCandidatesCityCouncil[mask]
    bcc = ballotsCastCityCouncil[mask]
    pcc = percentagesCastCityCouncil[mask]

    # to store precinct results
    presults = []
    for j in range(len(ps)):
        presults.append( {"mayor_election":{"candidates":m[j],
                                            "ballotsCast":bm[j],
                                            "percentages":pm[j],
                                            "party":np.repeat('P',len(m[j])).tolist() # placeholder
                                            },
                          "precinctSummary":{"registered_voters":rVoters[j],
                                             "total_ballots_cast":bCast[j],
                                             "precinct_number":ps[j]
                                             },
                          "city_council_election":{"candidates":cc[j],
                                                   "ballotsCast":bcc[j],
                                                   "percentages":pcc[j],
                                                   "party":np.repeat('P',len(m[j])).tolist() # placeholder
                                                   }
                          } # end of this precinct
                         ) # end of appending

    electionOut.append( {"year":d.year, "precincts":presults} )


# output
# save to json
import json


# for weird integers in numpy
# source: https://stackoverflow.com/questions/11942364/typeerror-integer-is-not-json-serializable-when-serializing-json-in-python
def default(o):
    if isinstance(o, np.int64): return int(o)  
    raise TypeError

#json.dumps({'value': numpy.int64(42)}, default=default)


# dump to file
f = open(saveFilejson,'w')
f.write(json.dumps(electionOut,indent=2, default=default))
f.close()
    
