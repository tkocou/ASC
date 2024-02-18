## Copyright 2023 by Thomas Kocourek, N4FWD

import tkinter as tk
#from tkinter import ttk
from tkinter import messagebox as mb

import os
#import sqlite3
#from datetime import datetime
from datetime import date
import global_var as gv
import read_session_count as rsc

def read_state_file(self):
    ## read in the contents of the import-update_by_state.txt
    ## selectively import only those states
    
    cs_read = ""
    #record_check = []
    self.result_text.delete(1.0,tk.END)
    file_list = os.listdir(gv.base_rpt_dir)
    target_file = os.path.join(gv.base_rpt_dir,gv.target_name)
    ## Check if we have any files to generate a report with
    with open(target_file,'r') as fh:
        test_contents = fh.read()
    if not os.path.isfile(target_file):
        mb.showwarning("Missing file in REPORTS Directory!",gv.target_name + " is missing in REPORTS directory.")
        return
    elif len(test_contents) == 0:
        mb.showwarning("Empty File!",gv.target_name + " is empty.")
        return
    ## sort list returned if more than one file
    if len(file_list) > 1:
        file_list.sort()
    
    #state_file = os.path.join(gv.base_rpt_dir,'import-update_by_state.txt')
    ## check each text file in directory 
    report_list = []   
    for file_line in file_list:
        ## skip over the capture file
        if file_line != gv.target_name:
            continue
        state_list = []
        with open(target_file,'r') as fh:
            cs_read = fh.read()
        state_list = cs_read.split('\n')
        report_list.extend(state_list)
        ##
        # At this point, we have a valid file name and potential list of states
        ##
        if len(report_list) == 0:
            mb.showwarning("No States listed","The import-update_by_state.txt file is empty.")
            ## No states listed, exit
            return
        
        ##
        ## Process the list of states
        ##
        ARRL_start = ""
        start_flag = True
        ## Did we get interrupted during an import / update
        if os.path.isfile(gv.temp_fetch_path):
            with open(gv.temp_fetch_path,'r') as gs:
                ## read in the last state being fetched
                ARRL_start = gs.read()
        self.result_text.delete(1.0,tk.END)      
        for state in report_list:
            if len(state) == 0:
                continue
            if len(ARRL_start) != 0 and state != ARRL_start and start_flag:
                continue
            start_flag = False
            website = gv.arrl_url + state.upper()
            text = "Importing from URL: "+website+'\n'
            with open(gv.temp_fetch_path,'w') as gs:
                gs.write(state)
            self.result_text.insert(tk.END,text)
            self.result_text.yview(tk.END)
            self.update_idletasks()
            rsc.get_count(self,state)
        text = "Finished."
        os.remove(gv.temp_fetch_path)
        self.result_text.insert(tk.END,text)
        ## update GUI
        today_date = str(date.today())
        self.as_of_var.set(today_date)
        self.update_idletasks()
        
    
