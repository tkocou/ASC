## Copyright 2023 by Thomas Kocourek, N4FWD

import tkinter as tk
#from tkinter import ttk
from tkinter import messagebox as mb

import os
import sqlite3
import global_var as gv

def read_text_file(self,flag):
    ## Need to check each text file for valid callsigns
    ## If all of the files are invalid, then throw an error message
    ## For each valid file, append the file name and the contents to
    ## the report 'list'
    if flag == '1':
        ARRL_only = True
        GLAARG_only = True
    elif flag == '2':
        ARRL_only = True
        GLAARG_only = False
    elif flag == '3':
        ARRL_only = False
        GLAARG_only = True
    
    report_list = []
    cs_read = ""
    record_check = []
    self.result_text.delete(1.0,tk.END)
    file_list = os.listdir(gv.base_rpt_dir)
    ## Check if we have any files to generate a report with
    if len(file_list) == 0:
        mb.showwarning("Empty REPORTS Directory!","No callsign text files found in REPORTS directory.")
        return
    ## sort list returned if more than one file
    if len(file_list) > 1:
        file_list.sort()
    
    ## save results into generic text file
    capture_file = os.path.join(gv.base_rpt_dir,'another_session_count.txt')
    try:
        with open(capture_file,'w') as fh: 
            pass
    except Exception:
        ## file exists, do nothing
        pass
    ## open the text file results capture file
    tf = open(capture_file,'w')
    ## check each text file in directory    
    for file_line in file_list:
        ## skip over the capture file
        if file_line == 'another_session_count.txt':
            continue
        if file_line == 'import-update-by-state.txt':
            continue
        cs_list = []
        path_to_file = os.path.join(gv.base_rpt_dir,file_line)
        with open(path_to_file,'r') as fh:
            cs_read = fh.read()
        cs_list = cs_read.split('\n')
        report_list.extend(cs_list)
        ##
        # At this point, we have a valid file name and potential list of callsigns
        ##
        if len(report_list) == 0:
            ## No callsigns, skip this file
            continue
        
        ##
        ## Process the list of callsigns
        ##
        callsign_list = []
        glaarg_callsign_list = []
        for call in report_list:
            ##
            ## callsigns not in the ARRL database are ignored
            ##
            tmp_list = []
            sql_text = "SELECT * FROM ve_count WHERE call LIKE ?"
            self.lookup_callsign = call
            self.exact_matched = False
            lup_callsign = '%'+self.lookup_callsign.upper()+'%'
            db_connection = sqlite3.connect(gv.asc_database_path)
            db_cursor = db_connection.cursor()
            
            tmp_list.append(lup_callsign)
            try:
                if len(call) > 0: ## might have an empty element in the list
                    ## Do SQL query only if 'call' is not empty
                    db_cursor.execute(sql_text,tuple(tmp_list))
                    record_check = db_cursor.fetchall()
                    self.exact_matched = True
                else:
                    record_check = []
            except Exception: ## database problem
                record_check = []
            
            if len(record_check) > 1:  ## multiple match
                self.exact_matched = False  
                sql_match = 'SELECT * FROM ve_count WHERE id = ?'
                tmp_list = []
                
                for record in record_check:
                    exact_match = record[1].split(' ')
                    if exact_match[0] == self.lookup_callsign.upper():
                        self.exact_matched = True
                        tmp_list.append(record[0])
                        try:
                            db_cursor.execute(sql_match,tuple(tmp_list))
                            record_check = db_cursor.fetchall()
                            ## add exactly matched callsign
                            callsign_list.extend(record_check)
                        except Exception: ## database problem
                            record_check = []
                        break
            else: ## add single matched callsign
                callsign_list.extend(record_check)
            
            ## GLAARG DB check
            ##
            ##
            ## callsigns not in the ARRL database are ignored
            ##
            tmp_list = []
            glaarg_sql_text = "SELECT * FROM glaarg_count WHERE csign LIKE ?"
            self.lookup_callsign = call
            self.exact_matched = False
            lup_callsign = '%'+self.lookup_callsign.upper()+'%'
            
            #db_connection = sqlite3.connect(gv.asc_database_path)
            #db_cursor = db_connection.cursor()
            
            tmp_list.append(lup_callsign)
            try:
                if len(call) > 0: ## might have an empty element in the list
                    ## Do SQL query only if 'call' is not empty
                    db_cursor.execute(glaarg_sql_text,tuple(tmp_list))
                    record_check = db_cursor.fetchall()
                    self.exact_matched = True
                else:
                    record_check = []
            except Exception: 
                record_check = []
            if len(record_check) > 1:  ## multiple match
                self.exact_matched = False  
                sql_match = 'SELECT * FROM glaarg_count WHERE id = ?'
                tmp_list = []
                
                for record in record_check:
                    exact_match = record[2]
                    if exact_match == self.lookup_callsign.upper():
                        self.exact_matched = True
                        tmp_list.append(record[0])
                        try:
                            db_cursor.execute(sql_match,tuple(tmp_list))
                            record_check = db_cursor.fetchall()
                            ## add exactly matched callsign
                            glaarg_callsign_list.extend(record_check)
                        except Exception: ## database problem
                            record_check = []
                        break
            else: ## add single matched callsign
                glaarg_callsign_list.extend(record_check)
            
            db_connection.close()
        
        ## Only do a report if we have valid data
        if len(callsign_list) > 0:
            if ARRL_only:
                ## Print the file name
                text_line = '\n'+file_line + ' - ARRL Report\n\n'
                tf.write(text_line)
                self.result_text.insert(tk.END,text_line)
                ## Print the contents
                callsign_list.sort(key=lambda tup_var: tup_var[4], reverse = True)
                for r in callsign_list:
                    text_line = "Count:{}, Call:{}, County:{}, State:{}, Accredited:{}\n".format(r[4],r[1],r[2],r[5],r[3])
                    tf.write(text_line)
                    self.result_text.insert(tk.END,text_line)
          
        if len(glaarg_callsign_list) > 0:
            if GLAARG_only:
                ## Print the file name
                text_line = '\n'+file_line + ' - GLAARG Report\n\n'
                tf.write(text_line)
                self.result_text.insert(tk.END,text_line)
                ## Print the contents
                glaarg_callsign_list.sort(key=lambda tup_var: tup_var[4], reverse = True)
                for r in glaarg_callsign_list:
                    text_line = "Count:{}, Call:{}, Name:{}, Helped:{}, Overseen:{}, New License:{}, Upgrades:{}\n".format(r[4],r[2],r[3],r[5],r[6],r[7],r[8])
                    tf.write(text_line)
                    self.result_text.insert(tk.END,text_line)
        
        report_list = []
    tf.close()      
    self.update_idletasks()
    
