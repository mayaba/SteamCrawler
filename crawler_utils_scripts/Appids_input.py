# This script reads a file contains appids, pick randomly 5000 appids, and create valid URLS for the reviews and news of each picked appid
import random


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
base_community_url = ['http://steamcommunity.com/app/',
                      '/reviews/?browsefilter=mostrecent&p=1&filterLanguage=english']
base_news_url = ['http://steamcommunity.com/app/',
                 '/allnews/?p=1']

# randomly pick a sample of 5000 appids
sample = random.sample(appids, 5000)
print(sample)
print(len(sample))

# write the community URL for the appids
with open('community_urls.txt', 'w') as file1:
    for app in sample:
        file1.write("%s\n" % app.join(base_community_url))
file1.close()

# write the news URL for the appids
with open('news_urls.txt', 'w') as file2:
    for app in sample:
        file2.write("%s\n" % app.join(base_news_url))
file2.close()
