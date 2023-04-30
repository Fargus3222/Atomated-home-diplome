import json
import os



JSON_PATH = f'{os.getcwd()}/json_configs'

def Get_req_images():
    info = []
    
 
    rootdir = f'{os.getcwd()}/../Required_images'
    for rootdir, dirs, files in os.walk(rootdir):
        for subdir in dirs:
            if("image" in subdir):

                info_image = {"name": subdir, "path":os.path.join(rootdir, subdir)} 
                info.append(info_image)


        

    with open(f"{JSON_PATH}/images.json", "w") as outfile:
        outfile.write(json.dumps(info, indent=4))


Get_req_images()