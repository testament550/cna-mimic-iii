from time import sleep
from bs4 import BeautifulSoup
import pandas as pd
import requests

base_url = "http://www.icd9data.com"

main_url = "http://www.icd9data.com/2015/Volume1/"

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3'}


response = requests.get(main_url, headers=headers)


main_soup = BeautifulSoup(response.content, 'html.parser')

data = []
for li1 in main_soup.select('.definitionList ul li'):
    level1_code = li1.find('a').text
    if level1_code != '740-759' or level1_code != '280-289':
        continue

    level1_description = li1.text.replace(level1_code, '').strip()
    link = li1.find('a')['href']

    lvl2_detail_url = f"{base_url}{link}"
    print(lvl2_detail_url)
    
    response = requests.get(lvl2_detail_url, headers=headers)
    lvl2_detail_soup = BeautifulSoup(response.content, 'html.parser')
  
    for li2 in lvl2_detail_soup.select('.definitionList li'):
        level2_code = li2.find('a').text
        level2_description = li2.text.replace(level2_code, '').strip()
        lvl3_detail_url = f"{base_url}{li2.find('a')['href']}"

        response = requests.get(lvl3_detail_url, headers=headers)
        lvl3_detail_soup = BeautifulSoup(response.content, 'html.parser')

        if '-' not in level2_code:
            for li3 in lvl3_detail_soup.select('.codeHierarchyUL li'):
                code = li3.find('a').text
                if '.' not in code:
                    continue
                
                if len(code.split('.')[1]) == 1:
                    level3_code = code
                    level3_description = li3.text.replace(level3_code, '').split('convert')[0].strip()
                    level4_code = code
                    level4_description = li3.text.replace(level4_code, '').split('convert')[0].strip()
                    level5_code = code
                    level5_description = level4_description
                
                if len(code.split('.')[1]) == 2:
                    level4_code = code
                    level4_description = li3.text.replace(level4_code, '').split('convert')[0].strip()
                    level5_code = code
                    level5_description = li3.text.replace(level5_code, '').split('convert')[0].strip()

                data.append([level1_code, 
                            level1_description, 
                            level1_code, 
                            level1_description, 
                            str(level2_code), 
                            level2_description, 
                            str(level4_code), 
                            level4_description,
                            str(level5_code),
                            level5_description])
            
            # continue

        for li3 in lvl3_detail_soup.select('.definitionList li'):
            level3_code = li3.find('a').text
            level3_description = li3.text.replace(level3_code, '').strip()
            lvl4_detail_url = f"{base_url}{li3.find('a')['href']}"
            response = requests.get(lvl4_detail_url, headers=headers)
            
            
            lvl4_detail_soup = BeautifulSoup(response.content, 'html.parser')

            if len(lvl4_detail_soup.select('.codeHierarchyUL li')) == 1:
                data.append([level1_code, 
                    level1_description, 
                    level2_code, 
                    level2_description, 
                    str(level3_code), 
                    level3_description, 
                    str(level3_code), 
                    level3_description,
                    str(level3_code),
                    level3_description])
                continue
                
            for li4 in lvl4_detail_soup.select('.codeHierarchyUL li'):
                code = li4.find('a').text
                if '.' not in code:
                    continue
                
                if len(code.split('.')[1]) == 1:
                    level4_code = code
                    level4_description = li4.text.replace(level4_code, '').split('convert')[0].strip()
                    level5_code = code
                    level5_description = level4_description
                
                if len(code.split('.')[1]) == 2:
                    level5_code = code
                    level5_description = li4.text.replace(level5_code, '').split('convert')[0].strip()

                data.append([level1_code, 
                            level1_description, 
                            level2_code, 
                            level2_description, 
                            str(level3_code), 
                            level3_description, 
                            str(level4_code), 
                            level4_description,
                            str(level5_code),
                            level5_description])


    
    df = pd.DataFrame(data, columns=['level1_code','level1_description',
                                 'level2_code','level2_description',
                                 'level3_code','level3_description',
                                 'level4_code','level4_description',
                                 'level5_code','level5_description'])
    output_path = 'icd9-categories-new.csv'
    df.to_csv(output_path, index=False)
    print('Sleeping for 5 minutes') #sleeping because we get 503 error for many requests
    sleep(300)



