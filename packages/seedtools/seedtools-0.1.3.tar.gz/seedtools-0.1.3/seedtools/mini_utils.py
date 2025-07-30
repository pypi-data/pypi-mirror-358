import os ,json,re,string 
from .data_path_settings import return_data_path
from rich import print as rich_print

DATA_PATH= return_data_path()



def print_u(text):
    rich_print(f"[underline]{text}[/underline]")


def read_json(file_path):
    """Read a JSON file and return its content."""
    with open(file_path, 'r') as file:
        content =  file.read()
        
        if content.strip() == "":
            print("FOUND EMPTY STRING")
        else:
            return json.loads(content)
    

def write_json(data, file_path):
    """Write data to a JSON file."""
    with open(file_path, 'w') as file:
        json.dump(data, file, indent=4)


def display_recursive(obj):
    
    for i in obj :
 
        if "-:" in i:
            heading  =  f"[underline]{i.split('-:')[0]}[/underline]"
            cont =  i.split("-")[1]
            rich_print(f"{heading} {cont}")
            
        else:
            print(i)

def remove_mentions(text):
    text = re.sub(r'@\S*', '', text)
    text = re.sub(r'#\S*', '', text)
    return text

def removing_special_chars(text):
    pat = r'[^a-zA-z0-9.,!?/:;\"\'\s]'
    return re.sub(pat,'',text)

def removing_numbers(text):
    pattern = r'[^a-zA-z.,!?/:;\"\'\s]' 
    return re.sub(pattern,'',text)

def remove_punctuation(text):
    return ''.join([c for c in text if c not in string.punctuation])


def clean_text(text,apply):
    text  = str(text).lower()
    transforms = {"mentions":remove_mentions,
                  "special_chars":removing_special_chars,
                  "numbers":removing_numbers,
                  "puncs":remove_punctuation}
    if isinstance(apply,list):
        
        for application in apply:
            if application in transforms.keys():
                text = transforms[application](text)
            else:
                print(f"Tranfromation : {application} Not Available")
    
    elif isinstance(apply,str) and apply == "all":
        for application in transforms.keys():
            text = transforms[application](text)

    else:
        pass
    
    return text 
        
        
        


def dropper(df,cols,status=True):
    quiet_log(f"Dropping Columns: {cols}", status)
    df = df.drop(columns=cols, errors='ignore')
    return df

def text_cleaner(df,cols,status=True):
    quiet_log(f"Processing cols : {cols}",status)
    for i in cols:
        try:
            df[i] = df[i].apply(lambda x :  clean_text(x,apply="all"))
        except:
            df[i].values = df[i].values.apply(lambda x :  clean_text(x,apply="all"))
    return df 
    

def mapper(df,cols_map,status=True):
    quiet_log("Mapped Columns: {}".format(list(cols_map.keys())),status)
    mappings =  {}
    for (key,maps) in cols_map.items():
        if key in df.columns:
            mappings[key] = []
            if maps == "auto":
                maps = {v: k for k, v in enumerate(df[key].unique())}
                mappings[key].append(maps)
            df[key] = df[key].map(maps)   
    return (df  ,mappings)



def mapper_auto(df,cols,status=True):
    cols_dict = {}
    for v in cols:
        cols_dict[v] = "auto"
    df,mappings = mapper(df,cols_dict,status)
    return (df,mappings)        

def connect(filename):
    path_ = os.path.join(DATA_PATH,filename)
    path_=  str(path_).replace("\\","/")
    return path_
    


def get_name(filename):
    name, ext =  os.path.splitext(filename)
    return name 

def get_Seed_name(filename):
    return f"{get_name(filename)}_seed.json"


def get_ext(filename):
    name, ext =  os.path.splitext(filename)
    return ext 

def write_seed(filename,data_):
    seed_file_name  =  f"{get_name(filename)}_seed.json"
    write_json(data_,connect(seed_file_name))
    return seed_file_name

def read_seed(filename):
    seed_file_name  =  f"{get_name(filename)}_seed.json"
    data  =  read_json(connect(seed_file_name))
    return data 


def read_version_names(filename):
    return read_seed(filename)["version_names"]

def update_seed(filename,new_data):
    data = read_seed(filename)
    data.update(new_data)
    write_json(data, connect(f"{get_name(filename)}_seed.json"))
    print("Seed Updated Successfully")
    return True

def quiet_log(msg,quiet_status=True):
    if not quiet_status:
        print(msg)


def read_seed_extended(filename):
    data = read_seed(filename)
    shape = data["shape"]
    cls =  data["columns"]
    desc =  data["desc"]
    return (shape,cls,desc)

def display_Seed_file(filename,status=True):
    if status==True:
        (shape,cls,desc) =   read_seed_extended(filename)
        
        print(f"Shape: {shape}")
        print(f"Columns: {cls}")
        print(f"Description: {desc}")
    
    