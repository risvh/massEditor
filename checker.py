from pathlib import Path

def list_dir(folderpath = ".", file = False, folder = False, silent = True):
    import os
    results = []
    for filename in os.listdir(folderpath):
        fullpath = os.path.join(folderpath, filename)
        if not file and os.path.isfile(fullpath): continue
        if not folder and os.path.isdir(fullpath): continue
        # ext = os.path.splitext(filename)[-1].lower()
        results.append(filename)
        if not silent: print(filename)
    return results

def read_txt(path):
    with open(path, 'r', encoding='utf-8-sig') as f:
        text = f.read()
    return text

def save_txt(text, path):
    with open(path, 'w', newline='\n') as f:
        f.write(text)
    return text

def get_obj_name(id):
    id = int(id)
    path = Path("./objects") 
    t = read_txt(path / ("%d.txt" % id))
    lines = t.splitlines()
    name = lines[1]
    return name

def has_decay_sound(id):
    id = int(id)
    path = Path("./objects") 
    t = read_txt(path / ("%d.txt" % id))
    lines = t.splitlines()
    for line in lines:
        if 'sounds=' in line:
            sid = line.split(',')[-1].split(':')[0]
            return sid != '-1'
    return False


path = Path("./transitions/")
files = list_dir(path, file=1)

for file in files:
    if ".txt" not in file: continue
    t = read_txt(path / file)
    
    actor = file.replace(".txt", "").split("_")[0]
    target = file.replace(".txt", "").split("_")[1]
    
    items = t.split()
    if len(items) < 2: continue

    new_actor = items[0]
    new_target = items[1]
    decay_time = items[2]
    move = '0'
    if len(items) > 7: move = items[7]

    if actor == '-1' and move == '0':
        if has_decay_sound(target):
            print(target, get_obj_name(target))
    

l = """
Maple Tree
Poplar Tree
Pine Tree
Yew Tree
Mango Tree
Juniper Tree
Rubber Tree
Apple Tree
Orange Tree
Lemon Tree
Field Maple Tree
Jelutong Tree
Hickory Tree
Bubinga Tree
Balsam Tree
Cedar Tree
Kapok Tree
Ash Tree
Blossom Tree
Forsythia Tree
Plane Tree
Birch Tree
Bay Tree
""".strip().splitlines()
# obj_set = {e.split()[0]: e.replace(e.split()[0] + " ", "") for e in obj_set}

def copy_file(src, dst):
    import shutil
    shutil.copyfile(src, dst)

# path = Path("./objects")
# files = list_dir(path, file=1)

# results = []




# for file in files:
#     if ".txt" not in file: continue
#     t = read_txt(path / file)
#     lines = t.splitlines()
#     if len(lines) < 2: continue
#     id = file.replace(".txt", "")
#     name = lines[1]
        
        
#     for num, line in enumerate(lines):
#         if "sounds=" in line:
            
#             if line.split(",")[-1][:2] != "-1":
#                 print(id, name, line[-6:][:2])
                
#                 lines[0] = "id=" + str(runningID)
#                 lines[1] = lines[1].replace("Apples", "Cocoa Pods")
#                 t = '\n'.join(lines)
                
#                 save_txt(t, path / ("%s.txt" % id))
#                 break
        
        
        
        
        
        
# path = Path("./categories")
# files = list_dir(path, file=1)

# results = []

# for file in files:
#     if ".txt" not in file: continue
#     t = read_txt(path / file)
#     lines = t.splitlines()
#     if len(lines) < 2: continue
#     id = file.replace(".txt", "")
#     name = lines[1]
    
#     parentID = 0
    
#     for num, line in enumerate(lines):
#         if "parentID=" in line:
#             parentID = line.replace("parentID=", "")
#             break
    
#     if lines[1] == 'pattern':
#         mode = "pattern"
#     elif lines[1] == 'probSet':
#         mode = "probSet"
#     else:
#         mode = "category"
    
#     parentName = get_obj_name(id)
    
#     # @ = None
#     # None = pattern
#     # Perhaps = probSet
    
#     if "#" in parentName:
#         print(id, mode, parentName)
        
        
        
        
        
        
        
        
        