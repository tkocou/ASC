## Copyright 2023 by Thomas Kocourek, N4FWD

import tkinter as tk
from tkinter import ttk
from tkinter import messagebox as mb

import sqlite3
import global_var as gv

def set_defaults(self):
    
    self.topper = tk.Toplevel(self)
    self.topper.title("Default Selections")
    self.topper.configure(bg="#b7d7c7")
    
    window_height = gv.top_window_y
    window_width = gv.top_window_x
    if gv.platform_os == "Darwin":
        self.topper.resizable(True, True)
        self.topper.minsize(gv.top_window_x,gv.top_window_y)
        self.topper.maxsize(gv.top_window_x,gv.top_window_y)
        
    screen_width = self.topper.winfo_screenwidth()
    screen_height = self.topper.winfo_screenheight()
    x_cordinate = int((screen_width/2) - (window_width/2))
    y_cordinate = int((screen_height/2) - (window_height/2))
    self.topper.geometry("{}x{}+{}+{}".format(window_width, window_height, x_cordinate, y_cordinate))
    
    self.topper.columnconfigure(0,weight=1)
    self.topper.columnconfigure(1,weight=1)
    self.topper.columnconfigure(2,weight=1)
    self.topper.columnconfigure(3,weight=1)
    self.topper.columnconfigure(4,weight=1)
    
    self.topper.rowconfigure(0,weight=1)
    self.topper.rowconfigure(1,weight=1)
    self.topper.rowconfigure(2,weight=1)
    self.topper.rowconfigure(3,weight=24)

    self.yourcall_var = tk.StringVar()
    self.date_var = tk.StringVar()
    self.defaultState = tk.StringVar()
    self.autoFlag = tk.StringVar()
    self.cronMin = tk.StringVar()
    self.cronHr = tk.StringVar()
    self.cronDom = tk.StringVar()
    self.cronMon = tk.StringVar()
    self.cronDow = tk.StringVar()
    
    db_connection = sqlite3.connect(gv.asc_database_path)
    db_cursor = db_connection.cursor()

    db_cursor.execute("SELECT * FROM settings")
    gv.set_tmp = db_cursor.fetchone()
    
    self.yourcall_var.set(gv.set_tmp[1])
    self.set_call_label = tk.Label(self.topper, text = 'Your Callsign')
    self.set_call_label.grid(column=0, row=0, sticky='nw', padx=(5,20), pady=(5,5))
    self.set_callsign_entry = tk.Entry(self.topper,textvariable=self.yourcall_var, width=8)
    self.set_callsign_entry.grid(column=0, row=0, sticky='nw', padx=(120,5), pady=(5,5))
    
    self.defaultState.set(gv.set_tmp[4])
    self.set_state_label = tk.Label(self.topper, text = 'Your State')
    self.set_state_label.grid(column=1, row=0, sticky='nw', padx=(5,20), pady=(5,5))
    self.set_state_entry = tk.Entry(self.topper,textvariable=self.defaultState, width = 3)
    self.set_state_entry.grid(column=1, row=0, sticky='nw', padx=(120,5), pady=(5,5))
    
    auto_flag = ""
    
    self.auto_flag_label = tk.Label(self.topper, text = '<- Auto Update')
    self.auto_flag_label.grid(column=0, row=1, sticky='nw', padx=(120,5), pady=(5,5))
    
    self.auto_flag_combo = ttk.Combobox(self.topper, width=8, textvariable=self.autoFlag)
    self.auto_flag_combo.grid(column=0, row=1, sticky='nw', padx=(10,5), pady=(5,5))
    self.auto_flag_combo['values'] = ('Disabled','Enabled')
    self.auto_flag_combo['state'] = 'readonly'
    self.auto_flag_combo.set(gv.default_auto)
    
    self.save_setting_button = tk.Button(self.topper, text="Save Settings", command = lambda: save_settings(self))
    self.save_setting_button.grid(column=1, row=1, sticky='nw', padx=(5,5), pady=(5,5))
    
    self.cancel_setting_button = tk.Button(self.topper, text="Cancel Changes", command = self.topper.destroy)
    self.cancel_setting_button.grid(column=2, row=1, sticky='nw', padx=(5,5), pady=(5,5))
    
    self.title_label = tk.Label(self.topper, text = "Auto-Fetch parameters in box below")
    self.title_label.grid(column=1, row=2, sticky='ew',padx=(5,5), pady=(5,5))
    
    self.theframe = tk.Frame(self.topper)
    self.theframe.grid(row=3, column=0, columnspan=3, rowspan=20, sticky='nsew', padx=(70,20), pady=(0,10))
    self.theframe.columnconfigure(0,weight=1)
    self.theframe.columnconfigure(1,weight=5)
    self.theframe.columnconfigure(2,weight=5)
    self.theframe.columnconfigure(3,weight=5)
    self.theframe.columnconfigure(4,weight=5)
    
    self.auto_flag_label = tk.Label(self.theframe, text = 'Minute')
    self.auto_flag_label.grid(column=0, row=0, sticky='nw', padx=(50,20), pady=(5,5))
    
    self.minute_select_combo = ttk.Combobox(self.theframe, width=3, textvariable=self.cronMin)
    self.minute_select_combo.grid(column=0, row=0, sticky='nw', padx=(120,5), pady=(5,5))
    self.minute_select_combo['values'] = tuple(gv.minute_selection_list)
    self.minute_select_combo['state'] = 'readonly'
    self.minute_select_combo.set(gv.set_tmp[6])
    
    self.hour_select_label = tk.Label(self.theframe, text = 'Hour')
    self.hour_select_label.grid(column=1, row=0, sticky='nw', padx=(5,20), pady=(5,5))
    
    self.hour_select_combo = ttk.Combobox(self.theframe, width=3, textvariable=self.cronHr)
    self.hour_select_combo.grid(column=1, row=0, sticky='nw', padx=(70,5), pady=(5,5))
    self.hour_select_combo['values'] = tuple(gv.hour_selection_list)
    self.hour_select_combo['state'] = 'readonly'
    self.hour_select_combo.set(gv.set_tmp[7])
    
    self.dom_select_label = tk.Label(self.theframe, text = 'Day of Month')
    self.dom_select_label.grid(column=2, row=0, sticky='nw', padx=(5,20), pady=(5,5))
    
    self.dom_select_combo = ttk.Combobox(self.theframe, width=3, textvariable=self.cronDom)
    self.dom_select_combo.grid(column=2, row=0, sticky='nw', padx=(130,5), pady=(5,5))
    self.dom_select_combo['values'] = tuple(gv.day_of_month_selection_list)
    self.dom_select_combo['state'] = 'readonly'
    self.dom_select_combo.set(gv.set_tmp[8])
    
    self.month_label = tk.Label(self.theframe, text = 'Month')
    self.month_label.grid(column=3, row=0, sticky='nw', padx=(5,20), pady=(5,5))
    
    self.month_select_combo = ttk.Combobox(self.theframe, width=10, textvariable=self.cronMon)
    self.month_select_combo.grid(column=3, row=0, sticky='nw', padx=(75,5), pady=(5,5))
    self.month_select_combo['values'] = tuple(gv.month_selection_list)
    self.month_select_combo['state'] = 'readonly'
    self.month_select_combo.set(gv.month_reverse_dict[gv.set_tmp[9]])
    
    self.dow_label = tk.Label(self.theframe, text = 'Day of Week')
    self.dow_label.grid(column=4, row=0, sticky='nw', padx=(5,20), pady=(5,5))
    
    self.dow_select_combo = ttk.Combobox(self.theframe, width=10, textvariable=self.cronDow)
    self.dow_select_combo.grid(column=4, row=0, sticky='nw', padx=(120,5), pady=(5,5))
    self.dow_select_combo['values'] = tuple(gv.day_of_week_selection_list)
    self.dow_select_combo['state'] = 'readonly'
    self.dow_select_combo.set(gv.dow_reverse_dict[gv.set_tmp[10]])
    
def save_settings(self):
    db_connection = sqlite3.connect(gv.asc_database_path)
    db_cursor = db_connection.cursor()
    setting_list = []
    gv.cron_string = ""
    setting_list.append(self.yourcall_var.get().upper()) ## update callsign
    setting_list.append(gv.set_tmp[2]) ## save date for database 've_count'
    setting_list.append(gv.set_tmp[3]) ## save date for 'glaarg'
    setting_list.append(self.defaultState.get()) ## update state
    
    fetch_flag = self.auto_flag_combo.get()
    if fetch_flag == 'Disabled':
        setting_list.append('0')
        gv.default_auto = "Disabled"
        self.running = False
    elif fetch_flag == 'Enabled':
        setting_list.append('1')
        gv.default_auto = "Enabled"
        self.running = True
    setting_list.append(self.minute_select_combo.get())
    gv.cron_string += self.minute_select_combo.get()+' '
    setting_list.append(self.hour_select_combo.get())
    gv.cron_string += self.hour_select_combo.get()+' '
    setting_list.append(self.dom_select_combo.get())
    gv.cron_string += self.dom_select_combo.get()+' '
    
    temp_var = self.month_select_combo.get()
    if temp_var != '*':
        setting_list.append(gv.month_selection_dict[self.month_select_combo.get()])
        gv.cron_string += gv.month_selection_dict[self.month_select_combo.get()]+' '
    else:
        setting_list.append('*')
        gv.cron_string += '* '
        
    temp_var = self.dow_select_combo.get()
    if temp_var != '*':
        setting_list.append(gv.day_of_week_selection_dict[self.dow_select_combo.get()])
        gv.cron_string += gv.day_of_week_selection_dict[self.dow_select_combo.get()]+' '
    else:
        setting_list.append('*')
        gv.cron_string += '*'

    tmp_sql = ""
    for item in gv.settings_field_list_glaarg:
        tmp_sql += item+'= ?, '
    tmp_sql = tmp_sql[:-2]
    values = tuple(setting_list)
    sql = "UPDATE settings SET "+tmp_sql
    db_cursor.execute(sql,values)
    db_connection.commit()
    db_cursor.execute("SELECT * FROM settings")
    set_tmp = db_cursor.fetchone()
    db_connection.close()
    ## Clean up and exit
    self.refresh_database()
    if setting_list[0] != "NOCALL":
        self.ur_call_var.set(setting_list[0])
    self.update_idletasks()
    self.topper.destroy()