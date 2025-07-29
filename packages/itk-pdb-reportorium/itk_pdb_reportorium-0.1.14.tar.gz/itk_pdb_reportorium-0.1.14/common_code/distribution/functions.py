### imports
import os
import sys
import itkdb
from contextlib import closing
import paramiko
import numpy as np
from scp import SCPClient
from stat import S_ISDIR, S_ISREG
import smtplib 
import randomname
import csv
import datetime
import arakawa as dp
from email.mime.text import MIMEText

###################
### itkdb stuff
###################

### check environment for variables
def CheckEnv(ref):
    try:
        env=os.environ[ref]
        print(ref,"found :)")
        return env
    except KeyError:
        print(ref,"not found :(")
    return None


### get credentials (from environment)
def CheckCredential(ref):
    for r in [ref,ref.upper(),ref.lower()]:
        cred=CheckEnv(r)
        if cred!=None:
            return cred
    return None


### get itkdb client
def SetClient():
    ac1=CheckCredential("ac1")
    ac2=CheckCredential("ac2")
    if ac1==None:
        print("missing ac1 credential")
    if ac2==None:
        print("missing ac2 credential")
    if ac1==None or ac2==None:
        print("Please check credentials")
        sys.exit(1)

    print("Set up user:")
    user = itkdb.core.User(access_code1=ac1, access_code2=ac2)
    user.authenticate()
    myClient = itkdb.Client(user=user)
    print("\n###\n"+user.name+" your token expires in "+str(myClient.user.expires_in)+" seconds\n###")
    # return client
    return myClient

###################
### eos stuff
###################

### copy file to eos
def SendToEos(usr, pswd, eos_path, infile_path, rename=None):
    file_stats = os.stat(infile_path)
    print(f"Use file: {infile_path} ({file_stats.st_size/(1024 * 1024)} mb)")
    print(" - run ssh & sftp clients:")
    
    host = "lxplus.cern.ch"

    ssh_client = paramiko.client.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(host, username=usr, password=pswd)
    print(" - got ssh client")

    with ssh_client.open_sftp() as sftp:
        print(" - opened sftp")
        if rename==None:
            fileName=infile_path.split('/')[-1]
            print(f"    {infile_path} \n    >>> \n    {eos_path+fileName}")
            sftp.put(infile_path, eos_path+fileName)
        else:
            print(f" - use rename {rename}")
            print(f"    {infile_path} \n    >>> \n    {eos_path+rename}")
            sftp.put(infile_path, eos_path+rename)
        print(" - this worked!")

    ssh_client.close()

    return True


### copy multiple files to eos
def SendFileListEos(usr, pswd, eos_path, fileList, chunk=50):
    print(f"Copying {len(fileList)} files.")
    print(" - run ssh & sftp clients:")
    
    host = "lxplus.cern.ch"

    ssh_client = paramiko.client.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(host, username=usr, password=pswd)
    print(" - got ssh client")

    with ssh_client.open_sftp() as sftp:
        print(" - opened sftp")
        print(" - looping with chunks of {chunk}")
        for r in range(0,len(fileList),chunk):
            print(f"   - {r}:{r+chunk}")
            for e,fl in enumerate(fileList[r:r+chunk]):
                file_stats = os.stat(fl)
                print(f"    - {r+e}: {fl} ({file_stats.st_size/(1024 * 1024)} mb)")
                fileName=fl.split('/')[-1]
                print(f"    {fl} \n    >>> \n    {eos_path+fileName}")
                sftp.put(fl, eos_path+fileName)
                    
                print("    - this worked!")
                    
    return True


### get files on eos
def GetFileList(usr, pswd, eos_path):
    print(f"Check path file: {eos_path}")
    print("Run ssh & scp clients:")

    host = "lxplus.cern.ch"

    ### access eos
    client = paramiko.client.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(host, username=usr, password=pswd)

    ### sftp for listing 
    sftp = client.open_sftp()

    fileList=[] 
    for entry in sftp.listdir_attr(eos_path):
        mode = entry.st_mode
        if S_ISDIR(mode):
            print(entry.filename + " is folder")
        elif S_ISREG(mode):
            print(entry.filename + " is file")
            fileList.append(eos_path+entry.filename)

    return fileList


### get list link aliases from eos
def UseLinkList(usr, pswd, link):
    link_list_url="/eos/atlas/atlascerngroupdisk/det-itk/prod-db/reports/link_list.csv"
    print(f"Get link list file: {link_list_url}")
    print("Run ssh & scp clients:")

    host = "lxplus.cern.ch"

    ### set up client
    ssh_client = paramiko.client.SSHClient()
    ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh_client.connect(host, username=usr, password=pswd, timeout=10)
    print(" - got ssh client")

    with ssh_client.open_sftp() as sftp:
        print(" - opened sftp")

        with sftp.open(link_list_url, 'r') as f:
            print(" - found file!")
            # data = f.read()
            reader = csv.reader(f)
            # reconstructing the data as a dictionary 
            linkDict = {rows[0].strip():rows[1].strip() for rows in reader if len(rows)>0}

    # remove any ending slash (avoid duplicate entries)
    if link[-1]=="/":
        link=link[0:-1]
    # now check for link (or link with slash)
    # return link alias if already in values
    if link in linkDict.values() or link+"/" in linkDict.values():
        linkKey=list(linkDict.keys())[list(linkDict.values()).index(link)]
        print(f"Link {link} found: {linkKey}")
        # return new alias
        return linkKey
    # add link alias and return if not in values
    else:
        print(f"Link {link} not found. Add new entry")
        newKey=randomname.get_name(adj=('physics',), noun=('cats'))
        # get new alias if already used
        while (newKey in linkDict.keys()):
            newKey=randomname.get_name(adj=('physics',), noun=('cats'))
        # add alias to list
        with ssh_client.open_sftp() as sftp:
            print(" - opened sftp")
            with sftp.open(link_list_url, 'ab') as f:
                print(" - append file!")
                # f.write('{"'+newKey+'":"'+link+'"}\n')
                f.write(f'{newKey}, {link}\n')
                # return new alias
                return newKey
    ### plan-B
    print(" - thing has gone wrong here!")
    return None


### send email via gmail SMTP
def SendEmail(eDict): #subject, body, sender, recipients, password):
    msg = MIMEText(eDict['body'])
    msg['Subject'] = eDict['subject']
    msg['From'] = eDict['from']
    msg['To'] = eDict['to']
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp_server:
       smtp_server.login(eDict['from'], eDict['pwd'])
       smtp_server.sendmail(eDict['from'], eDict['to'], msg.as_string())
    print("Message sent!")

### a useful dictionary to map objects to arakawa 
dpMap={'plot':dp.Plot,'df':dp.DataTable,'table':dp.Table,'text':dp.Text}



### drop exrate data to save space
def TrimPlotData(plotObj):

    ### get encoding info.
    encObjList=[]
    ### encoding on top level of simple plot
    if "encoding" in plotObj.__dict__.keys():
        print(" - found encoding on top level")
        encObjList=[plotObj['encoding']]
    # maybe deeper level for complex plots
    else:
        print(" - no encoding found on top level. Digging...")
        ### digging through chart elements
        for d in plotObj.__dict__['_kwds'].keys():
            if d=="encoding":
                print("  - found {d} key")
                encObjList.append(plotObj.__dict__['_kwds'][d])
            if type(plotObj.__dict__['_kwds'][d])==type([]):
                for l in plotObj.__dict__['_kwds'][d]:
                    if "_kwds" not in l.__dict__.keys():
                        continue
                    print(l.__dict__['_kwds'].keys())
                    if "encoding" in l.__dict__['_kwds'].keys():
                        print(f"  - found encoding in {d} list")
                        encObjList.append(l.__dict__['_kwds']['encoding'])
    
    if len(encObjList)<1:
        print("No encoding information found. return original")
        return plotObj
    print(f" - found {len(encObjList)} encodings")

    ### define and populate new encoding dictionary
    print(f"Make list of encoding channels...")
    encList=[]
    # check encodings are loopable
    for encObj in encObjList:
    # loop over encodings
        if "_kwds" not in encObj.__dict__.keys():
            print(f"no \"_kwds\" key in encoding\n\t{encObj.__dict__.keys()}")
        for enc in encObj.__dict__['_kwds']:
            # print(enc)
            try:
                # print(f"{enc}: {encObj[enc]}, --> {type(encObj[enc])}" )
                if str(encObj[enc])!='Undefined':
                    if str(encObj[enc]['field'])!='Undefined':
                        encStr=encObj[enc]['field'].split(':')[0].split('(')[-1].split(')')[0]
                        print(f" - appending {enc} field:",encStr)
                        encList.append(encStr)
                    else:
                        if str(encObj[enc]['shorthand'])!='Undefined':
                            encStr=encObj[enc]['shorthand'].split(':')[0].split('(')[-1].split(')')[0]
                            print(" - appending {enc} shorthand:",encStr)
                            encList.append(encStr)
                        if str(encObj[enc]['condition'])!='Undefined':
                            encStr=encObj[enc]['condition']['field']
                            print(f" - appending {enc} condition:",encStr)
                            encList.append(encStr)
            except KeyError:
                # print(f"no key {enc}")
                continue
            except TypeError:
                # print(f"strange type: {enc}")
                continue
        
    ### remove any duplicates
    encList=list(dict.fromkeys(encList))
    # print(" - list:",encList)
    print("- return trimmed data")
    print(f"  - encList:\n\t{encList}")
    # print(f"  - data columns:\n\t{plotObj['data'].columns}")
    print(f"  - missing:\n\t{np.setdiff1d(encList,plotObj['data'].columns)}")
    # keep original df columns (shorthand retrieval can include nick names)
    subList=list(set(encList) & set(plotObj['data'].columns))
    plotObj['data']=plotObj['data'][subList]
    return plotObj


### translate aggregate report to save space
def MakeAggregatePlot(plotObj):
    
    ### if not bar chart then return
    try:
        if plotObj.__dict__['_kwds']['mark']!="bar":
            print(f"  - not a bar chart: {plotObj.__dict__['_kwds']['mark']}")
            print(plotObj.__dict__)
            return plotObj
    except KeyError:
        print("  - missing _mark_ information")
        print(plotObj.__dict__.keys())
        return plotObj

    ### get encoding info.
    encObj=plotObj['encoding']

    ### define and populate new encoding dicitonary
    # print(f" - make new encoding dictionary...")
    newEncDict={'title':plotObj.__dict__['_kwds']['title']}
    # loop over encodings
    for enc in ['color','x','y']: # encObj.__dict__['_kwds']
        try:
            # print(encObj[enc])
            if str(encObj[enc]['field'])!='Undefined':
                print(" - appending field:",encObj[enc]['field'])
                newEncDict[enc]=encObj[enc]['field']
                newEncDict[enc]=newEncDict[enc]+":"+encObj[enc]['type'].title()[0]
            else:
                if str(encObj[enc]['shorthand'])!='Undefined':
                    print(" - appending shorthand:",encObj[enc]['shorthand'])
                    newEncDict[enc]=encObj[enc]['shorthand']

            # get format: VARIABLE:T , T-->type initial
        except KeyError:
            # print(f"no key {enc}")
            continue

    # print(f"  - new encoding dictionary:\n{newEncDict}")
        
    ### loop over encodings and find aggregate
    # print("- search for  aggregate...")
    df_agg=pd.DataFrame()
    for enc in ['color','x','y']: # encObj.__dict__['_kwds']
        aggField=None
        ### check if count aggregation is used
        try:
            if str(encObj[enc]['aggregate'])!='Undefined':
                print(f"- {encObj[enc]['field']} is has appropriate aggregate: {encObj[enc]['aggregate']}")
                aggField=encObj[enc]['field']
            else:
                print(f"- {encObj[enc]['field']} has undefined aggregate")
        except KeyError:
            # print(f" - {enc} is has no aggregate key")
            pass

        ### check if shorthand is used 
        if aggField==None:
            try:
                if str(encObj[enc]['shorthand'])!='Undefined':
                    ### and has brackets --> aggregation
                    if "(" in str(encObj[enc]['shorthand']) and ")" in str(encObj[enc]['shorthand']):
                        print(f" - using shorthand: {encObj[enc]['shorthand']}")
                        aggField=encObj[enc]['shorthand'].split(':')[0].split('(')[-1].split(')')[0]
                    else:
                        print(f" - shorthand not aggregate: {encObj[enc]['shorthand']}")
                else:
                    print(f"- shorthand is undefined")
            except KeyError:
                # print(f" - {enc} is has no shorthand key")
                pass

        ### if aggragation is found
        if aggField!=None:
            print(f"- updating aggragate: {aggField}")

            if df_agg.empty:
                df_plot=plotObj['data']
            else:
                df_plot=df_agg
            print(f" - length: {len(df_plot.index)}")
            # display(df_plot)

            ### check aggField in df columns (shorthand may have nickname?)
            if aggField not in df_plot.columns:
                print(f" - aggField: {aggField} missing from df columns. return original")
                return plotObj

            # group to make count aggreagation
            df_agg=df_plot.groupby(by=f'{aggField}').agg(agg=(f'{aggField}','count')).rename(columns={'agg':aggField+"_agg"})
            # concat aggragation to first of each group
            df_agg=pd.concat([df_agg[aggField+"_agg"],df_plot.groupby(by=f'{aggField}').first()], axis=1).reset_index()

            ### update new encoding dict to use aggragate
            newEncDict[enc]=aggField+"_agg:Q"

            # display(df_agg)
            # print("Column names:",df_agg.columns)
    

    ### if no aggregated data then return original
    if df_agg.empty:
        print(f"- return old plot")
        return plotObj
    ### make new aggragated plot
    print(f"- make new plot")
    newPlot=alt.Chart(df_agg).mark_bar().encode(
                    x=alt.X(newEncDict['x']),
                    y=alt.Y(newEncDict['y']),
                    color=alt.Color(newEncDict['color']),
                    tooltip=[newEncDict['x'],newEncDict['y'],newEncDict['color']]
                ).properties(
                    width=600,
                    title=newEncDict['title']+" (AGGREGATED)"
                ).interactive()
    ### return new plot
    return newPlot


### define dashboard building function
# assume format: [ {'name':"PAGE_NAME", 'content': [{'XXX':YYY}] } ]
# XXX --> type of object (dpMap key), YYY --> object, e.g. df, str, alt
def DashboardBuilder(pageList=[], repDict={}):
    # make list of pages
    pages=[]
    date_text=datetime.datetime.now().strftime("%Y-%m-%d")
    # read input credentials (if present)
    report_title="My *Awesome* report"
    if "title" in repDict.keys():
        report_title=repDict['title']
    author_name="I.T.K. Author"
    if "author" in repDict.keys():
        author_name=repDict['author']
    repo_link={'text':"Code Repository",'link':"https://gitlab.cern.ch/atlas-itk-production-software/common-reporting/itk-pdb-reportorium"}
    if "repo" in repDict.keys():
        repo_link['link']=repDict['repo']
    ### define front page
    pages.append(dp.Page(title="Front Page", blocks=[
            dp.Text(f"# {report_title}"),
            dp.Text(f"### Credits: \n - made on: {date_text}\n - by: {author_name}\n - using: [{repo_link['text']}]({repo_link['link']})")
                ] ) )
    # the main content
    for page in pageList:
        blockList=[]
        for con in page['content']:
            for k,v in con.items():
                print(f"working on {k}")
                if "df" in k.lower():
                    if v.empty:
                        print(" - skipping empty dataframe")
                        continue
                    if "dropDFs" in repDict.keys() and repDict['dropDFs']==True:
                        print(f" - skipping dataframe, repSpec['dropDFs']={repSpec['dropDFs']}")
                        continue
                    print(f"- df rows: {len(v.index)}")
                else:
                    if v==None:
                        print("\t this is None. skipping")
                        continue
                    if "plot" in k.lower() or "line" in k.lower():
                        plotObj=v
                        ### trimming (for all charts)
                        if "trim" in repDict.keys() and repDict['trim']==True:
                            print(" - trimming plot data")
                            plotObj=TrimPlotData(plotObj)
                        ### aggregation for plots
                        if "plot" in k.lower():
                            if "aggregate" in repDict.keys() and repDict['aggregate']==True:
                                ### transform plot and add to blocklist 
                                print(" - aggregating plot data")
                                # aggPlot=MakeAggregatePlot(v)
                                plotObj=MakeAggregatePlot(plotObj)
                        blockList.append(dpMap[k](plotObj))
                        continue
                    else:
                        if "text" in k.lower() and len(v)<1:
                            v="[empty string]"
                print(f"\t uploading: {dpMap[k]}") #"({v})")
                # print(f"\t {str(type(dpMap[k])}")
                try:
                    blockList.append(dpMap[k](v))
                except TypeError:
                    print("Type Error for ("+k+"):",dpMap[k])
        pages.append(dp.Page(title=page['name'], blocks=blockList))
    
    ### writing
    out_path="my_report.html"
    if "outPath" in repDict.keys():
        out_path=repDict['outPath']
    if ".html" not in out_path:
        out_path=out_path+".html"
    dp.save_report(pages, path=out_path)

    ### return file path
    return out_path
