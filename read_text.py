## Copyright 2023 by Thomas Kocourek, N4FWD

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb

import os
import sqlite3
import global_var as gv

def read_text_file(self):
    callsigns = []
    cs_read = ""
    record_check = []
    self.result_text.delete(1.0,tk.END)
    file_list = os.listdir(gv.base_rpt_dir)
    for file_line in file_list:
        cs_list = []
        path_to_file = os.path.join(gv.base_rpt_dir,file_line)
        with open(path_to_file,'r') as fh:
            cs_read = fh.read()
        cs_list = cs_read.split('\n')
        callsigns.extend(cs_list)
    if len(callsigns) == 0:
        mb.showwarning("Empty REPORTS Directory!","No callsign text files found in REPORTS directory.")
    callsign_list = []
    for call in callsigns:
        ##
        ## empty callsigns and callsigns not in the database are ignored
        ##
        tmp_list = []
        sql_text = "SELECT * FROM ve_count WHERE call LIKE ?"
        self.lookup_callsign = call
        self.exact_matched = False
        lup_callsign = '%'+self.lookup_callsign.upper()+'%'
        db_connection = sqlite3.connect(gv.asc_database)
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
        except: ## database problem
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
                    except: ## database problem
                        record_check = []
                    break
        else: ## add single matched callsign
            callsign_list.extend(record_check)
        db_connection.close()
    
    ## Only do a report if we have valid data
    if len(callsign_list) > 0:
        callsign_list.sort(key=lambda tup_var: tup_var[4], reverse = True)
        for r in callsign_list:
            text_line = "Count:{}, Call:{}, County:{}, State:{}, Accredited:{}\n".format(r[4],r[1],r[2],r[5],r[3])
            self.result_text.insert(tk.END,text_line)
            
    self.update_idletasks()
    
