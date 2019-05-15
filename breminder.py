#!/usr/bin/env python
# -*- coding: utf8 -*-

import pandas as pd
import re
import numpy as np
import smtplib
import datetime

# Start debugging server
# python -m smtpd -c DebuggingServer -n localhost:1025

file_name='bday.txt'
df= pd.read_csv(file_name, header = None,keep_default_na=False) #keep_default_na=False empty instead of NaN
df.columns=['Name','Email','Birth day']

def validate_mail():
    lst=[]
    for i in df['Email']:        
        matchmail=re.search(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]{2,}$)',i)
        try:
            lst.append(matchmail.group())
        except:lst.append(np.nan)
    return lst

def validate_bday():
    lst=[]
    for i in df['Birth day']:
        if len(re.findall(r'\d{4}-\d{2}-\d{2}' ,i))>0:            
            try:
                date_of_birth = datetime.datetime.strptime(i, "%Y-%m-%d")
                lst.append(date_of_birth)            
            except:
                lst.append(np.nan)
        elif len(re.findall(r'\d{2}-\d{2}',i))>0:            
            try:
                date_of_birth = datetime.datetime.strptime(i, "%m-%d")
                lst.append(date_of_birth)            
            except:
                lst.append(np.nan)
        else: lst.append(np.nan)      
    return lst

def validate_name():
    lst=[]
    for i in df['Name']:
        if len(re.findall(r'^[a-zA-Z]+(([,. -][a-zA-Z ])?[a-zA-Z]*)*$' ,i))>0:    
            lst.append(i)
        else:
            lst.append(np.nan)
    return lst       

df['valid_name'] = pd.Series(validate_name()).values
df['valid_mail'] = pd.Series(validate_mail()).values
df['valid_date'] = pd.Series(validate_bday()).values        #datetime64[ns]
df['week_ahead']=df['valid_date']+pd.DateOffset(7)
df['week_ahead_str']=df['week_ahead'].dt.strftime('%m-%d')
bb=df[['valid_name','valid_date']].loc[df['week_ahead_str'] == datetime.datetime.now().strftime('%m-%d')]

sendmail=df[['Email','Name','valid_mail','valid_name','valid_date']].loc[(df['week_ahead_str'] != datetime.datetime.now().strftime('%m-%d')) & (df['valid_mail'].notnull()) & (df['valid_name'].notnull())]

n=0
while n in range(0,len(bb)):     
    for ii in sendmail.itertuples(index=False):        
        msg= Parser(policy=default).parsestr(
            'From: Foo Bar <user@test.com>\n'
            'To: {}\n'
            'Subject: Birthday Reminder: {}s\'s birthday on {}\n'
            '\n'
            'Hi {},\n This is a reminder that {}(name_of_birthday_person)s will be celebrating their birthday on {}(date)s.'
            .format(ii.Email,bb.valid_name.iloc[n],bb.valid_date.iloc[n],ii.Name,bb.valid_name.iloc[n],bb.valid_date.dt.strftime('%m-%d').iloc[n]))
        try:
            # Send the message via our own SMTP server.
            s = smtplib.SMTP('localhost:1025')
            s.send_message(msg)
            s.quit()  
            print ("Successfully sent email")
        except :
           print ("Error: Unable to send email")
    n+=1
