# Import all the things!
import sys
import os
import argparse
import re
import pycurl
from urllib.request import urlopen
from urllib.request import urlretrieve
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from githarvester import __version__

# Display Startup Banner
def banner():
  print("")
  print("  _____ _ _     _    _                           _")
  print(" / ____(_) |   | |  | |                         | |")
  print("| |  __ _| |_  | |__| | __ _ _ ____   _____  ___| |_ ___ _ __ ")
  print("| | |_ | | __| |  __  |/ _` | '__\ \ / / _ \/ __| __/ _ \ '__|")
  print("| |__| | | |_  | |  | | (_| | |   \ V /  __/\__ \ ||  __/ |   ")
  print(" \_____|_|\__| |_|  |_|\__,_|_|    \_/ \___||___/\__\___|_|   ")
  print("")
  print("Version %s" % __version__)
  print("By: @metacortex of @dc801")
  print("")

# Parse GitHub search results
def githubsearch(search, regex, order, sort):

  navbarlinks = []
  githubbase = 'https://github.com/search?'
  githubsearchurl = {'o' : order, 'q' : search, 's' : sort, 'type' : 'Code', 'ref' : 'searchresults'}
  searchurl = githubbase + str(urlencode(githubsearchurl))
  if (order == 'asc'):
    print('[+] Searching Github for ' + search + ' and ordering by OLDEST')
    print(searchurl)
  elif (order == 'desc'):
    print('[+] Searching Github for ' + search + ' and ordering by NEWEST')
    print(searchurl)
  else:
    print('[+] Searching Github for ' + search + ' and ordering by BEST MATCH')
    print(searchurl)
  searchresults = urlopen(searchurl).read()
  soup = BeautifulSoup(searchresults, 'html.parser')

  # Find the bottom nav bar and parse out those links
  pagenav = soup.findAll('div', attrs={'class':'pagination'});
  for page in pagenav:
    pages = page.findAll('a')
    for a in pages:
      navbarlinks.append(a)
  try:
    totalpages = int(str(re.findall(r">.*</a>", str(navbarlinks[-2]))).strip('[').strip(']').strip('\'').strip('>').strip('</a>'))  # Because I suck at code
  except IndexError:
    print('  [!] Search error')
    sys.exit(0)
  print('  [+] Returned ' + str(totalpages) + ' total pages')

  # Parse each page of results
  currentpage = 1
  while (currentpage <= totalpages):
    parseresultpage(currentpage, search, order, sort, regex)
    currentpage += 1

def parseresultpage(page, search, order, sort, regex):
  print('    [+] Pulling results from page ' + str(page))
  githubbase = 'https://github.com/search?'
  githubsearchurl = {'o' : order, 'p' : page, 'q' : search, 's' : sort, 'type' : 'Code', 'ref' : 'searchresults'}
  searchurl = githubbase + str(urlencode(githubsearchurl))
  pagehtml = urlopen(searchurl).read()
  soup = BeautifulSoup(pagehtml, 'html.parser')

  # Find GitHub div with code results
  results = soup.findAll('div', attrs={'class':'code-list-item'})

  # Pull url's from results and hit each of them
  soup1 = BeautifulSoup(str(results), 'html.parser')
  for item in soup1.findAll('p', attrs={'class':'title'}):
    soup2 = BeautifulSoup(str(item), 'html.parser')
    individualresult = soup2.findAll('a')[1]
    individualresulturl = 'https://github.com/' + str(individualresult['href'])
    individualresultpage = urlopen(individualresulturl).read()
    soup3 = BeautifulSoup(str(individualresultpage), 'html.parser')
    for rawlink in soup3.findAll('a', attrs={'id':'raw-url'}):
      rawurl = 'https://github.com' + str(rawlink['href'])
      if (args.custom_regex):
        searchcode(rawurl, regex)
      else:
        wpsearchcode(rawurl, regex)

def searchcode(url, regex):
  code = urlopen(url).read()
  result = ''
  try:
    regexresults = re.search(regex, str(code))
    result = str(regexresults.group(0))
    if result is not None:
      if (args.url == True):
        print("        " + str(url))
      if (args.verbose == True):
        print("      [+] Found the following results")
        print("        " + str(result))
      if args.write_file:
        if (result == ''):
          pass
        else:
          f = open(args.write_file, 'a')
          f.write(str(result + '\n'))
          f.close()


      if args.directory:
        filename = args.directory + "/" + url.replace('/', '-')
        if not os.path.exists(args.directory):
          os.makedirs(args.directory)
        print("        [+] Downloading " + filename)
        urlretrieve(url, filename)
        fp = open(filename, 'wb')
        fp.write(code)
        fp.close()
    else:
      pass
  except:
    pass

#This whole function is confusing as hell FYI
def wpsearchcode(url, regex):
  code = urlopen(url).read()
  try:
    regexdb = re.search(r"define\(\'DB_NAME.*;", str(code), re.IGNORECASE)
    regexuser = re.search(r"define\(\'DB_USER.*;", str(code), re.IGNORECASE)
    regexpass = re.search(r"define\(\'DB_PASSWORD.*;", str(code), re.IGNORECASE)
    regexhost = re.search(r"define\(\'DB_HOST.*;", str(code), re.IGNORECASE)
    db = str(regexdb.group(0)).strip('define(\'').strip('\');').replace('\', \'', ':').strip('DB_NAME:')
    user = str(regexuser.group(0)).strip('define(\'').strip('\');').replace('\', \'', ':').strip('DB_USER:')
    password = str(regexpass.group(0)).strip('define(\'').strip('\');').replace('\', \'', ':').strip('DB_PASSWORD:')
    host = str(regexhost.group(0)).strip('define(\'').strip('\');').replace('\', \'', ':').strip('DB_HOST:')

    if (db == '\', '):  # Check for blank database because...shitty code
      db = ''
    if (user == '\', '):  # Check for blank user because...shitty code
      user = ''
    if (password == '\', '):  # Check for blank password because...shitty code
      password = ''
    if (host == '\', '):  # Check for blank host because...shitty code
      host = ''

    if (args.verbose == True):
      print('      [+] Found the following credentials')
      if (args.url == True):
        print('        ' + str(url))
      print('        database: ' + db)
      print('        user: ' + user)
      print('        password: ' + password)
      print('        host: ' + host)

    if args.write_file:
      f = open(args.write_file, 'a')
      results = 'Database: ' + db + '\nUser: ' + user + '\nPassword: ' + password + '\nHost: ' + host + '\n---\n'
      f.write(results)
      f.close()

  except:
    pass


def main():
  banner()  # Brandwhore

  # Parsing arguments
  parser = argparse.ArgumentParser(description='This tool is used for harvesting information from GitHub. By default it looks for code with the filename of \'wp-config.php\' and pulls out auth info')
  parser.add_argument('-d', action='store', dest='directory', help='Download results to a specific directory', type=str)
  parser.add_argument('-o', action='store', dest='organize', help='Organize results by \'new\', \'old\', \'best\', or \'all\'', type=str)
  parser.add_argument('-r', action='store', dest='custom_regex', help='Custom regex string', type=str)
  parser.add_argument('-s', action='store', dest='custom_search', help='Custom GitHub search string', type=str)
  parser.add_argument('-u', '--url', action='store_true', help='Output URL of found object')
  parser.add_argument('-v', '--verbose', action='store_true', help='Turn verbose output on. This will output matched lines')
  parser.add_argument('-w', action='store', dest='write_file', help='Write results to a file', type=str)
  global args
  args =  parser.parse_args()

  if not len(sys.argv) > 1:
    args.verbose = True

  if args.custom_search:
    search = args.custom_search
    print('[+] Custom search is: ' + str(search))
  else:
    search = 'filename:wp-config.php'
    print('[+] Using default search')
  if args.custom_regex:
    regex = args.custom_regex
    print('[+] Custom regex is: ' + str(regex))
  else:
    regex = 'regexhere'
    print('[+] Using default regex')


  if (args.organize == 'new'):
    githubsearch(search, regex, 'desc', 'indexed')
  elif (args.organize == 'old'):
    githubsearch(search, regex, 'asc', 'indexed')
  elif (args.organize == 'best'):
    githubsearch(search, regex, '', '')
  elif (args.organize == 'all'):
    githubsearch(search, regex, '', '')
    githubsearch(search, regex, 'desc', 'indexed')
    githubsearch(search, regex, 'asc', 'indexed')
  else:
    githubsearch(search, regex, '', '')

  print('[+] DONE')

try:
  if __name__ == "__main__":
    main()
except KeyboardInterrupt:
  print("[!] Keyboard Interrupt. Shutting down")
