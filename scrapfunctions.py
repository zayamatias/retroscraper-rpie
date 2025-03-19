import logging
from re import findall,sub,search
from xml.sax.saxutils import escape
from sys import exit as sysexit
from checksums import getChecksums
from shutil import copyfile,rmtree
import apicalls
from os import path as ospath
from os import makedirs,remove,mkdir
from json import dumps as jsondumps
from json import loads as jsonloads
from uuid import getnode
import xml.etree.ElementTree as ET
from queue import Queue
from threading import Thread
from time import sleep
from googletrans import Translator
from pathlib import Path as Path
import os
import subprocess
from sys import platform
import time

def removedir(config,path,logging,thn):
    if path=='/' or path=='.' or path =='':
        print ('ABORTING, RISK OF BREAKING THE SYSTEM!',flush=True)
        sysexit(1)
    if platform == "linux" or platform == "linux2":
        subprocess.call(['rm','-rf',path])
    else:
        rmtree(path)

def pathExists(config,path,logging,thn):
    return ospath.isdir(path)
    

def normalizeFileName(filename,config,syspath):
    if '/overlays/' in filename or '/bezels/' in filename:
        return filename
    if '/' not in filename:
        return escape (filename)
    if config['config']['relative']:
        fname = '.'+filename.replace(syspath,'/')
    else:
        fname = filename
    return escape (fname)


def makedir (config,path,logging,thn):
    logging.info('###### GOING TO CREATE LOCAL DIR '+path+' IN THREAD ['+str(thn)+']')
    makedirs(path)    
    logging.info('###### CREATED LOCAL DIR '+path+' IN THREAD ['+str(thn)+']')
    return

def testPath(mypath,logging,thn):
    if mypath =='' or not ospath.isdir(mypath):
        return False
    return True

def getArcadeName(name,thn):
    if '.' in name:
        name=name[:name.rindex('.')]
    callURL = 'http://www.mamedb.com/game/'+name+'.html'
    callURL2 = 'http://mamedb.blu-ferret.co.uk/game/'+name+'/'
    callURL3 = 'http://adb.arcadeitalia.net/dettaglio_mame.php?game_name=' + name
    #print ('###### GETTING ARCADE NAME IN URL '+callURL)
    response = apicalls.simpleCall(callURL)
    if response!= '':
        gamename = findall(r"<title>(.*?)<\/title>", response)[0].replace('Game Details:  ','').replace(' - mamedb.com','')
        logging.info ('###### FOUND GAME IN MAMEDB '+gamename+' THREAD['+str(thn)+']')
        return gamename
    response = apicalls.simpleCall(callURL2)
    if response !='':
        gamename = findall(r"\<title\>Game Details:  (\w*).*\<\/title\>", response[0])
        logging.info ('###### FOUND GAME IN MAMEDB BLU FERRET '+gamename+' THREAD['+str(thn)+']')
        return gamename
    response = apicalls.simpleCall(callURL3)
    if response != '':
        gamename = findall(r"<title>(.*?)<\/title>", response)[0].replace(' - MAME machine','').replace(' - MAME software','')
        gamename = gamename.replace(' - MAME machin...','')
    if gamename.upper()=='ARCADE DATABASE':
        #print('###### COULD NOT GET NAME FROM ARCADE ITALIA')
        gamename = ''
    logging.info ('###### FOUND GAME IN ARCADEITALIA '+gamename+' THREAD['+str(thn)+']')
    return gamename

def getInfoFromAPI(system,thisfilename,sha1,md5,crc,apikey,uuid,logging,thn):
    partfilename = thisfilename.replace ('\\','/')
    filename = partfilename[partfilename.rindex('/')+1:]
    result = apicalls.getSHA1(sha1, apikey,uuid,thn)
    nosha = False
    try:
        showfilename = filename.encode().decode('utf-8')
    except:
        showfilename = ''
    if result.status_code == 404:
        logging.info ('###### COULD NOT FIND SHA1 FOR FILE '+showfilename+' THREAD['+str(thn)+']')
        nosha = True
        result = apicalls.getCRC(crc, apikey,uuid,thn)
        if result.status_code == 404:
            logging.info ('###### COULD NOT FIND CRC FOR FILE '+showfilename+' THREAD['+str(thn)+']')
            result = apicalls.getMD5(md5, apikey,uuid,thn)
            if result.status_code == 404:
                logging.info ('###### COULD NOT FIND MD5 FOR FILE '+showfilename+' THREAD['+str(thn)+']')
                ### remove both lines below
                fname = filename[:filename.rindex('.')]
                if 75 in system:
                    logging.info ('###### ITS AN ARCADE GAMEE '+showfilename+' THREAD['+str(thn)+']')
                    #print ('going for arcadename')
                    arcadeName = getArcadeName(filename,thn)
                    #print (arcadeName)
                    if arcadeName == '' or not arcadeName:
                        arcadeName = fname
                    try:
                        partnames = sub(r'[^A-Za-z0-9]+',' ',arcadeName).lower().split()
                    except Exception as e:
                        print ('###### ERROR WHEN GETTING ARCADE NAME '+str(arcadeName)+' ->'+str(e)+' in file '+str(showfilename)+' THREAD['+str(thn)+']',flush=True)
                        sysexit()

                else:
                    logging.info ('###### ITS NOT AN ARCADE GAMEE '+showfilename+' THREAD['+str(thn)+']')
                    partnames =  sub(r'[^A-Za-z0-9]+',' ',fname).lower().split()
                if 0 not in system:
                    exclude_words = ['trsi','bill','sinclair','part','tape','gilbert','speedlock','erbesoftwares','aka','erbe','iso','psn','soft','crack','dsk','release','z80','2000','2001','2002','2003','2004','2005','2006','2007','2008','2009','2010','2011','2012','2013','2014','2015','2016','2017','2018','2019','2020','prototype','pirate','world','fre','h3c','jue','edition','c128','unl','1983','1984','ltd','side','1985','1986','1987','software','disabled','atx','bamcopy','playable','data','boot','xenophobia','code','dump','compilation','cd1','cd2','cd3','cd4','paradox','19xx','1988','1989','1990','1991','1992','1993','1994','1995','1996','manual','csl','defjam','files','pdx','doscopy','bootable','cracktro','flashtro','flt','checksum','error','qtx','aga','corrupt','disk1','disk2','disk3','disk4','disk5','disk6','italy','spain','psx','disc','demo','rev','slus','replicants','germany','france','start','tsth','patch','newgame','sega','beta','hack','rus','h1c','h2c','the','notgame','zzz','and','pal','ntsc','disk','file','inc','fullgame','48k','128k','16k','tap','tzx','usa','japan','europe','d64','t64','c64']
                    sfname = sub(r"[\(\[].*?[\)\]]", "", fname)
                    sfname = sfname.replace('_',' ').strip()
                    for thissys in system:
                        logging.info ('###### LOOKING IN SYSTEM '+str(thissys)+' THREAD['+str(thn)+']')
                        for partname in partnames:
                            logging.info ('###### LOOKING FOR SYSTEM '+str(partname)+' THREAD['+str(thn)+']')
                            if len(partname)>3 and not (partname.lower() in exclude_words) :
                                result = apicalls.getSearch(str(thissys),partname, apikey,uuid,thn)
                                if result.status_code !=404:
                                    logging.info ('###### FOUND IN THE BACKEND THREAD['+str(thn)+']')
                                    try:
                                        jsob = jsonloads(result.text)
                                        #print (jsob)
                                        respobj = jsob['response']
                                        #print (respobj)
                                        logging.info ('###### IT S A GOOD JSON THREAD['+str(thn)+']')
                                        try:
                                            myresults = respobj['results']
                                            logging.info ('###### THERE ARE RESULTS THREAD['+str(thn)+']')
                                        except:
                                            logging.error ('###### I GOT SOMETHING STRANGE,, NO RESULTS FOR A SEARCH! THREAD['+str(thn)+']')
                                            continue
                                    except Exception as e:
                                        logging.error ('ERROR IN JSON RECEIVED FROM BACKEND '+str(thissys)+' SEARCHING FOR '+partname+' '+str(e)+' THREAD['+str(thn)+']')
                                        continue
                                    for searchable in myresults:
                                        logging.info ('###### LOOKING FOR MATCHES THREAD['+str(thn)+']')
                                        if sfname.lower() == searchable['name']['text'].lower():
                                            logging.info ('###### THERE IS A MATCH THREAD['+str(thn)+']')
                                            result = apicalls.getURL(searchable['gameURL'], apikey,uuid,thn)
                                            submitJson = '{"request": {"type": "romnotincluded","data": {"gameUrl":"'+searchable['gameURL']+'","systemid": "'+str(system)+'","filename": "'+filename.encode().decode("utf-8")+'","match":"'+fname+'","SHA1": "'+sha1+'","MD5": "'+md5+'","CRC": "'+crc+'"}}}'
                                            subresult = apicalls.postSubmit (submitJson,apikey,uuid,logging,thn)
                                            return jsonloads(result.text)['response']
                                    logging.info ('###### THERE IS NO MATCH SO FAR THREAD['+str(thn)+']')
                    logging.info ('###### I GIVE UP LOOKING, WILL INFORM THE BACKEND THREAD['+str(thn)+']')
                    try:
                        jfilename = filename.encode().decode("utf-8")
                        submitJson = '{"request": {"type": "norom","data": {"systemid": "'+str(system)+'","filename": "'+jfilename+'","SHA1": "'+sha1+'","MD5": "'+md5+'","CRC": "'+crc+'"}}}'
                    except:
                        submitJson = '{"request": {"type": "norom","data": {"systemid": "'+str(system)+'","filename": "","SHA1": "'+sha1+'","MD5": "'+md5+'","CRC": "'+crc+'"}}}'
                    logging.info ('###### GOING TO SUBMIT TO BACKEND THREAD['+str(thn)+']')
                    result = apicalls.postSubmit (submitJson,apikey,uuid,logging,thn)
                    logging.info ('###### SUBMITTED TO BACKEND THREAD['+str(thn)+']')
                response = {"game": {"ratings": [], "dates": [], "names": [{'text':filename,'region':'default'}], "roms": [], "cloneof": "0", "genres": [],\
                            "notgame": "false", "system": {"url": "/api/system/"+str(system[0]), "id": int(system[0])}, "players": {"text": "Unknown"},\
                            "synopsis": [{"text":"Could not find Synopsis","language":"en"}], "editor": {}, "medias": [], "developer": {}, "id":0,\
                            "modes": []}}
                logging.info ('###### RETURNING EMPTY STANDARD RESPONSE THREAD['+str(thn)+']')
                return response
            else:
                nosha=True
        else:
            nosha=True
    try:
        logging.info ('###### I FOUND THE GAME THREAD['+str(thn)+']')
        rjson = jsonloads(result.text)
        logging.info ('###### GOT JSON '+str(rjson)+'THREAD['+str(thn)+']')
        response = rjson['response']
        if nosha:
            logging.info ('###### I FOUND NO SHA1 BUT I KNOW WHICH GAME IT IS, TELLING THE BACKEND THREAD['+str(thn)+']')
            try:
                logging.info ('###### I KNOW WHICH GAME ID IT IS, SO INFORM THREAD['+str(thn)+']')
                gameid = str(response['game']['id'])
            except:
                logging.error ('###### I SHOULD NOT BE HERE!! THERE MUST BE A GAME ID THREAD['+str(thn)+']')
                gameid = '99999999999999999999999999999999'
            submitJson = '{"request": {"type": "nosha","data": {"gameid":"'+gameid+'","systemid": "'+str(system)+'","filename": "'+filename+'","SHA1": "'+sha1+'","MD5": "'+md5+'","CRC": "'+crc+'"}}'
            logging.info ('###### TELLING THE BACKEND THREAD['+str(thn)+']')
            subresult = apicalls.postSubmit (submitJson,apikey,uuid,logging,thn)
    except Exception as e:
        logging.error ('###### GETTING INFO FROM API: '+str(result)+' ERROR '+str(e)+' THREAD['+str(thn)+']')
        logging.error ('###### '+str(system)+','+str(filename)+','+str(sha1)+','+str(md5)+','+str(crc)+' THREAD['+str(thn)+']')
        submitJson = '{"request": {"type": "error","data": {"filename": "'+filename+'","SHA1": "'+sha1+'","MD5": "'+md5+'","CRC": "'+crc+'"}}'
        logging.info ('###### TELLING THE BACKEND I FOUND SOMETHING STRANGE THREAD['+str(thn)+']')
        subresult = apicalls.postSubmit (submitJson,apikey,uuid,logging,thn)
        response = {"game": {"ratings": [], "dates": [], "names": [{'text':filename,'region':'default'}], "roms": [], "cloneof": "0", "genres": [],\
                    "notgame": "false", "system": {"url": "/api/system/"+str(system[0]), "id": int(system[0])}, "players": {"text": "Unknown"},\
                    "synopsis": [{"text":"Could not find Synopsis","language":"en"}], "editor": {}, "medias": [], "developer": {}, "id":0,\
                    "modes": []}}
        #sysexit()
    return response

def isValidVersion(appVer,apikey,uuid,thn):
    verJson = apicalls.getVersion(apikey,uuid,thn)
    try:
        reqVer = verJson['response']['version']
    except:
        reqVer = '9999999999999999'
    return (appVer==reqVer)

def getUniqueID():
    return ''.join(findall('..', '%012x' % getnode())).upper()

def loadConfig(logging,q,apikey,uuid,thn):
    config = dict()
    config['config']=dict()
    config['config']["SystemsFile"]=""
    config['config']["MountPath"]=""
    config['config']['decorators']=dict()
    return config

def saveConfig(config,q):
    homedir = str(Path.home())+'/.retroscraper/'
    configfilename= homedir+'retroscraper.cfg'
    try:
        f = open(configfilename, "w")
        f.write(jsondumps(config['config']))
        f.close()
    except Exception as e:
        print('CONFIG ERROR! - I CANNOT CREATE A CONFIG FILE '+str(e),flush=True)
        return config
    return

def processBezels(config,bezelURL, destbezel, apikey, uuid,filename,path,logging,thn,cli,syspath):
    extrapath = filename.replace(syspath,'')
    if '/' in extrapath:
        extrapath = extrapath[:extrapath.rindex('/')]
    else:
        extrapath =''
    try:
        sfn=filename.encode().decode('utf-8')
    except:
        sfn=''
    logging.info ('+++++++==========###### PROCESS BEZEL FOR '+sfn+' LOCATED AT '+path+' THREAD['+str(thn)+']')
    logging.info ('###### DOWNLOADING BEZELS THREAD['+str(thn)+']')
    logging.info ('###### '+destbezel+' THREAD['+str(thn)+']')
    destbezel = destbezel.replace('\\','/')
    path = path.replace('\\','/')
    filename = filename.replace('\\','/')
    bezeldir = destbezel[:destbezel.rindex('/')]
    apicalls.getImageAPI(config,bezelURL,destbezel,apikey,uuid,thn,'bezel',cli,logging)
    zipname = filename[filename.rfind('/')+1:]
    try:
        szname = zipname.encode().decode('utf-8')
    except:
        szname =''
    logging.info ('###### ZIPNAME IS '+szname+' THREAD['+str(thn)+']')
    if extrapath:
        bezelcfg = path+'/'+extrapath+'/'+zipname+'.cfg'
    else:
        bezelcfg = path+zipname+'.cfg'

    try:
        sbc = bezelcfg.encode().decode('utf-8')
    except:
        sbc =''
    logging.info ('###### BEZELCFG IS '+sbc+' THREAD['+str(thn)+']')
    bzlfile,bzlext = ospath.splitext (zipname)
    romcfg = bzlfile+'.cfg'
    try:
        rcf = romcfg.encode().decode('utf-8')
    except:
        rcf =''
    logging.info ('###### ROMCFG IS '+rcf+' THREAD['+str(thn)+']')
    romcfgpath = bezeldir+'/'+romcfg
    try:
        rcfp = romcfgpath.encode().decode('utf-8')
    except:
        rcfp =''

    logging.info ('###### ROMCFGPATH IS '+rcfp+' THREAD['+str(thn)+']')
    logging.info ('###### CREEATING FILE '+sbc+' IN THREAD ['+str(thn)+']')
    f = open(bezelcfg, "w")
    properfname = normalizeFileName(bezeldir,config,'bezel')
    filetext = 'input_overlay = "'+properfname+'/'+romcfg+'"\n'
    try:
        ft = filetext
        f.write(filetext)
    except:
        try:
            ft = filetext.encode().decode('utf-8')
        except:
            ft =''
        f.write(ft)
    logging.info ('###### WROTE FILE '+sbc+' === '+ft+' IN THREAD ['+str(thn)+']')
    f.close()
    fsize =os.stat(bezelcfg)
    logging.info ('###### CLOSE FILE '+sbc+' IN RESULTED IN '+str(fsize)+' THREAD ['+str(thn)+']')
    logging.info ('###### CREEATING FILE '+rcfp+' IN THREAD ['+str(thn)+']')
    nf = open(romcfgpath, "w")
    properfname = normalizeFileName(destbezel,config,'bezel')
    filetext = 'overlays = "1"\noverlay0_overlay = "'+properfname+'"\noverlay0_full_screen = "true"\noverlay0_descs = "0"\n'
    try:
        ft = filetext
        nf.write(filetext)
    except:
        try:
            ft=filetext.encode().decode('utf-8')
        except:
            ft = ''
            nf.writr(ft)
    logging.info ('###### WROTE FILE '+rcf+' === '+ft+' IN THREAD ['+str(thn)+']')
    nf.close()
    fsize =os.stat(romcfgpath)
    logging.info ('###### CLOSE FILE '+rcf+' IN RESULTED IN '+str(fsize)+' THREAD ['+str(thn)+']')

def loadSystems(config,apikey,uuid,remoteSystems,q,trans,logging):
    ### LOAD SYSTEMS INTO MEMORY
    try:
        logging.info ('###### READING FROM '+config['config']['SystemsFile'])
    except:
        logging.error ('###### CONFIG SYSTEMSFILE IS EMPTY!!!')
        return []
    tree = ET.ElementTree()
    logging.info ('###### OPENING FILE')
    try:
        tst = open(config['config']['SystemsFile'], 'r')
        tst.close()
    except:
        logging.error ('###### CANNOT READ SYSTEMS FILE!')
        print('Cannot read systems file!',flush=True)
        return 'XMLERROR'
    with open(config['config']['SystemsFile'], 'r') as xml_file:
        logging.info ('###### OPENED FILE')
        try:
            logging.info ('###### PARSING FILE')
            tree.parse(xml_file)
            logging.info ('###### PARSED FILE')
        except:
            logging.info ('###### ERROR IN THE XML, MAYBE 3 BYTES FOR UTF?')
            xml_file.seek(3)
            try:
                logging.info ('###### PARSING FILE ONE MORE TIME')
                tree.parse(xml_file)
                logging.info ('###### PARSED FILE')
            except:
                logging.error ('###### DEFINITELY BAD XML!')
                #q.put([trans['xmlerr'],'popup',trans['xmlerrmsg']])
                return 'XMLERROR'
    try:
        logging.info ('###### GETTING ROOT ELEMENT')
        root = tree.getroot()
        logging.info ('###### GOT ROOT ELEMENT')
        systems=[]
        for child in root:
            logging.info ('###### DOING CHILD '+child.tag.lower())
            if child.tag.lower() == 'system':
                logging.info ('###### IT IS A SYSTEM TAG - CREATE NEW DICT')
                mySystem=dict()
                logging.info ('###### IT IS A SYSTEM TAG - GIVE IT EMPTY ID')
                mySystem['id']=[]
                logging.info ('###### ITERATING THROUGH CHILDS')
                for xmlSystem in child:
                    try:
                        logging.info ('###### GET SYSTEM INFO')
                        mySystem[xmlSystem.tag.lower()]=xmlSystem.text
                    except Exception as e:
                        print('CANNOT GET TAG NAME '+str(e),flush=True)
                        pass
                    logging.info ('###### GOT SYSTEM TAG ['+xmlSystem.tag.lower()+']')
                    if str(xmlSystem.tag.upper())=='NAME':
                        logging.info ('###### STARTING SYSTEM ==================================================')
                        logging.info ('###### GOT SYSTEM NAME - WILL TRY TO MATCH IT')
                        for rSystem in remoteSystems['systems']:
                            try:
                                logging.info ('###### GOT NAMES '+str(rSystem['lookupnames']))
                            except:
                                pass
                            for sysname in rSystem['lookupnames']:
                                try:
                                    if xmlSystem.text.upper() == sysname.upper():
                                        mySystem['id'].append(rSystem['id'])
                                        break
                                except:
                                    pass
                if 'path' in mySystem.keys():
                    ### TODO DISTINCT WINDOWS OR LINUX
                    if mySystem['path'][-1] != '/':
                        mySystem['path']=mySystem['path']+'/'
                if mySystem['id']:
                    systems.append(mySystem)
                    logging.info('###### FOUND '+str(jsondumps(systems)))
                else:
                    mySystem['id']=[0]
                    systems.append(mySystem)
                    q.put(['errorlabel','text',trans['unksystem']+' '+str(mySystem['name'])])
    except Exception as e:
        print ('CANNOT PARSE XML '+str(e),flush=True)
        systems=[]
    return systems

def loadCompanies(apikey,uuid,thn):
    externalCompanies = apicalls.getCompaniesFromAPI(apikey,uuid,thn)
    companies = dict()
    for thisCompany in externalCompanies['companies']:
        companies[str(thisCompany['id'])]=thisCompany['text']
    return companies

def multiDisk(filename):
    matchs=[]
    checkreg = r'\([P|p][A|a][R|r][T|t][^\)]*\)|\([F|f][I|i][L|l][E|e][^\)]*\)|\([D|d][I|i][S|s][K|k][^\)]*\)|\([S|s][I|i][D|d][E|e][^\)]*\)|\([D|d][I|i][S|s][C|c][^\)]*\)|\([T|t][A|a][P|p][E|e][^\)]*\)'
    matchs = matchs+findall(checkreg,filename)
    checkreg = r'[G|g][A|a][M|m][E|e]\ [D|d][I|i][S|s][K|k]\ \d*'
    matchs = matchs+findall(checkreg,filename)
    return matchs

def multiHack(filename):
    checkreg = r'\(.*[H|h][A|a][C|c][K|k][^\)]*\)|\([P|p][R|o][T|t][O|o][T|t][Y|y][P|p][E|e][^\)]*\)|\([D|d][E|e][M|m][O|o][^\)]*\)|\([S|s][A|a][M|m][P|p][L|l][E|e][^\)]*\)|\([B|b][E|e][T|t][A|a][^\)]*\)'    
    matchs = findall(checkreg,filename)
    return matchs

def multiCountry(filename):
    matchs=[]
    checkreg = r'\([E|e][U|u][R|r][O|o][P|p][E|e][^\)]*\)|\([U|u][S|s][A|a][^\)]*\)|\([J|j][A|a][P|p][A|a][N|n][^\)]*\)|\([E|e][U|u][R|r][A|a][S|s][I|i][A|a][^\)]*\)'
    matchs = matchs+findall(checkreg,filename)
    checkreg = r'\([S|s][P|p][A|a][I|i][N|n][^\)]*\)|\([F|f][R|r][A|a][N|n][C|c][E|e][^\)]*\)|\([G|g][E|e][R|r][M|m][A|a][N|n][Y|y][^\)]*\)'
    matchs = matchs+findall(checkreg,filename)
    checkreg = r'\([P|p][A|a][L|l][^\)]*\)|\([N|n][T|t][S|s][C|c][^\)]*\)|\([E|e][N|n][G|g][^\)]*\)|\([R|r][U|u][^\)]*\)|\([D|d][E|e][^\)]*\)|\([E|e][^\)]*\)|\([U|u][^\)]*\)|\([J|j][^\)]*\)|\([S|s][^\)]*\)|\([N|n][^\)]*\)|\([F|f][^\)]*\)|\([J|j][P|p][^\)]*\)|\([N|n][L|l][^\)]*\)|\([K|k][R|r][^\)]*\)|\([E|e][S|s][^\)]*\)'
    matchs = matchs+findall(checkreg,filename)
    return matchs

def multiVersion(filename):
    matchs=[]
    ## Check if version is between ()
    checkreg = r'\([V|v|R|r]\d+\.\d+.*\)'
    matchs = matchs+findall(checkreg,filename)
    if matchs:
        for match in matchs:
            filename = filename.replace(match,'')
    checkreg = r'[V|v|R|r]\d+\.\d+'
    nmatchs = findall(checkreg,filename)
    if nmatchs:
        for match in matchs:
            filename = filename.replace(match,'')
        matchs = matchs+nmatchs
    checkreg = r'#\d+'
    matchs = matchs+findall(checkreg,filename)
    return matchs

def bracketmatch(filename):
    checkreg = r'\[.*\]'
    matchs = findall(checkreg,filename)
    return matchs

def getMediaUrl(mediapath,file,medias,mediaList,logging,thn,typeofmedia,regionList=['wor']):
    imageURL = ''
    destfile =''
    if medias:
        for mediatype in mediaList:
            for region in regionList:
                for img in medias:
                    #logging.info('####### MEDIATYPE '+str(mediatype)+'   IMG VALUES '+str(img.values()))
                    if mediatype=='box-2D':
                        if mediatype in img.values():
                            destfile = mediapath+file+'-box.'+img['format']
                            imageURL = img['url'].replace(img['region'],'wor')
                            logging.info ('###### RETURNING '+imageURL+' THREAD['+str(thn)+']')
                            return imageURL,destfile
                    else:
                        if mediatype in img.values() and region in img.values():
                            destfile = mediapath+file+'-'+typeofmedia+'.'+img['format']
                            imageURL = img['url']
                            return imageURL,destfile
    return imageURL,destfile


def getFileInfo(file,system,companies,emptyGameTag,apikey,uuid,q,sq,config,logging,filext,tq,thn,xmlvalues,rthn,cli):
    ### SHOULD ADD THE CHECK COFIG BIT
    for xvalue in xmlvalues:
        emptyGameTag=emptyGameTag.replace(xvalue[0],xvalue[1])
    try:
        showfile = file.encode().decode('utf-8')
    except:
        showfile = ''
    logging.info ('###### STARTING FILE '+showfile+'THREAD['+str(thn)+']')
    file=file.replace('\\','/')
    file=str(file)
    if ospath.isdir(file):
        logging.info ('###### THIS IS A DIRECTORY! THREAD['+str(thn)+']')
        ### THIS INFORMS THE THREAD HAS ENDED
        tq.put(rthn)
        return
    logging.info ('####### GETTING CHECKSUMS FOR '+str(showfile)+'THREAD['+str(thn)+']')
    mysha1,mymd5,mycrc = getChecksums(file,config,logging,thn)
    logging.info ('####### GOT CHECKSUMS FOR '+str(showfile)+' THREAD['+str(thn)+']')
    ## PROCESS FILE AND START DOING MAGIC
    logging.info ('####### GETTING INFO FOR '+str(showfile)+' THREAD['+str(thn)+']')
    result = getInfoFromAPI (system['id'],file,mysha1,mymd5,mycrc,apikey,uuid,logging,thn)
    logging.info ('####### GOT INFO FOR '+str(showfile)+' THREAD['+str(thn)+']')
    if (not result) or ('game' not in result.keys()):
        ### THERE WAS AN ERROR GETTING INFORMATION FOR THIS FILE
        logging.error('###### I COULD NOT GET THE GAME INFORMATION FROM API '+str(result)+' THREAD['+str(thn)+']')
        ### THIS INFORMS THE THREAD HAS ENDED
        tq.put(rthn)
        return
    try:
        gsysid = result['game']['system']['id']
    except Exception as e:
        if 75 in system['id']:
            gsysid = 75
        else:
            gsysid = system['id'][0]
    ### AQUISTOY
    thisTag = emptyGameTag
    ### Take care of multisystems
    simplefile = file[file.rindex('/')+1:file.rindex('.')]
    try:
        showsfile = simplefile.encode().decode('utf-8')
    except:
        showsfile =''
    logging.info ('###### SIMPLE FILE NAME :['+str(showsfile)+'] THREAD['+str(thn)+']')
    system['path'] = system['path'].replace('\\','/')
    if config['config']['fixedmediadir']:
        if config['config']['fixedmediadir'][0]=='/':
            mediadestdir = config['config']['fixedmediadir']+system['name']+'/'
        else:
            mediadestdir = system['path']+config['config']['fixedmediadir'][2:]
    else:
        mediadestdir = system['path']+'images/'
    try:
        pfbx =  config['config']['preferbox']
    except:
        pfbx = False
    if not pfbx:
        logging.info ('###### DOWNLOADING SCREENSHOT THREAD['+str(thn)+']')
        try:
            imageURL,destimage = getMediaUrl(mediadestdir,simplefile,result['game']['medias'],['mixrbv1','ss','sstitle'],logging,thn,'image',['wor','default'])
        except Exception as e:
            logging.error ('##### EFRROR WHEN DOWNLOADING IMAGES ['+str(result)+']]#####=='+str(e))
    else:
        logging.info ('###### DOWNLOADING BOX')
        imageURL,destimage = getMediaUrl(mediadestdir,simplefile,result['game']['medias'],['box-2D'],logging,thn,'box',['wor'])
    try:
        novi =  config['config']['novideodown']
    except:
        novi = False
    if not novi:
        logging.info ('###### DOWNLOADING VIDEO THREAD['+str(thn)+']')
        if not config['config']['fixedmediadir']:
            mediadestdir = system['path']+'videos/'
        videoURL,destvideo = getMediaUrl(mediadestdir,simplefile,result['game']['medias'],['video-normalized'],logging,thn,'video',['wor','default'])
    else:
        logging.info ('###### NOT DOWNLOADING VIDEO THREAD['+str(thn)+']')
        videoURL = ''
        destvideo = ''
    if not config['config']['fixedmediadir']:
        mediadestdir = system['path']+'marquees/'
    marqueeURL,destmarquee = getMediaUrl(mediadestdir,simplefile,result['game']['medias'],['screenmarqueesmall'],logging,thn,'marquee',['wor','default',])
    try:
        dobezels = config['config']['bezels']
    except:
        dobezels = False
    if dobezels:
        logging.info ('++++++++++++++++ TRYING TO GET BEZELS THREAD['+str(thn)+']')
        destbezel=''
        bezelURL=''
        logging.info ('###### FIRST CASE THREAD['+str(thn)+']')
        dpath = system['path'].replace('/roms/','/overlays/')+'bezels/'
        logging.info ('###### CONVERTING '+str(system['path'])+'    '+dpath+' THREAD['+str(thn)+']')
        bezelURL,destbezel = getMediaUrl(dpath,simplefile,result['game']['medias'],['bezel-16-9'],logging,thn,'bezel',['wor','default'])
        if destbezel=='' and config['config']['sysbezels']: ## CONFIG UPDATE
            sysmedias=[{"url": "/api/medias/"+str(gsysid)+"/system/bezel-16-9(wor).png",
            "region": "wor",
            "type": "bezel-16-9",
            "format": "png"
            }]
            bezelURL,destbezel = getMediaUrl(system['path'].replace('/roms/','/overlays/')+'bezels/','system_bezel-'+str(gsysid),sysmedias,['bezel-16-9'],logging,thn,'bezel',['wor','default'])
        logging.info ('++++++++++++++++ BACK FROM BEZELS THREAD['+str(thn)+']')
    else:
        bezelURL=''
    if imageURL !='':
        imglocation = apicalls.getImageAPI(config,imageURL,destimage,apikey,uuid,thn,'ss',cli,logging)
        if not imglocation:
            destimage =''
    else:
        imglocation = ''
    if videoURL !='':
        success = apicalls.getImageAPI(config,videoURL,destvideo,apikey,uuid,thn,'video',cli,logging)
        if not success:
            destvideo =''
    if marqueeURL !='':
        success = apicalls.getImageAPI(config,marqueeURL,destmarquee,apikey,uuid,thn,'marquee',cli,logging)
        if not success:
            destmarquee =''
    if bezelURL !='':
        logging.info ('==================================##### PROCESSNG BEZEL THREAD['+str(thn)+']')
        logging.info ('##### URL='+str(bezelURL)+' THREAD['+str(thn)+']')
        logging.info ('###### DESTBEZEL = '+str(destbezel)+' THREAD['+str(thn)+']')
        processBezels(config,bezelURL,destbezel,apikey,uuid,file,system['path'],logging,thn,cli,system['path'])
    thisTag = thisTag.replace('$PATH',normalizeFileName(file,config,system['path']))
    logging.info ('###### GAME NAMES FOUND :['+str(result['game']['names'])+']')
    gameName = result['game']['names'][0]['text']
    try:
        gmf=gameName.encode().decode('utf-8')
    except:
        gmf =''
    logging.info ('###### GAME NAME FOUND :['+gmf+']')
    tempfile = simplefile
    matchs = multiDisk(tempfile)
    if matchs:
        for match in matchs:
            tempfile = tempfile.replace(match,'')
    logging.info ('###### MULTI DISK MATCH :['+str(matchs)+']')
    vmatchs = multiVersion(tempfile)
    if vmatchs:
        for match in vmatchs:
            try:
                tempfile = tempfile.replace('('+match+')','')
                tempfile = tempfile.replace(match,'')
            except:
                pass
    logging.info ('###### VERSION MATCH :['+str(vmatchs)+']')
    cmatchs = multiCountry(tempfile)
    if cmatchs:
        for match in cmatchs:
            tempfile = tempfile.replace(match,'')
    logging.info ('###### COUNTRY MATCH :['+str(cmatchs)+']')
    hmatchs = multiHack(simplefile)
    logging.info ('###### HACK MATCH :['+str(hmatchs)+']')
    if hmatchs:
        for match in hmatchs:
            tempfile = tempfile.replace(match,'')
    bmatchs = bracketmatch(tempfile)
    logging.info ('###### BRACKET MATCH :['+str(bmatchs)+']')
    logging.info ('###### FILE ENDED AS :['+str(tempfile)+']')
    try:
        if cmatchs and config['config']['decorators']['country']:
            for cmatch in cmatchs:

                if cmatch.lower() not in gameName.lower():
                    gameName = gameName+' '+cmatch.replace('_',' ')
    except:
        logging.info ('###### NO COUNTRY SELECTION CONFIGURED')
    try:
        if matchs and config['config']['decorators']['disk']:
            for match in matchs:
                if match.lower() not in gameName.lower():
                    gameName = gameName+' '+match.replace('_',' ')
    except:
        logging.info ('###### NO DISK SELECTION CONFIGURED')
    try:
        if vmatchs and config['config']['decorators']['version']:
            for vmatch in vmatchs:
                if vmatch.lower() not in gameName.lower():
                    if "(" not in vmatch:
                        gameName = gameName+' ('+vmatch.replace('_',' ')+')'
                    else:
                        gameName = gameName+' '+vmatch.replace('_',' ')
    except:
        logging.info ('###### NO VERSION SELECTION CONFIGURED')
    try:
        if hmatchs and config['config']['decorators']['hack']:
            for hmatch in hmatchs:
                if hmatch.lower() not in gameName.lower():
                    gameName = gameName+' '+hmatch.replace('_',' ')
    except:
        logging.info ('###### NO HACK SELECTION CONFIGURED')
    try:
        if bmatchs and config['config']['decorators']['brackets']:
            for bmatch in bmatchs:
                if bmatch.lower() not in gameName.lower():
                    gameName = gameName+' '+bmatch.replace('_',' ')
    except:
        logging.info ('###### NO BRACKET SELECTION CONFIGURED')
    ## TRY PRINT I/OF QUEUE
    #q.put(['gamelabel','text',' System : '+system['name']+' | Game : '+gameName])
    print ('System: '+system['name']+' | Game : '+gameName,flush=True)
    thisTag = thisTag.replace('$NAME',escape(gameName))
    description = 'Description for this game is empty!'
    founddesc = False
    if result['game']['synopsis']:
        try:
            if not config['config']['language']:
                config['config']['language']='en'
        except:
                config['config']['languags']='en'
        language = config['config']['language']
        logging.info ('###### SEARCHING DESCRIPTION IN '+str(language))
        for desc in result['game']['synopsis']:
            logging.info ('###### FOUND LANGUAGE '+desc['language'].upper())
            if desc['language'].upper()==language.upper():
                description= desc['text'].replace('&quot;','"')
                founddesc=True
                break
        if not founddesc:
            logging.info ('###### COULD NOT FIND DESCRIPTION IN YOU PREFERRED LANGUAGE '+str(config['config']['language'])+' SO I\'M DEFAULTING TO FIRST FOUND')
            untdesc = result['game']['synopsis'][0]['text'].replace('&quot;','"')
            try:
                if config['config']['usegoogle']:
                    translator=Translator()
                    translator.raise_Exception = True
                    langtot = config['config']['language']
                    translation = translator.translate(untdesc,dest=langtot)
                    description = translation.text
                    logging.info ('###### I\'VE TRANSLATED THE TEXT ')
                else:
                    description = untdesc
            except Exception as e:
                try:
                    translator=Translator()
                    translator.raise_Exception = True
                    langtot = config['config']['language']
                    translation = translator.translate(untdesc,dest=langtot)
                    description = translation.text
                except Exception as e:
                    logging.error ('###### COULD NOT TRANSLATE '+str(e))
                    description = untdesc
    logging.info ('###### PUTTING DESCRPTION IN QUEUE')
    #q.put(['gamedesc','text',description])
    logging.info ('###### DESCRPTION IN QUEUE')
    try:
        logging.info ('###### REPLACING DESCRIPTION IN TAG')
        thisTag = thisTag.replace('$DESCRIPTION',escape(description))
        logging.info ('###### REPLACED DESCRIPTION IN TAG')
    except Exception as e:
        logging.error ('###### CANNT REPLACE TRANSLATION '+str(e))
    ratings = ''
    #if result['game']['ratings']:
    #    for rating in result['game']['ratings']:
    #        ratings =  ratings + ' ' + rating['type']+':'+rating['text']
    #    ratings = ratings[1:]
    logging.info ('###### REPLACING RATINGS IN TAG')
    thisTag = thisTag.replace('$RATING',escape(ratings))
    logging.info ('###### REPLACED RATINGS IN TAG')
    editor = 'Unknown'
    logging.info ('###### REPLACING EDITOR IN TAG')
    if 'id' in result['game']['editor'].keys():
        logging.info ('###### LOOKING FOR EDITOR ID')
        edid = str(result['game']['editor']['id'])
        logging.info ('###### EDITOR ID FOUND')
    try:
        logging.info ('###### GETTING COMPANY - EDITOR ID')
        editor = companies[edid]
        logging.info ('###### GOT COMPANY - EDITOR ID')
    except:
        logging.info ('###### COULDNOT GET COMPANY - EDITOR ID')
        pass
    logging.info ('###### REPLACING EDITOR')
    thisTag = thisTag.replace('$PUBLISHER',escape(editor))
    logging.info ('###### REPLACED EDITOR')
    developer = 'Unknown'
    if 'id' in result['game']['developer'].keys():
        logging.info ('###### GETTING DEV ID')
        devid = str(result['game']['developer']['id'])
        logging.info ('###### GOT DEV ID')
        try:
            logging.info ('###### GETTING DEVELOPER NAME')
            developer = companies[devid]
            logging.info ('###### GOT DEVELOPER NAME')
        except:
            logging.info ('###### COULD NOT GET DEVELOPER NAME')
            pass
    logging.info ('###### REPLACE DEV')
    thisTag = thisTag.replace('$DEVELOPER',escape(developer))
    genre=''
    logging.info ('###### REPLACE IMAGE')
    thisTag = thisTag.replace('$IMAGE',normalizeFileName(destimage,config,system['path']))
    logging.info ('###### REPLACE VIDEO')
    thisTag = thisTag.replace('$VIDEO',normalizeFileName(destvideo,config,system['path']))
    logging.info ('###### REPLACE MARQUEE')
    thisTag = thisTag.replace('$MARQUEE',normalizeFileName(destmarquee,config,system['path']))
    logging.info ('###### REPLACE RELEASE DATE')
    thisTag = thisTag.replace('$RELEASEDATE','')
    thisTag = thisTag.replace('$PLAYERS','')
    thisTag = thisTag.replace('$GENRE','')
    ### Repalce all tags with value from response
    logging.info ('###### PUT IN QUEUE')
    #q.put(['scrapPB','valueincrease'])
    logging.info ('###### DID PUT IN QUEUE')
    logging.info ('###### PUT IN SQUEUE')
    sq.put ((thisTag,int(result['game']['id'])))
    logging.info ('###### DID PUT IN SQUEUE')
    logging.info ('###### PUT IN TQUEUE')
    tq.put(rthn)
    logging.info ('###### DID PUT IN TQUEUE')
    logging.info ('###### DONE FILE '+showfile)
    return

def getGamelistData(gamelistfile):
    try:
        tree = ET.parse(gamelistfile)
    except:
        return []
    gamelist = tree.getroot()
    currValues = dict()
    for game in gamelist:
        myValues = []
        pc = False
        favo = False
        lastplay = False
        for gametag in game:
            if gametag.tag.lower()=='playcount':
                if gametag.text:
                    myValues.append(("$PLAYCOUNT",gametag.text))
                    pc = True
            if gametag.tag.lower()=='favorite':
                if gametag.text:
                    myValues.append(("$FAVO","\n\t\t<favorite>true</favorite>"))
                    favo = True
            if gametag.tag.lower()=='lastplayed':
                if gametag.text:
                    myValues.append(("$LASTPLAY",gametag.text))
                    lastplay = True
            if gametag.tag.lower()=='path':
                tmppath = gametag.text
                if '/' in tmppath:
                    gcpath = tmppath[tmppath.rindex('/')+1:]
                if '\\' in tmppath:
                    gcpath = tmppath[tmppath.rindex('\\')+1:]
                if '/' not in tmppath and '\\' not in tmppath:
                    gcpath = tmppath
        if not favo :
            myValues.append(("$FAVO",""))
        if not pc :
            myValues.append(("$PLAYCOUNT","0"))
        if not lastplay :
            myValues.append(("$LASTPLAY",""))
        if myValues:
            currValues[gcpath]=myValues
    return currValues

def downloadmissingrom(downsites,sysid,romname,syspath):
    logging.info ('DOWNLOAD MISSING ROM '+romname)
    success = False
    for site in downsites['sites']:
        for system in site['systems']:
            if int(system['id'])==int(sysid):
                for downurl in system['urls']:
                    logging.info ('========================== DOING '+str(sysid)+' ROM '+romname)    
                    destfile = apicalls.downloadRom(downurl,syspath,romname)
                    ###### TO DO:
                    #### BREAK FROM LOOP IF SUCCESFULL
                    #### CHECK IF IT COMPRESSED AND UNCOMPRESS
    return success

def findMissingGames(config,systemid,havelist,apikey,uuid,systems,queue,doDownload):
    allgames = apicalls.getAllGames(systemid,apikey,uuid)
    missfile ='missing.txt'
    f = open (missfile,'a')
    sysname = ''
    for thissys in systems:
        if systemid in thissys['id']:
            sysname = thissys['name']
            break
    f.write('++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\nSystem: '+sysname+'\n++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++\n')
    for game in allgames:
        if game['gameid'] not in havelist:
            output =''
            thisGame = apicalls.getGame(game['gameid'],apikey,uuid)
            output = output+'Game: '+thisGame['game']['names'][0]['text']+'\n==========================================================================\nRoms:\n'
            queue.put(['gamelabel','text','Missing:'+thisGame['game']['names'][0]['text']])
            roms=''
            for rom in thisGame['game']['roms']:
                if doDownload:
                    if downloadmissingrom(config['downsites'],systemid,rom['filename'],thissys['path']):
                        pass
                    else:
                        roms = roms+rom['filename']+'\n'
                else:
                    roms = roms+rom['filename']+'\n'
            roms = roms + '--------------------------------------------------------------------------\n'
            output=output+roms
            f.write(output)
    f.close()
    return

def writeXML(sq,writeFile,q):
    #q.put(['gamelabel','text','WRITING GAMELIST'])
    print ('Writing Gamelist',flush=True)
    thesegames =[]
    ## LOOP OF ALL FILES FINISHED
    donequeue = False
    while not donequeue:
        try:
            value = sq.get_nowait()
            try:
                if value:
                    try:
                        writeFile.write(value[0]+"")
                    except:
                        try:
                            wvalue = value[0].encode().decode('utf-8')
                            writeFile.write(wvalue)
                        except:
                            pass
                        
                    thesegames.append(value[1])
            except Exception as e:
                logging.error ('###### UNABLE TO WRITE TO GAMELIST FILE:'+str(e))
        except:
            donequeue = True
    return thesegames


def fileProcess(currFileIdx,romfiles,currglvalues,system,q,sq):
    #Get the rom file in the list atposition currFileIdx and validate is usable
    file = str(romfiles[currFileIdx])
    try:
        logging.info ('####### STARTING WITH FILE '+str(file))
        logfilename = file
    except:
        logfilename = ''
        logging.info ('####### STARTING WITH FILE ')
    if '/' in file:
        filename = file[file.rindex('/')+1:]
    if '\\' in file:
        filename = file[file.rindex('\\')+1:]
    if '\\' not in file and '/' not in file:
        filename = file
    if '.' in file:
        filext = file[file.rindex('.'):]
    else:
        filext=''
    if filename in currglvalues:
        oldValues = currglvalues[filename]
    else:
        ### This file was not in the CURRENT XML
        oldValues=[('$LASTPLAY','0'),('$FAVO',''),('$PLAYCOUNT','0')]
    logging.info ('####### TRIMMED TO FILE '+logfilename)
    if (not filext in system['extension']) or ('gamelist.xml' in file.lower()):
            logging.info ('###### This file ['+logfilename+'] is not in the list of accepted extensions')
            #q.put(['scrapPB','valueincrease'])
            sq.put ('')
            return '','',''
    else:
        return file,filext,oldValues

def getSystems(allsys,selected,all):
    retsys = []
    for system in allsys:
        if not system['name']:
            logging.error ('THERE IS AN ERROR IN SYSTEM '+str(system))
            continue
        mysys = dict()
        if all or system['name'].lower() in selected:
            mysys['name']=system['name']
            mysys['id']=system['id']
            mysys['path']=system['path']
            mysys['extension']=system['extension']
            retsys.append(mysys)
            if not all:
                selected.remove(system['name'])
    if selected:
        print ('COULD NOT LOCATE SYSTEMS '+str(selected),flush=True)
        logging.error ('COULD NOT LOCATE SYSTEMS '+str(selected))
    return retsys

def sortRoms(q,remotesystems,apikey,uuid,companies,config,logging,thn):
    ### Getting all files
    systems=dict()
    for sys in remotesystems['systems']:
        systems[sys['id']]=sys['names'][0]['name_eu'].replace(' ','_').lower()
    systems[168]='notgame'
    systems[0]='unknown'
    romfiles = [x for x in sorted(Path(config['config']['sort']['indir']).glob('**/*.*')) ]
    for file in romfiles:
        if ('.cfg' in str(file)) or ('.xml' in str(file)) or ('.png' in str(file))or ('.mp4' in str(file)):
            continue
        print ('Processing '+str(file))
        logging.info ('####### GETTING CHECKSUMS FOR '+str(file)+'THREAD['+str(thn)+']')
        mysha1,mymd5,mycrc = getChecksums(file,config,logging,thn)
        logging.info ('####### GOT CHECKSUMS FOR '+str(file)+' THREAD['+str(thn)+']')
        ## PROCESS FILE AND START DOING MAGIC
        logging.info ('####### GETTING INFO FOR '+str(file)+' THREAD['+str(thn)+']')
        result = getInfoFromAPI ([0],str(file),mysha1,mymd5,mycrc,apikey,uuid,logging,thn)
        sysid = result['game']['system']['id']
        try:
            sysname = systems[int(sysid)]
        except:
            print ('There\'s an error in the backend, system '+str(sysid)+' is not recognized.')
            sys.exit()
        origfile = str(file)
        destdir  = config['config']['sort']['outdir']+sysname
        if not os.path.exists(destdir):
            os.makedirs(destdir)
        destfile = destdir+origfile[origfile.rindex('/'):]
        print ('Copying '+origfile+' to '+destfile)
        subprocess.call (['cp',origfile,destfile])
    return

def normalizeText(text):
    return text.replace(' ','_').replace('\'','').replace('(','').replace(')','').replace('&','and').replace(',','').replace('.','').replace('-','_').replace('!','').replace('?','').replace(':','').replace(';','').replace('/','_').replace('\\','_').replace('"','').replace('___','_').replace('__','_').replace('_',' ').lower()

def createGenreGamelist(gamelistname):
    writeFile = open(gamelistname,'w',encoding="utf-8")
    writeFile.close()
    return

def appendCustomCollection(gamelistname,rompath):
    print ("Adding "+rompath+" to "+gamelistname)
    writeFile = open(gamelistname,'a',encoding="utf-8")
    writeFile.write(rompath+'\n')
    writeFile.close()

def returnGenres(romfile,config,system,logging,apikey,uuid,thn):
    mysha1,mymd5,mycrc = getChecksums(str(romfile),config,logging,thn)
    logging.info ('####### GOT CHECKSUMS FOR '+str(romfile)+' THREAD['+str(thn)+']')
    ## PROCESS FILE AND START DOING MAGIC
    logging.info ('####### GETTING INFO FOR '+str(romfile)+' THREAD['+str(thn)+']')
    result = getInfoFromAPI (system['id'],str(romfile),mysha1,mymd5,mycrc,apikey,uuid,logging,thn)
    mygenres =[]
    for mygenre in result['game']['genres']:
        if mygenre['id'] not in mygenres:
            mygenres.append(mygenre['id'])
    if not mygenres:
        mygenres.append(999999)
    return (mygenres)

def sortGenres(q,genres,systems,apikey,uuid,companies,config,logging,remoteSystems,selectedSystems,scanqueue,origrompath,trans,thn,cli=False):
    hpath = str(Path.home())+'/.emulationstation/collections/'
    if not os.path.exists(hpath):
        makedirs(hpath)
    print ('Sorting Roms By Genre',flush=True)
    standard_genres =dict()
    for genre in genres['genres']:
        genre_name=[normalizeText(myname['text']) for myname in genre['names'] if myname['language']=='en']
        if genre_name:
            genre_filename = hpath+"custom-"+genre_name[0]+'.cfg'
            standard_genres[genre['id']] =  genre_filename
            createGenreGamelist(genre_filename)
    standard_genres[999999] =  hpath+"custom-unknown.cfg"
    createGenreGamelist(hpath+"custom-unknown.cfg")
    if not systems:
        logging.info ('###### NO SYSTEMS TO SCAN')
        print ('COULD NOT FIND ANY SYSTEMS - EXITING',flush=True)
        return
    logging.info ('###### DO ALL SYSTEMS?')
    try:
        doallsystems = (selectedSystems[1]==trans['all'])
    except:
        if not selectedSystems:
            doallsystems=True
        else:
            doallsystems=False
    logging.info ('###### DO ALL SYSTEMS '+str(doallsystems))
    logging.info ('###### THESE ARE THE SELECTED SYSTEMS:'+str(selectedSystems))
    systemList = getSystems(systems,selectedSystems,doallsystems)

    for system in systemList:
        if system['name'].lower()=='retropie':
            print ('Skipping System '+str(system['name']))
            continue
        print ('Doing System '+str(system['name']))
        try:
            spath = system['path']
            if spath[-1] != '/':
                spath = spath +'/'
            logging.info ('###### GOING FOR LOCAL PATH')
            try:
                if config['config']['fixedmediadir']:
                    if config['config']['fixedmediadir']=='/':
                        excpaths=['/NONE/','/NONE/','/NONE/']
                    else:
                        tmpex =config['config']['fixedmediadir'][1:]+system['name']
                        excpaths=[tmpex,tmpex,tmpex]
                else:
                    excpaths = ['/images/','videos/','/marquees/']
                if config['config']['recursive']:
                    romfiles = [x for x in sorted(Path(spath).glob('**/*.*')) if ((excpaths[0] not in x.as_posix()) and (excpaths[1] not in x.as_posix()) and (excpaths[2] not in x.as_posix()) and ('.cfg' not in x.name) and ('.save' not in x.name) and ('.xml' not in x.name))]
                else:
                    romfiles = [x for x in sorted(Path(spath).glob('*.*')) if ((excpaths[0] not in x.as_posix()) and (excpaths[1] not in x.as_posix()) and (excpaths[2] not in x.as_posix()) and ('.cfg' not in x.name) and ('.save' not in x.name) and ('.xml' not in x.name))]
            except:
                romfiles = [x for x in sorted(Path(spath).glob('*.*')) if ((excpaths[0] not in x.as_posix()) and (excpaths[1] not in x.as_posix()) and (excpaths[2] not in x.as_posix()) and ('.cfg' not in x.name) and ('.save' not in x.name) and ('.xml' not in x.name))]
            logging.info ('###### FOUND '+str(len(romfiles))+' ROMS FOR SYSTEM')
        except Exception as e:
            logging.error ('####### CANNOT OPEN SYSTEM DIR '+system['path']+' ERROR '+str(e))
            errormsg = trans['nodirmsg'].replace('$DIR',str(system['path'])).replace('$SYS',str(system['name']))
            print ('ERROR '+errormsg)
            #q.put(['errorlabel','text',errormsg])
            continue
        try:
            logging.info('==========='+str(len(romfiles)))
        except Exception as e:
            logging.error(str(e))
        if len(romfiles)==0:
            errormsg = trans['noromsmsg'].replace('$DIR',str(system['path'])).replace('$SYS',str(system['name']))
            print ('ERROR '+errormsg)
            #q.put (['errorlabel','text',errormsg])
            continue
        print ('Found '+str(len(romfiles))+ ' roms for the system')
        if 75 in system['id']:
            sysid=75
            print ('This is an arcade system')
        else:
            sysid=system['id'][0]
        #### SYSTEM IMAGE
        for myrom in romfiles:
            filext = myrom.suffix
            if (not filext in system['extension']) or ('gamelist.xml' in str(myrom).lower()):
                print ('This file ['+str(myrom.name)+'] is not in the list of accepted extensions')
                continue

            genres = returnGenres(myrom,config,system,logging,apikey,uuid,thn)
            for mygenre in genres:
                try:
                    customcollectionfile = standard_genres[mygenre]
                    appendCustomCollection(customcollectionfile,str(myrom))
                except:
                    logging.error ('###### COULD NOT FIND GENRE '+str(mygenre))
                    print ('Could not find genre '+str(mygenre))
        pass        
    ### IM HERE
    return
    
def scanSystems(q,systems,apikey,uuid,companies,config,logging,remoteSystems,selectedSystems,scanqueue,origrompath,trans,thn,cli=False):
    hpath = str(Path.home())+'/.retroscraper/'
    print ('Scanning Files',flush=True)
    #q.put(['gamelabel','text','Scanning Files'])
    missfile ='missing.txt'
    if ospath.isfile(missfile):
        remove(missfile)
    logging.info ('###### INTO SYSTEM SCAN')
    if not systems:
        logging.info ('###### NO SYSTEMS TO SCAN')
        print ('COULD NOT FIND ANY SYSTEMS - EXITING',flush=True)
        return
    getmeout = False
    emptyGameTag = r"\n\t<game>\n\t\t<rating>$RATING</rating>\n\t\t<name>$NAME</name>\n\t\t<marquee>$MARQUEE</marquee>\n\t\t<image>$IMAGE</image>\n\t\t<publisher>$PUBLISHER</publisher>\n\t\t<releasedate>$RELEASEDATE</releasedate>\n\t\t<players>$PLAYERS</players>\n\t\t<video>$VIDEO</video>\n\t\t<genre>$GENRE</genre>\n\t\t<path>$PATH</path>\n\t\t<developer>$DEVELOPER</developer>\n\t\t<thumbnail/>\n\t\t<desc>$DESCRIPTION</desc>$FAVO\n\t\t<playcount>$PLAYCOUNT</playcount>\n\t\t<lastplayed>$LASTPLAY</lastplayed>\n\t</game>"
    logging.info ('###### DO ALL SYSTEMS?')
    try:
        doallsystems = (selectedSystems[1]==trans['all'])
    except:
        if not selectedSystems:
            doallsystems=True
        else:
            doallsystems=False
    logging.info ('###### DO ALL SYSTEMS '+str(doallsystems))
    logging.info ('###### THESE ARE THE SELECTED SYSTEMS:'+str(selectedSystems))
    systemList = getSystems(systems,selectedSystems,doallsystems)
    for system in systemList:
        if system['name'].lower()=='retropie':
            print ('Skipping System '+str(system['name']))
            continue
        print ('Doing System '+str(system['name']))
        logging.info ('###### START SCAN SYSTEM '+str(system))
        if config['config']['MountPath']:
            system['path']=system['path'].replace(origrompath,config['config']['MountPath'])
        if not testPath(system['path'],logging,thn):
            errormsg = trans['nodirmsg'].replace('$DIR',str(system['path'])).replace('$SYS',str(system['name']))
            logging.error ('###### COULD NOT FIND PATH '+system['path'])
            #q.put(['errorlabel','text',errormsg])
            print ('ERROR '+errormsg,flush=True)
            continue
        outXMLFile = system['path']+'gamelist.xml'
        try:
            createdtime = os.path.getmtime(outXMLFile)
            now =time.time()
            elapsed = now-createdtime
        except:
            ## There was no original Gamelist File
            elapsed = config['config']['olderthan'] - 1
            pass
        if elapsed<config['config']['olderthan']:
            print ('System '+str(system['name'])+' was updated less than '+str(int(config['config']['olderthan']/24/60/60))+' days ago. Skipping',flush=True)
            continue
        currglvalues = getGamelistData(outXMLFile)
        tmpxmlFile = hpath+'gamelist'+str(os.getpid())+'.xml'
        writeFile = open(tmpxmlFile,'w',encoding="utf-8")
        writeFile.write("<?xml version='1.0' encoding='utf-8'?><gameList>")
        romfiles=[]
        print ('Scanning Directory',flush=True)
        #q.put(['gamelabel','text','SCANNING DIRECTORY'])
        try:
            spath = system['path']
            if spath[-1] != '/':
                spath = spath +'/'
            logging.info ('###### GOING FOR LOCAL PATH')
            try:
                if config['config']['fixedmediadir']:
                    if config['config']['fixedmediadir']=='/':
                        excpaths=['/NONE/','/NONE/','/NONE/']
                    else:
                        tmpex =config['config']['fixedmediadir'][1:]+system['name']
                        excpaths=[tmpex,tmpex,tmpex]
                else:
                    excpaths = ['/images/','videos/','/marquees/']
                if config['config']['recursive']:
                    romfiles = [x for x in sorted(Path(spath).glob('**/*.*')) if ((excpaths[0] not in x.as_posix()) and (excpaths[1] not in x.as_posix()) and (excpaths[2] not in x.as_posix()) and ('.cfg' not in x.name) and ('.save' not in x.name) and ('.xml' not in x.name))]
                else:
                    romfiles = [x for x in sorted(Path(spath).glob('*.*')) if ((excpaths[0] not in x.as_posix()) and (excpaths[1] not in x.as_posix()) and (excpaths[2] not in x.as_posix()) and ('.cfg' not in x.name) and ('.save' not in x.name) and ('.xml' not in x.name))]
            except:
                romfiles = [x for x in sorted(Path(spath).glob('*.*')) if ((excpaths[0] not in x.as_posix()) and (excpaths[1] not in x.as_posix()) and (excpaths[2] not in x.as_posix()) and ('.cfg' not in x.name) and ('.save' not in x.name) and ('.xml' not in x.name))]
            logging.info ('###### FOUND '+str(len(romfiles))+' ROMS FOR SYSTEM')
        except Exception as e:
            logging.error ('####### CANNOT OPEN SYSTEM DIR '+system['path']+' ERROR '+str(e))
            errormsg = trans['nodirmsg'].replace('$DIR',str(system['path'])).replace('$SYS',str(system['name']))
            print ('ERROR '+errormsg)
            #q.put(['errorlabel','text',errormsg])
            continue
        try:
            logging.info('==========='+str(len(romfiles)))
        except Exception as e:
            logging.error(str(e))
        if len(romfiles)==0:
            errormsg = trans['noromsmsg'].replace('$DIR',str(system['path'])).replace('$SYS',str(system['name']))
            print ('ERROR '+errormsg)
            #q.put (['errorlabel','text',errormsg])
            continue
        print ('Found '+str(len(romfiles))+ ' roms for the system')
        if 75 in system['id']:
            sysid=75
            print ('This is an arcade system')
        else:
            sysid=system['id'][0]
        #### SYSTEM IMAGE
        try:
            cm = config['config']['cleanmedia']
        except:
            config['config']['cleanmedia'] = False
        if config['config']['cleanmedia']:
            try:
                print ('Deleting Images')
                #q.put(['gamelabel','text','DELETING IMAGES'])
                if config['config']['fixedmediadir']:
                    if config['config']['fixedmediadir'][0]=='/':
                        deldir = config['config']['fixedmediadir']+system['name']
                    else:
                        deldir = system['path']+config['config']['fixedmediadir'][1:]
                else:
                    deldir = system['path']+'images/'
                if deldir =='/' or deldir=='.' or deldir=='' :
                    print ('ABORTING!!! Risk of deleting everything !! Check your mediapath!!')
                    sysexit(1)
                else:
                    removedir(config,deldir,logging,thn)
                logging.info ('###### DELETED DIRECTORY IMAGES ')
            except Exception as e:
                logging.info ('###### COULD NOT DELETE DIRECTORY IMAGES '+str(e))
            try:
                print ('Deleting Videos')
                #q.put(['gamelabel','text','DELETING VIDEOS'])
                if config['config']['fixedmediadir']:
                    if config['config']['fixedmediadir'][0]=='/':
                        deldir = config['config']['fixedmediadir']+system['name']
                    else:
                        deldir = system['path']+config['config']['fixedmediadir'][1:]
                else:
                    deldir = system['path']+'videos/'
                if deldir =='/' or deldir=='.' or deldir=='' :
                    print ('ABORTING!!! Risk of deleting everything !! Check your mediapath!!')
                    sysexit(1)
                else:
                    removedir(config,deldir,logging,thn)
                logging.info ('###### DELETED DIRECTORY VIDEOS ')
            except Exception as e:
                logging.info ('###### COULD NOT DELETE DIRECTORY VIDEOS '+str(e))
            try:
                print ('Deleting Marquees')
                #q.put(['gamelabel','text','DELETING MARQUEES'])
                if config['config']['fixedmediadir']:
                    if config['config']['fixedmediadir'][0]=='/':
                        deldir = config['config']['fixedmediadir']+system['name']
                    else:
                        deldir = system['path']+config['config']['fixedmediadir'][1:]
                else:
                    deldir = system['path']+'marquees/'
                if deldir =='/' or deldir=='.' or deldir=='' :
                    print ('ABORTING!!! Risk of deleting everything !! Check your mediapath!!')
                    sysexit(1)
                else:
                    removedir(config,deldir,logging,thn)
                logging.info ('###### DELETED DIRECTORY MARQUEES ')
            except Exception as e:
                logging.info ('###### COULD NOT DELETE DIRECTORY MARQUEES '+str(e))
        if config['config']['fixedmediadir'] :
            if config['config']['fixedmediadir'][0]!='/':
                meddir = system['path']+config['config']['fixedmediadir'][2:]
            else:
                meddir = config['config']['fixedmediadir']+system['name']+'/'
            if not pathExists(config,meddir,logging,thn):
                makedir(config,meddir,logging,thn)
        else:
            if not pathExists(config,system['path']+'images/',logging,thn):
                makedir(config,system['path']+'images/',logging,thn)
            if not pathExists (config,system['path']+'videos/',logging,thn):
                makedir(config,system['path']+'videos/',logging,thn)
            if not pathExists (config,system['path']+'marquees/',logging,thn):
                makedir(config,system['path']+'marquees/',logging,thn)
        bpath = system['path'].replace('/roms/','/overlays/')+'bezels/'
        if not pathExists(config,bpath,logging,thn):
            makedir(config,bpath,logging,thn)

        currFileIdx = 0
        totalfiles = len(romfiles)
        sq = Queue()
        tq = Queue()
        ## NUMBER OF TOTAL THREADS / CAREFULL,  MORE THAN 5 MAY GET YOU KICKED OUT OF THE BACKEND ;-)
        nthrds = 5
        thread_list = [None]*nthrds
        havegames=[]
        gamecounter = 0
        alldone = False
        finishedthreads=False
        #initialize threads
        for thrn in range (0,nthrds):
            logging.info ('###### CHECKING THREAD '+str(thrn)+' WHICH HAS VALUE '+str(thread_list[thrn]))
            file =''
            while file =='' and (not alldone):
                if (currFileIdx < totalfiles):
                    file,filext,oldValues = fileProcess(currFileIdx,romfiles,currglvalues,system,q,sq)
                    currFileIdx = currFileIdx+1
                else:
                    alldone=True
            if not alldone:
                try:
                    logging.info ('###### CHECKING THREAD '+str(thrn)+' WHICH HAS VALUE '+str(thread_list[thrn]))
                    showfile = file.encode().decode('utf-8')
                except:
                    logging.info('###### EXCEPTION '+str(e)+' IN THREAD '+str(thrn))
                    showfile = ''
                logging.info ('###### STARTING FILE '+showfile+' IN THREAD '+str(thrn))
                uthrn = (int(system['id'][0])*100000)+(currFileIdx*10)+thrn
                thread = Thread(target=getFileInfo,args=(file,system,companies,emptyGameTag,apikey,uuid,q,sq,config,logging,filext,tq,uthrn,oldValues,thrn,cli))
                thread_list[thrn]=thread
                thread.start()
                gamecounter = gamecounter +1
        rq = 0
        while not finishedthreads:
            rq = rq + 1
            try:
                value = tq.get_nowait()
                rq = 0
                logging.info ('###### QUEUE VALUE '+str(value) )
                try:
                    thread_list[value].join()
                    thread_list[value]=None
                except:
                    pass
                if None in thread_list:
                    ## There is an empty thread, run it!
                    file =''
                    while file =='' and (not alldone):
                        if (currFileIdx < totalfiles):
                            file,filext,oldValues = fileProcess(currFileIdx,romfiles,currglvalues,system,q,sq)
                            currFileIdx = currFileIdx+1
                        else:
                            alldone = True
                    if not alldone:
                        try:
                            logging.info ('###### CHECKING THREAD '+str(value)+' WHICH HAS VALUE '+str(thread_list[value]))
                            showfile = file.encode().decode('utf-8')
                        except:
                            logging.info('###### EXCEPTION '+str(e)+' IN THREAD '+str(value))
                            showfile = ''
                        logging.info ('###### STARTING FILE '+showfile+' IN THREAD '+str(value))
                        uthrn = (int(system['id'][0])*100000)+(currFileIdx*10)+value
                        thread = Thread(target=getFileInfo,args=(file,system,companies,emptyGameTag,apikey,uuid,q,sq,config,logging,filext,tq,uthrn,oldValues,value,cli))
                        thread_list[value]=thread
                        thread.start()
                        gamecounter = gamecounter +1
                if (not any(thread_list)) and alldone:
                    finishedthreads=True
            except:
                sleep (0.01)
                if rq == 1000:
                    rq =0
                    if (not any(thread_list)):
                        tq.put(0)
                pass
            if (gamecounter == 100) or finishedthreads:
                havegames = havegames + writeXML(sq,writeFile,q)
                gamecounter = 0
        #havegames = havegames + writeXML(sq,writeFile,q)
        logging.info ('###### CLOSING GAMELIST.XML IN THREAD '+str(thn))
        writeFile.write("\n</gameList>")
        logging.info ('###### FILE CLOSING GAMELIST.XML IN THREAD '+str(thn))
        writeFile.close()
        ###############################################################################
        bkcount = 1
        try:
            logging.info ('###### CHECKING IF NEED TO BACKUP OR NOT IN THREAD '+str(thn))
            chk  = config['config']['nobackup']
        except:
            logging.info ('###### THERE IS NO VALUE IN CONFIG IN THREAD '+str(thn))
            chk = False
            logging.info ('######DEFAULTED TO TRUE IN THREAD '+str(thn))
        if not chk:
            logging.info ('###### I NEED TO DO BACKUP IN THREAD '+str(thn))
            while ospath.isfile(outXMLFile+'.'+str(bkcount)):
                logging.info ('###### FILE '+str(bkcount)+' EXISTS IN THREAD '+str(thn))
                bkcount = bkcount + 1
            logging.info ('###### FILE '+str(bkcount)+' DOES NOT EXIST - MAKING BACKUP IN THREAD '+str(thn))
            if ospath.isfile(outXMLFile):
                result = copyfile(outXMLFile,outXMLFile+'.'+str(bkcount))
                logging.info ('###### FILE '+str(bkcount)+' BACKUP DONE IN THREAD '+str(thn))
        logging.info ('###### COPYING NEW GAMELIST IN THREAD '+str(thn))
        result = copyfile(tmpxmlFile,outXMLFile)
        remove(tmpxmlFile)
        logging.info ('###### COPIED NEW GAMELIST IN THREAD '+str(thn))
        try:
            findmissing=config['config']['domissfile']
        except:
            findmissing = False
        try:
            doDownload=config['config']['downmissing']
        except:
            doDownload = False
        if findmissing or doDownload:
            logging.info ('##### GOING TO FIND MISSING GAMES IN THREAD '+str(thn))
            findMissingGames(config,sysid,havegames,apikey,uuid,systems,q,doDownload)
            logging.info ('##### DONE FINDING MISSING GAMES IN THREAD '+str(thn))
    if ospath.isfile(hpath+'system.png'):
        remove(hpath+'system.png')
    if ospath.isdir(str(Path.home())+'/.retroscraper/imgtmp/'):
        logging.info ('###### REMOVING TEMP IMAGES DIR')
        rmtree(str(Path.home())+'/.retroscraper/imgtmp/')
        logging.info ('###### REMOVED TEMP IMAGES DIR')
    if ospath.isdir(str(Path.home())+'/.retroscraper/filetmp/'):
        logging.info ('###### REMOVING TEMP IMAGES DIR')
        rmtree(str(Path.home())+'/.retroscraper/filetmp/')
        logging.info ('###### REMOVED TEMP IMAGES DIR')
    logging.info ('###### INFORMING SCAN DONE IN THREAD '+str(thn))
    print ('Scan Done!',flush=True)
    #q.put(['scandone','scandone',False])
    logging.info ('###### INFORMED SCAN DONE IN THREAD '+str(thn))
    #q.put(['gamelabel','text',''])
    #q.put(['gamedesc','text',''])
    #q.put(['gameimage','source',''])
    #q.put(['sysImage','source',''])
    #q.put(['sysImageGame','source',''])
    #q.put(['sysLabel','text',trans['alldone']])
    #q.put(['scandone','scandone',True])
    return

def getAbsRomPath(testpath,thn):
    #print ('Received path '+testpath)
    retpath = ''
    if 'roms' in testpath.lower():
        #print ('YES')
        retpath = testpath[:testpath.rindex('roms')+4]
        #print (retpath)
    return retpath
