import requests
import json
import os
from jikanpy import Jikan

user = os.environ.get('MAL_USER')
apikey = os.environ.get('SONARR_APIKEY')
sonarr_endpoint = os.environ.get('SONARR_ENDPOINT')

if None in [user,apikey,sonarr_endpoint]:
    print("please include the required environment variables")
    exit()

# valid lists are: all, watching, completed, onhold, dropped, plantowatch/ptw
target_list = os.environ.get('TARGET_LIST','ptw')


root_folder_path = os.environ.get('ROOT_FOLDER_PATH','/downloads/Anime')
monitored = os.environ.get('MONITORED',True)
all_missing = os.environ.get('ALL_MISSING',False)


# create jikan object to call to jikan-MAL API
jikan = Jikan()

page = 1
params = {  'page':page,
            'sort':'desc',
            'order_by':'last_updated'
         }

# get initial list from MAL
plan_to_watch = jikan.user(username=user, request='animelist',argument=target_list, parameters=params)['anime']

# get all pages if really long
tmp_plan_to_watch = plan_to_watch
while len(tmp_plan_to_watch) >= 300:
    page+=1
    params['page']=page
    tmp_plan_to_watch =  jikan.user(username=user, request='animelist',argument=target_list, parameters=params)['anime']
    plan_to_watch.extend(tmp_plan_to_watch)
titles=[x['title'] for x in plan_to_watch]
mal_ids=[x['mal_id'] for x in plan_to_watch]
print(titles)
print(mal_ids)
# ################
exit()
# Load mal-tvdb mappings
mappings = json.load(open('./animelist_mappings.json'))

# loop through all ids in list
for mal_id in mal_ids:
# # map MAL ids to tvdb ids
    element = next((item for item in mappings if item["mal_id"] == mal_id), None)

    # skip if not found
    if element is None:
        print("not found, maybe it hasn't been added yet?")
        # exit()
        continue
    if 'thetvdb_id' not in element:
        print("no tvdb entry")
        # exit()
        continue

    tvdb_id = element['thetvdb_id']


    # create payload
    payload = { 'term': tvdb_id,
                'apikey': apikey
                } 

    # lookup to get full info
    resp = requests.get(sonarr_endpoint+'/api/series/lookup',params=payload)

    # break on error
    if resp.status_code != 200:
        print(f"error, status code {resp.status_code}")
        exit()

    # get single json array element
    json_payload = resp.json()[0]
    
    # add sonarr required info and additional options 
    # print(json_payload)
    json_payload['profileId']=1
    json_payload['seasonFolder']=True
    json_payload['monitored']=monitored
    json_payload['RootFolderPath']=root_folder_path
    json_payload['addOptions']={"searchForMissingEpisodes": all_missing}
    json_payload['seriesType']='anime'




    # check if it already exists on sonarr
    # resp = requests.get(sonarr_endpoint+'/api/series/1',params={'apikey':apikey})
    # json_payload = resp.text
    # print(json_payload)

    # post to add show
    resp = requests.post(sonarr_endpoint+'/api/series',params={'apikey':apikey}, json=json_payload)
    if resp.status_code != 200:
        print(f"error, status code {resp.status_code}")
        exit()
    print(resp.text)




