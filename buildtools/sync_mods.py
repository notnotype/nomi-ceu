from pathlib import Path
import requests
from icecream import ic
from zipfile import ZipFile
import hashlib
import re
import subprocess
import json
import shutil
import os

# ModData https://raw.githubusercontent.com/Hex-Dragon/PCL2/main/Plain%20Craft%20Launcher%202/Resources/ModData.txt

api_key = '$2a$10$FY2a2.th733ddYVDLM5KTeGKZ.pJPeEzTUokOJJL8gLn0/HSC0RsS'
client = requests.Session()
client.headers = headers = {
  'Accept': 'application/json',
  'Content-Type': 'application/json',
  'x-api-key': api_key
}
with open("ModData.txt", "r", encoding="utf8") as f:
  mod_data = (i.strip() for i in f.readlines() if i.strip())

def calc_file_hash(path: str | Path) -> str:
  if isinstance(path, str):
    path = Path(path)
  with open(path, "rb") as f:
    return hashlib.md5(f.read()).hexdigest()

def i18modname(curseforge_name: str) -> str:
  for each in mod_data:
    for each2 in each.split("¨"):
      splited = each2.split("|")
      assert(len(splited) >= 1)
      if splited[0] in curseforge_name:
        if len(splited) == 1:
          return splited[0]
        elif len(splited) == 2:
          return re.sub(" \(.*\)", "", splited[1])
        else:
          return re.sub(" \(.*\)", "", splited[1])

def download_mod(mod_id, file_id, base_dir) -> Path:
  if isinstance(base_dir, str):
    base_dir = Path(base_dir)
  base_dir.mkdir(parents=True, exist_ok=True)
  resp = client.get(f'https://api.curseforge.com/v1/mods/{mod_id}/files/{file_id}')
  resp.raise_for_status()
  mod_info = resp.json()['data']
  ic(mod_info)
  download_url = mod_info["downloadUrl"]
  resp = client.get(download_url)
  resp.raise_for_status()
  raw_name = mod_info['fileName']
  filename = f"[{i18modname(raw_name)}] {raw_name}"
  filename = base_dir / filename
  with open(filename, "wb") as f:
    f.write(resp.content)
  
  return filename

def search_by_fingerprint(fingerprint):
  resp = client.post('https://api.curseforge.com/v1/fingerprints', json={'fingerprints': [fingerprint]})
  resp.raise_for_status()
  # with open("fingerprint_result.json", "w", encoding='utf8') as f:
  #   f.write(resp.text)
  matcheds = resp.json()['data']['exactMatches']
  if not matcheds:
    raise RuntimeError("Mod not found")
  matched = matcheds[0]
  return matched['file']['modId'], matched['file']['id']

def calc_fingerprint(path: str | Path):
  if isinstance(path, str):
    path = Path(path)
  status, result = subprocess.getstatusoutput(f'node ./fingerprint/index.mjs "{str(path)}"')
  if status != 0:
    raise RuntimeError("Can't calculate: " + result)
  return int(result)

manifest_mod_file = []
source_dir = Path('/mnt/d/Notype/things/mc/nomi-ceu-bak/versions/nomi-ceu (1.4.3)/')
target_dir = Path('/home/notnotype/Desktop/nomi-ceu-client-1.4.3/')

for each in (i for i in (source_dir / 'mods').glob('*') if i.is_file()):
  try:
    fingerprint = calc_fingerprint(each)
    modid, fileid = search_by_fingerprint(fingerprint)
  
    ic(each, modid, fileid)

    resp = client.get(f'https://api.curseforge.com/v1/mods/{modid}/files/{fileid}')
    resp.raise_for_status()
    mod_info = resp.json()['data']

    # with open("result.json", "w", encoding="utf8") as f:
    #   f.write(resp.text)

    curseforge_md5 = mod_info['hashes'][1]['value']
    file_md5 = calc_file_hash(each)
    # ic(curseforge_md5, file_md5)
    if curseforge_md5 == file_md5:
      manifest_mod_file.append({
        "projectID": modid,
        "fileID": fileid,
        "required": True
      })
  except RuntimeError as e:
    print(f"[{str(e)}]Can't process: filename: {each}")
    dst_file = target_dir / 'overrides' / 'mods' / each.name
    if dst_file.exists():
      os.remove(dst_file)
    print(f"Moving {each} to {dst_file}")
    shutil.copy(each, dst_file)
    continue

with open(target_dir / "manifest.json", 'r', encoding='utf8') as f:
  old_manifest = json.load(f)
old_manifest['files'] = manifest_mod_file
with open(target_dir / "manifest.json", 'w', encoding='utf8') as f:
  f.write(json.dumps(old_manifest))
# t = calc_fingerprint('./abcdefghijkaaaaaaaaaaaaaaaaaaaaaaaaaaa.jar')
# ic(t)