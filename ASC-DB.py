#! /bin/python
## Bit and pieces are borrowed from my CVE-DB program
## Copyright 2023 Thomas Kocourek, N4FWD

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb

import os
import sys
import re
import sqlite3
from datetime import datetime
from datetime import date
from croniter import croniter 
from threading import *
from threading import Thread
    
## import support files here
import ve_utilities as ut
import global_var as gv
import asc_db_setup as adb
import read_session_count as rsc
import session_count_display as scd
import detailed_count_display as dcd
import set_up_defaults as sud
import read_text as rt
import read_session_count_glaarg as rg
import glaarg_session_count_display as gls
import glaarg_detailed_count_display as gld
import read_state as rs

# for inter-thread comms
event = Event()

class Update(Thread):
    global event
    def __init__(self, app_self, func, display_widget, cron_data):
        super().__init__()
        self.keep_running = True
        self.cron_data = cron_data
        self.called_function = func
        self.display_widget = display_widget
        self.app_self = app_self
        self.no_skip = True
        
        self.display_widget.delete(1.0,tk.END)
        
    def stop(self):
        self.keep_running = False
        self.no_skip = False
    
            
    def run(self):
        curr_time = datetime.now()
        iter_time_obj = croniter(self.cron_data, curr_time)
        while self.keep_running:
            ## when 'iter_time_obj.get_next()' is invoked, the next available
            ## time is created. For a daily cron event, the date will jump
            ## to the next available day per the cron setting.
            curr_time = datetime.now()
            sometime = iter_time_obj.get_next(datetime)
            delta = (sometime - curr_time).total_seconds()
            text = "Auto-Update: Waiting time in seconds to next update: {}\n".format(delta)
            self.display_widget.insert(tk.END,text)
            event.wait(delta)
            if self.no_skip:
                text = "Auto-Update: Updating database at {}.\n".format(datetime.now())
                self.display_widget.insert(tk.END,text)
                self.called_function()
                text = "Auto-Update: Finished Update at {}.\n\n".format(datetime.now())
                self.display_widget.insert(tk.END,text)
            else:
                self.no_skip = True
            curr_time = datetime.now()
        text = "Auto-Update: Exiting thread.\n"
        self.display_widget.insert(tk.END,text)
              

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        
        self.protocol("WM_DELETE_WINDOW",self.goodbye)
        self.environment = ut.set_environment
        ## GUI variables go next
        ## set up window dimensions, title , etc.
        self.title(gv.program)
        self.resizable(width=False, height=False)
        self.running = False
        self.update_db_obj = None
        ## save SQL results
        self.text_text = ""
        self.text_list = []
        self.shebang = False
        self.lookup_callsign = ""
        self.exact_matched = False
        self.glaarg_exact_matched = False
        self.sort_key = tk.StringVar()
        self.sort_key.set(gv.def_sort_key)
        self.sort_dir = True
        self.total_sort = False
        
        self.as_of_var = tk.StringVar()
        self.glaarg_as_of_var = tk.StringVar()
        self.ur_call_var = tk.StringVar()
        self.ur_county_var = tk.StringVar()
        self.ur_state_var = tk.StringVar()
        self.ur_session_count_var = tk.StringVar()
        self.ur_accreditation = tk.StringVar()
        
        self.their_call_var = tk.StringVar()
        self.their_county_var = tk.StringVar()
        self.their_state_var = tk.StringVar()
        self.their_session_count_var = tk.StringVar()
        self.their_accreditation = tk.StringVar()
        self.their_lookup_var = tk.StringVar()
        self.glaarg_their_lookup_var = tk.StringVar()
        self.glaarg_their_call_var = tk.StringVar()
        self.glaarg_their_session_count_var = tk.StringVar()
        self.glaarg_helped_var = tk.StringVar()
        self.glaarg_overseen_var = tk.StringVar()
        self.glaarg_new_license_var = tk.StringVar()
        self.glaarg_upgrades_var =tk.StringVar()
        
        
        ## Let's start the window in the center of the desktop screen
        window_height = 700
        window_width = 1400
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_cordinate = int((screen_width/2) - (window_width/2))
        y_cordinate = int((screen_height/2) - (window_height/2))
        self.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
        
        self.style = ttk.Style()
        self.style.theme_use("clam")
        
        
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.columnconfigure(2, weight=1)

        self.rowconfigure(0,weight=1)
        self.rowconfigure(1,weight=1)
        self.rowconfigure(2,weight=24)
        self.rowconfigure(3,weight=6)
        self.rowconfigure(4,weight=1)
        
        #print("Setting up menu")
        self.set_menu()
        #print("Setting up entries")
        self.set_up_ur_entries()
        #print("Setting up GUI")
        self.set_gui()
        #print("Refresh database")
        self.refresh_database()
        
    def set_menu(self):
        self.menubar = tk.Menu(self)
        self.filemenu = tk.Menu(self.menubar, tearoff = 0)
        self.filemenu.add_command(label="Import/Update ARRL Session Counts",command=lambda: self.get_arrl_data())
        self.filemenu.add_command(label="Import/Update ARRL by State", command=lambda: rs.read_state_file(self))
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Import/Update GLAARG Session Counts",command=lambda: self.get_glaarg_data())
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Set Defaults", command=lambda: sud.set_defaults(self))
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Reset database",command=lambda: self.reset_database())
        self.filemenu.add_separator()
        self.filemenu.add_command(label="Exit", command=self.goodbye)
        
        ## menu items for reports
        ##
        self.reportmenu = tk.Menu(self.menubar, tearoff = 0)
        self.reportmenu.add_command(label="ARRL Session Count Summary", command=lambda: scd.session_count_data(self))
        self.reportmenu.add_command(label="ARRL Session Count Detailed", command=lambda: dcd.detailed_count_data(self))
        self.reportmenu.add_separator()
        self.reportmenu.add_command(label="GLAARG Session Count Summary", command=lambda: gls.session_count_data(self))
        self.reportmenu.add_command(label="GLAARG Session Count Detailed", command=lambda: gld.detailed_count_data(self))
        self.reportmenu.add_separator()
        self.reportmenu.add_command(label="Other Session Counts - All", command=lambda: rt.read_text_file(self,'1'))
        self.reportmenu.add_command(label="Other Session Counts - ARRL Only", command=lambda: rt.read_text_file(self,'2'))
        self.reportmenu.add_command(label="Other Session Counts - GLAARG Only", command=lambda: rt.read_text_file(self,'3'))
        
        
        self.helpmenu = tk.Menu(self.menubar, tearoff = 0)
        self.helpmenu.add_command(label="About", command=self.about)
        
        self.menubar.add_cascade(label="File", menu = self.filemenu)
        self.menubar.add_cascade(label="Reports", menu = self.reportmenu)
        self.menubar.add_cascade(label="About", menu = self.helpmenu)
        self.config(menu = self.menubar)
        
        ## GUI widgets
    
    def set_gui(self):
        
        ## Labels for areas
        self.list_label = tk.Label(self, text="Results")
        self.list_label.grid(row=0, column=2, sticky='ne', padx=(10,350), pady=(10,10))
        
        self.result_text = tk.Text(self)
        self.result_text.grid(column=2, row=1, pady=(10,10), padx=(20,30), sticky='nes')
        self.result_text.configure(background="#d8f8d8", wrap="word", height=38, width=90,fg="#000000")
        self.result_text.delete(1.0,tk.END)
        self.text_scroll = ttk.Scrollbar(self, orient=tk.VERTICAL, command=self.result_text.yview)
        self.text_scroll.grid(column=2, row=1, sticky='nse', rowspan=20, pady=4, padx=(10,10))
        self.result_text['yscrollcommand'] = self.text_scroll.set
        
        self.urframe = tk.Frame(self)
        self.urframe.grid(row=0, column=0, rowspan=20, sticky='nsew', padx=10, pady=(0,10))
        self.urframe.columnconfigure(0,weight=1)
        self.urframe.columnconfigure(0,weight=5)
        
        self.as_of_label = tk.Label(self.urframe, text='ARRL: ')
        self.as_of_label.grid(column=1, row=0, sticky='ne', padx=(5,5), pady=(5,5))
        self.as_of_entry = tk.Entry(self.urframe, textvariable = self.as_of_var, width=12, state='readonly')
        self.as_of_entry.grid(column=2, row=0, sticky='nw', padx=(5,5), pady=(5,5))
        self.as_or_glaarg_label = tk.Label(self.urframe, text="GLAARG: ")
        self.as_or_glaarg_label.grid(column=3, row=0, sticky='nw',padx=(5,5), pady=(5,5))
        self.as_of_glaarg_entry = tk.Entry(self.urframe, textvariable = self.glaarg_as_of_var, width=12, state='readonly')
        self.as_of_glaarg_entry.grid(column=3, row=0, sticky='ne', padx=(5,5), pady=(5,5))
        
        self.ur_call_label = tk.Label(self.urframe, text = 'Your Callsign')
        self.ur_call_label.grid(column=1, row=1, sticky='ne', padx=(5,5), pady=(5,5))
        self.ur_call_entry = tk.Entry(self.urframe, textvariable = self.ur_call_var, width=12, state='readonly')
        self.ur_call_entry.grid(column=2, row=1, sticky='nw', padx=(5,5), pady=(5,5))
        
        auto_row = 6
        
        self.spacer2_label = tk.Label(self.urframe, text=" ")
        self.spacer2_label.grid(column=0, row=auto_row, sticky='nw', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.their_lookup_button = tk.Button(self.urframe, text='Lookup Call', command=self.get_lookup_data)
        self.their_lookup_button.grid(column=2, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        self.their_lookup_entry = tk.Entry(self.urframe, textvariable=self.their_lookup_var, width=20)
        self.their_lookup_entry.grid(column=3, row=auto_row, sticky='nw', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.sp_label = tk.Label(self.urframe, text="ARRL Stats")
        self.sp_label.grid(column=1,row=auto_row, sticky='nw', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.their_call_label = tk.Label(self.urframe, text='Callsign')
        self.their_call_label.grid(column=2, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        self.their_call_entry = tk.Entry(self.urframe, textvariable = self.their_call_var, width=20)
        self.their_call_entry.grid(column=3, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.their_county_label = tk.Label(self.urframe, text = 'County')
        self.their_county_label.grid(column=2, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        self.their_county_entry = tk.Entry(self.urframe, textvariable = self.their_county_var, width=20)
        self.their_county_entry.grid(column=3, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.their_state_label = tk.Label(self.urframe, text = 'State')
        self.their_state_label.grid(column=2, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        self.their_state_entry = tk.Entry(self.urframe, textvariable = self.their_state_var, width=20)
        self.their_state_entry.grid(column=3, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.their_session_count_label = tk.Label(self.urframe, text = "Count")
        self.their_session_count_label.grid(column=2, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        self.their_session_count_entry = tk.Entry(self.urframe, textvariable = self.their_session_count_var, width=20)
        self.their_session_count_entry.grid(column=3, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.their_accreditation_label = tk.Label(self.urframe, text = 'Accredited')
        self.their_accreditation_label.grid(column=2, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        self.their_accreditation_entry = tk.Entry(self.urframe, textvariable = self.their_accreditation, width=20)
        self.their_accreditation_entry.grid(column=3, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.sp_label = tk.Label(self.urframe, text="GLAARG Stats")
        self.sp_label.grid(column=1,row=auto_row, sticky='nw', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.glaarg_their_call_label = tk.Label(self.urframe, text='Callsign')
        self.glaarg_their_call_label.grid(column=2, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        self.glaarg_their_call_entry = tk.Entry(self.urframe, textvariable = self.glaarg_their_call_var, width=20)
        self.glaarg_their_call_entry.grid(column=3, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.glaarg_their_session_count_label = tk.Label(self.urframe, text = "Count")
        self.glaarg_their_session_count_label.grid(column=2, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        self.glaarg_their_session_count_entry = tk.Entry(self.urframe, textvariable = self.glaarg_their_session_count_var, width=20)
        self.glaarg_their_session_count_entry.grid(column=3, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.glaarg_helped_label = tk.Label(self.urframe, text = "Helped")
        self.glaarg_helped_label.grid(column=2, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        self.glaarg_helped_entry = tk.Entry(self.urframe, textvariable = self.glaarg_helped_var, width=20)
        self.glaarg_helped_entry.grid(column=3,row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.glaarg_overseen_label = tk.Label(self.urframe, text = "Overseen")
        self.glaarg_overseen_label.grid(column=2, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        self.glaarg_overseen_entry = tk.Entry(self.urframe, textvariable = self.glaarg_overseen_var, width=20)
        self.glaarg_overseen_entry.grid(column=3,row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.glaarg_new_license_label = tk.Label(self.urframe, text = "New License")
        self.glaarg_new_license_label.grid(column=2, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        self.glaarg_new_license_entry = tk.Entry(self.urframe, textvariable = self.glaarg_new_license_var, width=20)
        self.glaarg_new_license_entry.grid(column=3,row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        auto_row += 1
        self.glaarg_upgrades_label = tk.Label(self.urframe, text = "Upgrades")
        self.glaarg_upgrades_label.grid(column=2, row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        self.glaarg_upgrades_entry = tk.Entry(self.urframe, textvariable = self.glaarg_upgrades_var, width=20)
        self.glaarg_upgrades_entry.grid(column=3,row=auto_row, sticky='ne', padx=(5,5), pady=(5,5))
        
        
        ## more fields can be added as needed
    
    def reset_database(self):
        answer = mb.askokcancel("Query","Doing this action will delete the database. Are you sure?")
        if answer: ## Clicked Okay
            os.remove(gv.asc_database_path)
            if os.path.exists(gv.temp_fetch_path):
                    os.remove(gv.temp_fetch_path)
            mb.showinfo("Finished","Database has been flushed.\nExit and restart the ASC-DB program to rebuild the database.\nRemember to run Set Defaults.\n")
        
    def refresh_database(self):
        db_connection = sqlite3.connect(gv.asc_database_path)
        db_cursor = db_connection.cursor()
        db_cursor.execute("SELECT * FROM settings")
        self.settings_check = db_cursor.fetchone()
        if len(gv.settings) == 0:
            self.ur_call_var.set(self.settings_check[1])
            self.as_of_var.set(self.settings_check[2])
            self.glaarg_as_of_var.set(self.settings_check[3])
        else:
            self.ur_call_var.set(gv.settings[1])
            self.as_of_var.set(gv.settings[2])
            self.glaarg_as_of_var.set(gv.settings[3])
        
        if self.running == False and self.settings_check[gv.cron_activate_flag] == '1':
            
            ## Inserting default auto-update values into the 'settings' table
            rec_cols = ', '.join(gv.settings_field_update_list)
            q_marks = ','.join(list('?'*len(gv.settings_field_update_list)))
            values = tuple(gv.settings_default_update_values)
            sql = "INSERT INTO settings ("+rec_cols+") VALUES ("+q_marks+")"
            sql_result = db_cursor.execute(sql,values)
            ## commit insert
            db_connection.commit()
        
        ## Do not invoke the auto-update until parameters are set
        elif self.settings_check[gv.cron_activate_flag] == '1' and self.running : 
            if self.update_db_obj == None: ## thread obj has not been initialized
                self.update_db_obj = Update(self, self.run_auto_update,self.result_text,gv.cron_string) ## Pass the parameters
                self.update_db_obj.start()
                self.update_idletasks()
        else:
            ## do these following items only if the thread is running
            if self.update_db_obj != None: ## object was initialized
                self.update_db_obj.stop()
                event.set() ## force threading event to release
                self.update_db_obj = None
                self.running = False
            ## Inserting default values into the 'settings' table
            tmp_sql = ""
            for item in gv.settings_field_update_list:
                tmp_sql += item+'= ?, '
            tmp_sql = tmp_sql[:-2]
            values = tuple(gv.settings_default_update_values)
            sql = "UPDATE settings SET "+tmp_sql
            db_cursor.execute(sql,values)
            
            ## commit insert
            db_connection.commit()
            
        db_connection.close()   
            
    def run_auto_update(self):
        self.get_quiet_arrl_data()

    def get_quiet_arrl_data(self):
        for state in gv.states_list:
            website = gv.arrl_url + state
            rsc.get_count(self,state)
        ## update GUI
        today_date = str(date.today())
        self.as_of_var.set(today_date)   
        self.update_idletasks()
        
    def get_arrl_data(self):
        ARRL_start = ""
        start_flag = True
        ## Did we get interrupted during an import / update
        if os.path.isfile(gv.temp_fetch_path):
            with open(gv.temp_fetch_path,'r') as gs:
                ## read in the last state being fetched
                ARRL_start = gs.read()
        self.result_text.delete(1.0,tk.END)
        for state in gv.states_list:
            if len(ARRL_start) != 0 and state != ARRL_start and start_flag:
                continue
            start_flag = False
            website = gv.arrl_url + state
            text = "Importing from URL: "+website+'\n'
            with open(gv.temp_fetch_path,'w') as gs:
                gs.write(state)
            self.result_text.insert(tk.END,text)
            self.result_text.yview(tk.END)
            self.update_idletasks()
            rsc.get_count(self,state)
        text = "Finished."
        ## remove temp file
        os.remove(gv.temp_fetch_path)
        self.result_text.insert(tk.END,text)
        ## update GUI
        today_date = str(date.today())
        self.as_of_var.set(today_date)
        self.update_idletasks()
        
    def get_glaarg_data(self):
        ## Clear the text box
        self.result_text.delete(1.0,tk.END)
        website = gv.glaarg_url
        mb.showinfo("GLAARG Import/Update","The GLAARG website will take some time to complete the import/update. Please wait for the 'Finished!' message.")
        text = "Importing GLAARG stats ...\n"
        self.result_text.insert(tk.END,text)
        self.update_idletasks()
        error_status = rg.get_count(self)
        if error_status:
            mb.showerror("Error","Problem obtaining data from GLAARG website.")
        else:
            mb.showinfo("GLAARG Import/Update","Import/Update is Finished!")
        
        ##
        ## Clear the text box
        self.result_text.delete(1.0,tk.END)
        ## update GUI
        today_date = str(date.today())
        self.glaarg_as_of_var.set(today_date)
        self.update_idletasks()
            
    def get_state_data(self):
        db_connection = sqlite3.connect(gv.asc_database_path)
        db_cursor = db_connection.cursor()

        db_cursor.execute("SELECT * FROM settings")
        setting = db_cursor.fetchone()
        db_connection.close()
        self.result_text.delete(1.0,tk.END)
        state = setting[3]
        website = gv.arrl_url + state
        text = "Importing from URL: "+website+'\n'
        self.result_text.insert(tk.END,text)
        self.update_idletasks()
        rsc.get_count(self,state)
        text = "Finished."
        self.result_text.insert(tk.END,text)
        self.update_idletasks()
    
    def set_up_ur_entries(self):
        self.get_data()
        self.ur_call_var.set(gv.settings[1])
        self.as_of_var.set(gv.settings[2])
        self.ur_county_var.set(gv.ve_stat[1])
        self.ur_state_var.set(gv.ve_stat[4])
        self.ur_session_count_var.set(gv.ve_stat[3])
        self.ur_accreditation.set(gv.ve_stat[2])
        
        self.their_call_var.set('')
        self.their_county_var.set('')
        self.their_state_var.set('')
        self.their_session_count_var.set('')
        self.their_accreditation.set('')

    def get_lookup_data(self):
        tmp_list = []
        self.exact_matched = False
        sql_text = "SELECT * FROM ve_count WHERE call LIKE ?"
        glaarg_sql_text = "SELECT * FROM glaarg_count WHERE csign LIKE ?"
        self.lookup_callsign = self.their_lookup_var.get()
        self.glaarg_their_lookup_var.set(self.lookup_callsign)
        ## was button clicked without entering a callsign?
        if self.lookup_callsign == 'NOCALL':
            return
        elif len(self.lookup_callsign) == 0:
            ## Do a self look-up
            self.lookup_callsign = self.ur_call_var.get()+'!'
            self.result_text.delete(1.0,tk.END)
        ## check for no wildcard match condition
        if self.lookup_callsign[-1] == '!':
            self.shebang = True
            self.exact_matched = False
            self.glaarg_exact_matched = False
            ls = self.lookup_callsign[:-1]
            self.lookup_callsign = ls
        lup_callsign = '%'+self.lookup_callsign.upper()+'%'
        db_connection = sqlite3.connect(gv.asc_database_path)
        db_cursor = db_connection.cursor()
        
        tmp_list.append(lup_callsign)
        try:
            db_cursor.execute(sql_text,tuple(tmp_list))
            arrl_check = db_cursor.fetchall()
            #print("ARRL: ",arrl_check)
            if len(arrl_check) == 0:
                arrl_check = None
        except:
            arrl_check = None
        
        try:    
            db_cursor.execute(glaarg_sql_text, tuple(tmp_list))
            glaarg_check = db_cursor.fetchall()
            #print("GLAARG: ",glaarg_check)
            if len(glaarg_check) == 0:
                glaarg_check = None
        except:
            glaarg_check = None
            
        sql_match = 'SELECT * FROM ve_count WHERE id = ?'
        glaarg_sql_match = 'SELECT * from glaarg_count WHERE id = ?'
        tmp_list = []
        
        ## ARRL record [call,county,accreditation date,count]
        self.their_lookup_var.set('')
        if arrl_check != None:
            for record in arrl_check:
                exact_match = record[1].split(' ')
                if exact_match[0] == self.lookup_callsign.upper() and self.shebang:
                    self.exact_matched = True
                    tmp_list.append(record[0])
                    try:
                        db_cursor.execute(sql_match,tuple(tmp_list))
                        arrl_check = db_cursor.fetchall()
                    except:
                        arrl_check = None
                    break
        
        ## GLAARG record ['ve_num','csign','ve_name','sess_ct','helped','overseen','new_lic','upgrades']  
        self.glaarg_their_lookup_var.set('')
        tmp_list = []
        if glaarg_check != None:
            for record in glaarg_check:
                #print("record: ",record)
                exact_match = record[2]
                #print("exact_match: ",exact_match)
                #print("lookup_callsign: ",self.lookup_callsign.upper())
                #print("shebang: ",self.shebang)
                if (exact_match == self.lookup_callsign.upper()) and self.shebang:
                    self.glaarg_exact_matched = True
                    #print("exact_matched: ",self.glaarg_exact_matched)
                    tmp_list.append(record[0])
                    try:
                        #print("Record: ",tmp_list)
                        db_cursor.execute(glaarg_sql_match,tuple(tmp_list))
                        glaarg_check = db_cursor.fetchall()
                    except:
                        glaarg_check = None
                    break
            #else:
            #    break   
        
        db_connection.close()
        #self.update_idletasks()
        self.result_text.delete(1.0,tk.END)
        if arrl_check != None:
            if len(arrl_check) == 1 or self.exact_matched:
                ## ARRL record ['call','county','accredit','scount','state']
                record = arrl_check[0]
                self.their_call_var.set(record[1])
                self.their_county_var.set(record[2])
                self.their_state_var.set(record[5])
                self.their_session_count_var.set(record[4])
                self.their_accreditation.set(record[3])
            elif len(arrl_check) > 1:
                self.their_call_var.set('')
                self.their_county_var.set('')
                self.their_state_var.set('')
                self.their_session_count_var.set('')
                self.their_accreditation.set('')
                ## sort on session count, descending order
                arrl_check.sort(key=lambda tup_var: tup_var[4], reverse = True)
                self.result_text.delete(1.0,tk.END)
                text_line = "ARRL Stats\n"
                #print("text_line: ",text_line)
                self.result_text.insert(tk.END,text_line)
                self.update_idletasks()
                for r in arrl_check:
                    text_line = "Count:{}, Call:{}, County:{}, State:{}, Accredited:{}\n".format(r[4],r[1],r[2],r[5],r[3])
                    self.result_text.insert(tk.END,text_line)
                    
        #if self.lookup_callsign.upper() == 'NOCALL':
        #    pass
        elif arrl_check == None or (self.exact_matched == False and self.shebang):
            #self.result_text.delete(1.0,tk.END)
            self.their_call_var.set('')
            self.their_county_var.set('')
            self.their_state_var.set('')
            self.their_session_count_var.set('')
            self.their_accreditation.set('')
            text = "Callsign {} was not found in ARRL listing!".format(self.lookup_callsign.upper())+'\n'
            self.result_text.insert(tk.END,text)
            self.update_idletasks()
            
        ## Do GLAARG report 
        #if len(glaarg_check) == 0:
        #    glaarg_check = None
            
        if glaarg_check != None:
            if len(glaarg_check) == 1 or self.glaarg_exact_matched:
                ## GLAARG record  ['ve_num','csign','ve_name','sess_ct','helped','overseen','new_lic','upgrades']
                record = glaarg_check[0] ## extract tuple
                #print("record:: ",record)
                self.glaarg_their_call_var.set(record[2])
                self.glaarg_their_session_count_var.set(record[4])
                self.glaarg_helped_var.set(record[5])
                self.glaarg_overseen_var.set(record[6])
                self.glaarg_new_license_var.set(record[7])
                self.glaarg_upgrades_var.set(record[8])
                
                ## can add more as needed
            elif len(glaarg_check) > 1:
                #print("Multi")
                self.glaarg_their_call_var.set('')
                self.glaarg_their_session_count_var.set('')
                self.glaarg_helped_var.set('')
                self.glaarg_overseen_var.set('')
                self.glaarg_new_license_var.set('')
                self.glaarg_upgrades_var.set('')
                glaarg_check.sort(key=lambda tup_var: tup_var[4], reverse = True)
                text_line = "\nGLAARG Stats\n"
                self.result_text.insert(tk.END,text_line)
                #self.update_idletasks()
                #print("glaarg_check: ",glaarg_check)
                for r in glaarg_check:
                    text_line = "Count:{}, Call:{}, Name:{}, Helped:{}, Overseen:{}, New License:{}, Upgrades:{}\n".format(r[4],r[2],r[3],r[5],r[6],r[7],r[8])
                    #print("r: ",text_line)
                    self.result_text.insert(tk.END,text_line)
                    
        #if self.lookup_callsign.upper() == 'NOCALL':
        #    pass
        elif glaarg_check == None or (self.glaarg_exact_matched == False and self.shebang):
            #print("glaarg_check",glaarg_check)
            self.glaarg_their_call_var.set('')
            self.glaarg_their_session_count_var.set('')
            self.glaarg_helped_var.set('')
            self.glaarg_overseen_var.set('')
            self.glaarg_new_license_var.set('')
            self.glaarg_upgrades_var.set('')
            #self.result_text.delete(1.0,tk.END)
            text = "Callsign {} was not found in GLAARG listing!".format(self.lookup_callsign.upper())+'\n'
            self.result_text.insert(tk.END,text)
            
                
        self.shebang = False
        self.update_idletasks()
    
    def get_data(self):
        tmp_list = []
        db_connection = sqlite3.connect(gv.asc_database_path)
        db_cursor = db_connection.cursor()

        db_cursor.execute("SELECT * FROM settings")
        gv.settings = db_cursor.fetchone()
        try:
            callsign = '%'+gv.settins[1]+'%'
            tmp_list.append(callsign)
            sql = "SELECT * FROM ve_count WHERE call LIKE ?"
            db_cursor.execute(sql,tuple(tmp_list))
            gv.ve_stat = db_cursor.fetchall()
            ## remove sql reference to record
            gv.ve_stat.pop(0)
        except:
            gv.ve_stat = ['NO-CALL','NO-COUNTY','NO-ACCREDITATION','NO-COUNT','NO-STATE']
        
        db_connection.close()
    
    def toggle_dir(self): ## used in detailed_count_display()
        if self.sort_dir:
            self.sort_dir = False
        else:
            self.sort_dir = True
        
    def goodbye(self):
        if self.update_db_obj != None:
            self.update_db_obj.stop()
            event.set() ## force threading event to release
        sys.exit()
        
    def about(self):
        info = gv.program+"\n\n"
        info += "Version: "+gv.version+'\n\n'
        info += "Written by Thomas Kocourek, N4FWD\n\n"
        info += "Copyright 2023"+'\n\n'
        info += "Released under the GNU 3 License \n\n"
        mb.showinfo('About',info)   

def main():
    ## set-up database. adb is imported at beginning of this file
    environment = adb.setup()
    if not environment:
        rw = tk.Tk()
        rw.overrideredirect(1)
        rw.withdraw()
        mb.showwarning('Error','Problem with database or environment or permissions!\nTry restarting program.')
        rw.destroy()
        sys.exit()
    app = App()
    app.mainloop()
    
if __name__ == '__main__':
    main()