import requests
import time
import csv

secretsVersion = input('To edit production server, enter the name of the \
secrets file: ')
if secretsVersion != '':
    try:
        secrets = __import__(secretsVersion)
        print('Editing Production')
    except ImportError:
        secrets = __import__('secrets')
        print('Editing Development')
else:
    print('Editing Development')

startTime = time.time()

baseURL = secrets.baseURL
user = secrets.user
password = secrets.password
repository = secrets.repository

auth = requests.post(baseURL + '/users/' + user + '/login?password='
                     + password).json()
session = auth['session']
headers = {'X-ArchivesSpace-Session': session,
           'Content_Type': 'application/json'}

endpoint = '/repositories/' + repository + '/resources?all_ids=true'

ids = requests.get(baseURL + endpoint, headers=headers).json()

f = csv.writer(open('topContainerCountByResource.csv', 'w'))
f.writerow(['title'] + ['bib'] + ['uri'] + ['id_0'] + ['id_1'] + ['id_2']
           + ['id_3'] + ['topContainerCount'])

f2 = csv.writer(open('topContainersLinks.csv', 'w'))
f2.writerow(['resourceUri'] + ['topContainerUri'])

f3 = csv.writer(open('uniqueTopContainers.csv', 'w'))
f3.writerow(['topContainer'] + ['indicator'] + ['barcode'])


total = len(ids)
topContainerLinks = []
uniqueTopContainers = []
for id in ids:
    resourceTopContainers = []
    print('id', id, total, 'records remaining')
    total = total - 1
    endpoint = '/repositories/' + repository + '/resources/' + str(id)
    output = requests.get(baseURL + endpoint, headers=headers).json()
    title = output['title']
    print(title)
    uri = output['uri']
    try:
        bib = output['user_defined']['real_1']
    except ValueError:
        bib = ''
    print(bib)
    id0 = output['id_0']
    try:
        id1 = output['id_1']
    except ValueError:
        id1 = ''
    try:
        id2 = output['id_2']
    except ValueError:
        id2 = ''
    try:
        id3 = output['id_3']
    except ValueError:
        id3 = ''
    page = 1
    resultsPage = ''
    results = []
    while resultsPage != []:
        print(page)
        payload = {'page': page, 'page_size': '100', 'root_record': endpoint}
        search = requests.get(baseURL + '/search', headers=headers,
                              params=payload).json()
        resultsPage = search['results']
        for result in resultsPage:
            results.append(result)
        page = page + 1

    for result in results:
        try:
            topContainers = result['top_container_uri_u_sstr']
            for topContainer in topContainers:
                if topContainer not in resourceTopContainers:
                    resourceTopContainers.append(topContainer)
                if topContainer not in uniqueTopContainers:
                    uniqueTopContainers.append(topContainer)
                topContainerLink = str(id) + '|' + topContainer
                if topContainerLink not in topContainerLinks:
                    topContainerLinks.append(topContainerLink)
        except ValueError:
            topContainers = []
    topContainerCount = len(resourceTopContainers)
    print('top containers', topContainerCount)
    f.writerow([title] + [bib] + [uri] + [id0] + [id1] + [id2] + [id3]
               + [topContainerCount])

print('top container links')
for topContainerLink in topContainerLinks:
    f2.writerow([topContainerLink[:topContainerLink.index('|')]]
                + [topContainerLink[topContainerLink.index('|') + 1:]])

print('unique top containers')
for topContainer in uniqueTopContainers:
    print(topContainer)
    search = requests.get(baseURL + topContainer, headers=headers).json()
    try:
        indicator = search['indicator']
    except ValueError:
        indicator = ''

    try:
        barcode = search['barcode']
    except ValueError:
        barcode = ''
    f3.writerow([topContainer] + [indicator] + [barcode])

elapsedTime = time.time() - startTime
m, s = divmod(elapsedTime, 60)
h, m = divmod(m, 60)
print('Total script run time: ', '%d:%02d:%02d' % (h, m, s))
