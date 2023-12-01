## Copyright 2023 by Thomas Kocourek, N4FWD

## program vars
program = "Another Session Count for VEs"
version = "1.2.1"

top_window_x = 1280
top_window_y = 700
platform_os = ""

asc_dir = "ASC"
first_pass = True

report_dir = "REPORTS"
asc_database_name = 'asc.db'
temp_database_name = 'temp.db'
ARRL_fetch_state = 'ARRL_fetch.txt'
target_name = 'import-update-by-state.txt'
## path to the database file which is set in 'arrl_db_setup.py'
asc_database_path = ""
temp_database_path = ""
base_rpt_dir = ""
temp_fetch_path = ""
## tables names = 've_count' & 'glaarg_count'

states_list = ['AK','AL','AR','AZ','CA','CO','CT','DC','DE','FL','GA','HI','IA','ID','IL','IN','KS','KY','LA','MA','MD','ME','MI','MN','MO','MS','MT','NC','ND','NE','NH','NJ','NM','NV','NY','OH','OK','OR','PA','PR','RI','SC','SD','TN','TX','UT','VA','VT','WA','WI','WV','WY']

arrl_url = "https://www.arrl.org/ve-session-counts?call_sign=&state="  ## needs State appended to complete the URL
glaarg_url = "https://glaarg.org/session-stats/"
glaarg_mode = False

settings_field_list = ['yourcall','date','defaultState','autoflag','cronMin','cronHr','cronDom','cronMon','cronDow']
settings_field_list_glaarg = ['yourcall','date','gl_date','defaultState','autoflag','cronMin','cronHr','cronDom','cronMon','cronDow']
settings_field_update_list = ['autoflag','cronMin','cronHr','cronDom','cronMon','cronDow']
settings_default_values = ['NOCALL','NotYet','GA','0','0','3','*','*','*']
settings_default_values_glaarg = ['NOCALL','NotYet','NotYet','GA','0','0','3','*','*','*']
settings_default_update_values = ['0','0','3','*','*','*']
settings = []
set_tmp = []
ve_stat = []

gl_field_list = ['ve_num','csign','ve_name','sess_ct','helped','overseen','new_lic','upgrades','tag']
gl_input_list = ['ve_num','csign','ve_name','sess_ct','helped','overseen','new_lic','upgrades']
ve_field_list = ['call','county','accredit','scount','state','tag']
ve_input_list = ['call','county','accredit','scount']

def_sort_key = '0'

default_state = ""
default_auto = "Disabled"

month_selection_list = ['*','January','February','March','April','May','June','July','August','September','October','November','December']
month_selection_dict = {'January':'1','February':'2','March':'3','April':'4','May':'5','June':'6','July':'7','August':'8','September':'9','October':'10','November':'11','December':'12','*':'*'}
month_reverse_dict={'1':'January','2':'February','3':'March','4':'April','5':'May','6':'June','7':'July','8':'August','9':'September','10':'October','11':'November','12':'December','*':'*'}
minute_selection_list = ['0','5','10','15','20','25','30','35','40','45','50','55']
hour_selection_list = ['0','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23']
## use input via 'Entry' widget for day of month
day_of_week_selection_list = ['*','Sunday','Monday','Tuesday','Wednesday','Thursday','Friday','Saturday']
day_of_week_selection_dict ={'Sunday':'0','Monday':'1','Tuesday':'2','Wednesday':'3','Thursday':'4','Friday':'5','Saturday':'6','*':'*'}
dow_reverse_dict={'0':'Sunday','1':'Monday','2':'Tuesday','3':'Wednesday','4':'Thursday','5':'Friday','6':'Saturday','*':'*'}

day_of_month_selection_list = ['*','1','2','3','4','5','6','7','8','9','10','11','12','13','14','15','16','17','18','19','20','21','22','23','24','25','26','27','28']

select_report_list = ['State Higher','State Equal','State Lower','Total Higher','Total Equal','Total Lower']
select_report_list_default = 'State Higher'
glaarg_select_report_list = ['Total Higher','Total Equal','Total Lower']
glaarg_select_report_list_default = 'Total Higher'

cron_string = "0 3 * * *"
cron_activate_flag = 5

## radio button parameters based on sort of report
rb_cols = [('session','4',0),('county','2',80)] 
def_sort_key = '4'
glaarg_cols = [('glaarg session count','4',0),('Callsign','2',80)]
glaarg_default_sort_key = '4'

timing_start = 0
timing_end = 0
