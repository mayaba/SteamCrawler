import requests
import json
import csv


def writeData(response):
    data = []
    data.append(response['appid'])
    data.append(response['name'])
    owners_range = response['owners']
    data.append(owners_range)
    data.append(int(owners_range.split('..')[
                0].strip().replace(',', '')))  # min
    data.append(int(owners_range.split('..')[
                1].strip().replace(',', '')))  # max
    data.append(response['average_forever'])
    data.append(response['median_forever'])
    data.append(response['average_2weeks'])
    data.append(response['median_2weeks'])
    data.append(response['price'])
    data.append(response['initialprice'])
    data.append(response['discount'])
    return data


def readFile(inputFile):
    file = open(inputFile, "r")
    lines = file.readlines()
    file.close()
    strtipedLines = []
    for line in lines:
        strtipedLines.append(line.strip('\n'))
    return strtipedLines


# full path to the appids file
appids_file = r'C:\Users\Raheem\Desktop\Concordia\SOEN 6591\project\steam-crawler\steam_crawler\crawler_utils_scripts\input\appids.txt'
appids = readFile(appids_file)
url = 'http://steamspy.com/api.php'
params = {'request': 'appdetails', 'appid': ''}
results_file = "steam_spy_results.csv"
# field names
fields = ['appid', 'name', 'owners_range', 'owners_min', 'owners_max',      'average_forever',
          'median_forever', 'average_2weeks', 'median_2weeks', 'price', 'initialprice', 'discount']

# writing to csv file
with open(results_file, 'w', newline='', encoding="utf-8") as r_file:
    # creating a csv writer object
    csvwriter = csv.writer(r_file)
    csvwriter.writerow(fields)

    for appid in appids:
        print('Querying ' + appid + ': number ' +
              str(appids.index(appid)+1) + ' out of ' + str(len(appids)))
        params['appid'] = appid
        response = requests.get(url, params=params).json()
        if response:
            csvwriter.writerow(writeData(response))

    r_file.close()
