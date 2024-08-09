import os
import base64
import bz2
import platform
import re

import global_var as gv
import icons_array as ia 

asc_dir = ""
home_dir = os.path.expanduser('~')
basic_dir = ""
gv.platform_os = platform.system()
sys_platform = gv.platform_os

def set_environment():
    global asc_dir, home_dir, basic_dir
    ### Some code to accomodate the development environment
    ### leaving this in should not affect the production version

    gv.basic_dir = os.getcwd()
    
    if re.search(r"Projects",gv.basic_dir): ## we might be working in directory "Projects/ASC"
        project_dir = "Projects"
    else:
        project_dir = ""
        
    ## Is the program running in my development environment?
    ##
    ## Build correct path to working directory and save as a global
    ## That way the correct path can be referenced elsewhere
    ##
    ## The flag 'first_pass' is set to true in 'global_var.py' at start of program
    if gv.first_pass:
        if project_dir == "Projects":
            ## Build a path referencing the home dir
            if gv.basic_dir[-3:] != 'ASC':
                asc_dir = os.path.join(os.getcwd(),gv.asc_dir)
            else:
                asc_dir = gv.basic_dir
            project3_dir = os.path.join(asc_dir, gv.report_dir)
            gv.base_rpt_dir = os.path.join(home_dir, project3_dir)
            
            ## while the program is running, set 'first_pass' to False
            gv.first_pass = False
        elif project_dir != "Projects":
            home_dir = os.path.expanduser('~')
            gv.basic_dir = home_dir
            asc_dir = os.path.join(home_dir,gv.asc_dir)
            gv.base_rpt_dir = os.path.join(asc_dir, gv.report_dir)
            ## while the program is running, set 'first_pass' to False
            gv.first_pass = False
        else:
            pass
        
        ## Create the ASC directory
        try:
            os.mkdir(asc_dir)
        except Exception: ## directory already exists, do nothing
            pass


        try:
            os.mkdir(gv.base_rpt_dir)
        except Exception: ## directory already exists, do nothing
            pass

        make_launcher() 
    
    ## return that path
    if gv.basic_dir[-3:] == "ASC":
        basic_dir = gv.basic_dir[:-4]
    else:
        basic_dir = gv.basic_dir
        
    return basic_dir

        

def make_launcher():
    global asc_dir, home_dir, basic_dir
    
     ## Path to Desktop
    desktop_dir = os.path.join(home_dir,"Desktop")
    
    ## we are looking for the path to 'bash'
    ## the os.system() function does not return expexted results
    ## so a round-about method is used
    file_to_cap = "tmp_file"
    ## create a temporary file
    with open(file_to_cap,"w") as x: 
        pass
    ## tell the os.system() to write it's result to the temporary file
    cmd = "which bash > "+ file_to_cap
    os.system(cmd)
    ## read in the result and assign it to a variab;e
    with open("tmp_file","r") as x:
        shell_cmd = x.read()
    shell_cmd.rstrip('\n') ## last character is a '\n'; remove it
    print("shell_cmd: ",list(shell_cmd))
    ## remove the temporary file.
    os.remove(file_to_cap)

    #file_dict={'licon':"database.svg",'wicon':"database.ico",'wdesk':"CVE-DB.lnk"}
    file_dict={'licon':"database.svg"}
    
    keys = file_dict.keys()
    for key in keys:
        file_name = os.path.join(asc_dir,file_dict[key])
        string_data = ia.local_array[key]
        byte_data = bytes(string_data,'utf-8')
        decoded_data = base64.b64decode(byte_data)
        bin_data = bz2.decompress(decoded_data)
        with open(file_name,"wb") as f:
            f.write(bin_data)
          
    if sys_platform  == "Linux":
        ## let's create a desktop launcher
            launcher = "ASC-DB.desktop"
            desktop_launcher_path = os.path.join(desktop_dir,launcher)
            ## get the path towhere js8msg2 is executing from
            #exec_path = os.path.join(home_dir,"bin/ASC-DB")
            exec_path = os.path.join(home_dir,"ASC/start.sh")
            ## tell the launch to not display any printing from the start.sh
            exec_cmd = shell_cmd+ " "+ exec_path + "> /dev/null"
            icon_picture_path = os.path.join(asc_dir,"database.svg")
            ## updating launcher internals
            with open(desktop_launcher_path, "w") as fh:
                fh.write("[Desktop Entry]\n")
                fh.write("Version="+gv.version+"\n")
                fh.write("Type=Application\n")
                fh.write("Terminal=false\n")
                fh.write("Icon="+icon_picture_path+'\n')
                fh.write("Icon[en_US]="+icon_picture_path+'\n')
                fh.write("Name[en_US]=ASC-DB\n")
                #fh.write("Exec="+exec_path+'\n')
                fh.write("Exec="+exec_cmd+'\n')
                fh.write("Comment[en_US]="+gv.program+"\n")
                fh.write("Name=CVE-DB\n")
                fh.write("Comment="+gv.program+"\n")
            os.chmod(desktop_launcher_path,0o755)
