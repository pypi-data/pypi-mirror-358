import os,warnings
from .mini_utils import *
import pandas as pd
from rich import print as rich_print
from .data_path_settings import return_data_path




DATA_PATH= return_data_path()



# to check data file and seed file
def check_data(filename):
    seed_file =  False 
    data_file = False 
    file_path =  connect(filename)
    
    if filename in os.listdir(DATA_PATH):
        print("- data File ✔")
        data_file =  True
        
    else:
        print("-  data File ❌")
    
    seed_file_name = get_Seed_name(filename)
    if seed_file_name in os.listdir(DATA_PATH):
        print("- Seed file ✔")
        seed_file= True 
    else:
        print("- Seed File ❌")
    return seed_file


#check seed file status 

def check_data_mini(filename):

    seed_file_name =  get_Seed_name(filename)
    if seed_file_name in os.listdir(DATA_PATH):
        return True 
    else:
        return False 

    
        

# here data is loaded one , cause data might be tsv or encoded utf-8 
# to register csv file 
def register_csv(data,filename,desc=None):
    
    if check_data_mini(filename):
        os.remove(connect(get_Seed_name(filename)))  # removing the old seed file  and creating a fresh one 
        print("found already existing seed file , removed it ")
    
    
    data_seed = {}
    
    desc= desc if desc is not None  else "DATA IS NOT YET PROVIDED"
    
    data_seed["shape"] =  data.shape 
    data_seed["columns"] =  list(data.columns)
    data_seed["desc"] =  desc
    data_seed["version_names"] = []  # new names version will be added here
    
    
    seed_name  = write_seed(filename,data_seed)
    print(f"Seed `{seed_name}`  Registered Succesfully")
    


class RegisterVersion:
    
    def __init__(self,filename,version_name):
        self.filename = filename
        self.version_name = None
        self.enable_execute =  False
        if self.check_version(filename,version_name):
                self.version_name = version_name
                self.enable_execute =  True
                self.new_data = {}
                self.new_data["version_names"] = read_version_names(self.filename) + [self.version_name]
                self.new_data.setdefault(self.version_name, {})["drop_cols"] = []
                self.new_data.setdefault(self.version_name, {})["map_cols"] = {}
                self.new_data.setdefault(self.version_name, {})["text_cols"] = []
                
        else:
            print(f"Version `{version_name}` already exists or seed file is not registered.")
       
    
    def drop_cols(self,cols_list=[]):
        try :
            if self.version_name is not None:
                self.new_data[self.version_name]["drop_cols"] = cols_list
        except KeyError:
            print("Version name is already registered, please choose a different name.")
            
        
    def map_cols(self,cols_map={}):
        
        try:
            if self.version_name is not None:
                self.new_data[self.version_name]["map_cols"] = cols_map 
        except KeyError:
            print("Version name is already registered, please choose a different name.")
    
    def clean_cols(self,cols=[]):
        try:
            if self.version_name is not None:
                self.new_data[self.version_name]["text_cols"] = cols 
        except KeyError:
            print("Version name is already registered, please choose a different name.")
        
    
    
    def execute(self):
        if self.enable_execute:
            update_status = update_seed(self.filename, self.new_data)
            if update_status:
                print(f"Version `{self.version_name}` registered successfully")
                return True
            else:
                print("Failed to register version.")
                return False
        else:
            print_u("Version registration is not enabled. Please check the version name or seed file status.")
            return False
        
            
    
    def check_version(self,filename,version_name):        
        
        try :
            check_data_mini(filename)
            if version_name not in read_version_names(filename):
                return True
            else:
                print(f"Version `{version_name}` already registered. Please choose a different name.")
                return False
        except FileNotFoundError:
            print("Seed file not found, please register the seed file first.")
            return False
        
        
        
class load_seed:
    def __init__(self,filename,version=None,quiet=False):
        
        seed_status = check_data_mini(filename)
        self.filename =  filename
        self.termination_status =  False
        self.cols_status = {"drop_cols":False,
                          "map_cols":False,
                          "text_cols":False}
        
        self.cols = {"drop_cols":[],"map_cols":{},"text_cols":[]}

             
        ## VERSION != NONE + SEED STATUS 
        if version is not None and seed_status==True:
            if version in  read_version_names(filename):
                self.data =  self.read_data_file(self.filename,version,quiet)
                quiet_log(f"READING VERSION : {version}",quiet)
                self.terminate_version = True
                
                for col in self.cols_status.keys():
                    if self.cols_status[col] == False:
                        print_u(f"Column not found : {col}  Re Registering seed file")
                        self.register()
                        self.register_version(version,drop_cols=self.cols["drop_cols"],
                                              cols_maps=self.cols["map_cols"],text_cols=self.cols["text_cols"])
                        
            
            if version not in read_version_names(filename):
                warnings.warn(f"Version Name : {version}  Not Found  passing out normal data ")
                self.data =  pd.read_csv(connect(self.filename))
                self.termination_status =  False 
            
            display_Seed_file(filename,not quiet)
        
        ## VERSION == NONE + SEED STATUS 
        elif seed_status ==True and version is None:
            self.data =  pd.read_csv(connect(self.filename))      
            display_Seed_file(filename,not quiet)
        
        ## NEW DATA 
        else:
            self.data  = pd.read_csv(connect(filename))
            warnings.warn("SEED FILE IS NOT CONFIGURED YET , CONFIGURE IT USING `register` and `register_version`")
        
        
        
        
    def read_data_file(self,filename,version,quiet_status=False):
        seed_data = read_seed(filename)[version]
        data = pd.read_csv(connect(filename))
        
        transformations = {
        "drop_cols": dropper,
        "map_cols": mapper,
        "text_cols": text_cleaner }
        
        
        
        for key,func in transformations.items():
            if key in seed_data.keys():
                data =  func(data,seed_data[key],quiet_status)
                self.cols_status[key] = True 
                self.cols[key] =  seed_data[key]

        
        return data 

    
    

    def versions_list(self):
        versions = read_version_names(self.filename)
        return f"AvAILABLE VERSIONS : {versions}"
    
    def seed_file(self):
        return read_seed(self.filename)
    
    def terminate_version(self,vname):
        
        if self.termination_status and vname != None:
            seed_data = read_seed(self.filename)
            del seed_data[vname]
            seed_data["version_names"] =  [i for i in seed_data["version_names"] if i !=  vname]
            write_seed(self.filename,seed_data)
            return f"{vname} terminated "
        else:
            print("Cant terminate version , version : {vanme} not found  or You have passed `None`")
        

    
    
    def register(self,desc=None):
        
        msg = '''
        data file should be in small case 
        iris.csv  ❌
        Iris.csv  ✔
        '''
        register_csv(self.data,self.filename,desc)
    
    
    def register_version(self,version,drop_cols=[],cols_maps={},text_cols=[],exec=True):
        v =  RegisterVersion(self.filename,version)
        if drop_cols != [] :
            v.drop_cols(drop_cols)
        if cols_maps != {}:
            v.map_cols(cols_maps)
        if text_cols != []:
            v.clean_cols(text_cols)
        
        if exec:
            return v.execute()
        else:
            print_u("`v.execute()` it after checking new data")




             
        
            
            
    
    
    

    
    
