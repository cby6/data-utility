import ibm_db_dbi
import pandas as pd

dir='/home/shared_folder/temp_bc/'
con = ibm_db_dbi.connect('DATABASE=wm;HOSTNAME=10.11.12.141;PORT=50000;PROTOCOL=TCPIP;UID=produser;PWD=d2a@ruStuC;','','')
con.set_autocommit(True)
cursor=con.cursor()
fd=open('{d}client.dat'.format(d=dir),'r')
client=fd.read().rstrip()
fd.close()
if client=='pxmca' or client=='hrpus' or client=='sofca':
    fd=open('{d}npe_final_framework.sql'.format(d=dir),'r')
elif client=='ncrca' or client=='accus' or client=='culci' or client=='ncrca_sm':
    fd=open('{d}npe_final_nwc.sql'.format(d=dir),'r')
else:
    fd=open('{d}npe_final.sql'.format(d=dir),'r')
sqlfile=fd.read()
fd.close()
sqlstring=sqlfile.split(';')
for sqlquery in sqlstring:
    query = ''.join(sqlquery).rstrip()
    if query:
#        print query
        cursor.execute(query.format(c=client))
con.close()
print "npe_final table has been updated"
