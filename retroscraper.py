import os
import sys
import argparse
import scrapfunctions
from sys import exit as sysexit
from platform import system
from threading import Thread
from queue import Queue
from time import sleep
from signal import signal,SIGINT
import logging
import apicalls
from pathlib import Path as sysPath
from datetime import datetime

## Override Argparse exit on error
class ArgumentParser(argparse.ArgumentParser):    
    def error(self, message):
        sys.stderr.write('error: %s\n' % message)
        self.print_help()
        sys.exit(2)

globalapikey='A6512E49024B7D064F6A61B4F02E1270B1D77793'
version = '0.5'
trans = dict()
cli = False


if __name__ == '__main__':
    supportedlanguages ={'af': 'afrikaans','sq': 'albanian','am': 'amharic','ar': 'arabic','hy': 'armenian','az': 'azerbaijani'\
                    ,'eu': 'basque','be': 'belarusian','bn': 'bengali','bs': 'bosnian','bg': 'bulgarian','ca': 'catalan'\
                    ,'ceb': 'cebuano','ny': 'chichewa','zh-cn': 'chinese (simplified)','zh-tw': 'chinese (traditional)'\
                    ,'co': 'corsican','hr': 'croatian','cs': 'czech','da': 'danish','nl': 'dutch','en': 'english'\
                    ,'eo': 'esperanto','et': 'estonian','tl': 'filipino','fi': 'finnish','fr': 'french','fy': 'frisian'\
                    ,'gl': 'galician','ka': 'georgian','de': 'german','el': 'greek','gu': 'gujarati','ht': 'haitian creole'\
                    ,'ha': 'hausa','haw': 'hawaiian','iw': 'hebrew','he': 'hebrew','hi': 'hindi','hmn': 'hmong'\
                    ,'hu': 'hungarian','is': 'icelandic','ig': 'igbo','id': 'indonesian','ga': 'irish','it': 'italian'\
                    ,'ja': 'japanese','jw': 'javanese','kn': 'kannada','kk': 'kazakh','km': 'khmer','ko': 'korean'\
                    ,'ku': 'kurdish (kurmanji)','ky': 'kyrgyz','lo': 'lao','la': 'latin','lv': 'latvian','lt': 'lithuanian'\
                    ,'lb': 'luxembourgish','mk': 'macedonian','mg': 'malagasy','ms': 'malay','ml': 'malayalam','mt': 'maltese'\
                    ,'mi': 'maori','mr': 'marathi','mn': 'mongolian','my': 'myanmar (burmese)','ne': 'nepali','no': 'norwegian'\
                    ,'or': 'odia','ps': 'pashto','fa': 'persian','pl': 'polish','pt': 'portuguese','pa': 'punjabi','ro': 'romanian'\
                    ,'ru': 'russian','sm': 'samoan','gd': 'scots gaelic','sr': 'serbian','st': 'sesotho','sn': 'shona','sd': 'sindhi'\
                    ,'si': 'sinhala','sk': 'slovak','sl': 'slovenian','so': 'somali','es': 'spanish','su': 'sundanese','sw': 'swahili'\
                    ,'sv': 'swedish','tg': 'tajik','ta': 'tamil','te': 'telugu','th': 'thai','tr': 'turkish','uk': 'ukrainian'\
                    ,'ur': 'urdu','ug': 'uyghur','uz': 'uzbek','vi': 'vietnamese','cy': 'welsh','xh': 'xhosa','yi': 'yiddish'\
                    ,'yo': 'yoruba','zu': 'zulu'} 
    now = datetime.now()
    dts = now.strftime("%Y.%m.%d.%H.%M.%S")
    if not os.path.isdir(str(sysPath.home())+'/.retroscraper/imgtmp/'):
        os.makedirs(str(sysPath.home())+'/.retroscraper/imgtmp/')
    if not os.path.isdir(str(sysPath.home())+'/.retroscraper/filetmp/'):
        os.makedirs(str(sysPath.home())+'/.retroscraper/filetmp/')
    logging.basicConfig(filename=str(sysPath.home())+'/.retroscraper/retroscraper'+dts+'.log', level=logging.ERROR)
    parser = ArgumentParser(description='RetroScraper...supercharge your roms with metadata!')
    parser.add_argument('--systemsfile', help='location of the es_systems.cfg file)',nargs=1)
    parser.add_argument('--nobackup', help='Do not backup gamelist.xml file',action='store_true')
    parser.add_argument('--relativepaths', help='Use relative paths instead of full paths',action='store_true')
    parser.add_argument('--recursive', help='Search subdirctories in systems paths',action='store_true')
    parser.add_argument('--mediadir', help='Single media dir wwhere all media is going to be stored, strat with \'/\' for absolute path (this will append the system name autoamtically), otherwise relative to system path',nargs=1)
    parser.add_argument('--keepdata', help='Keep favorites and play count of your games',action='store_true')
    parser.add_argument('--preferbox', help='Prefer boxes instead of screenshots',action='store_true')
    parser.add_argument('--novideodown', help='Do not download videos',action='store_true')
    parser.add_argument('--nodb', help='Do not use a local DB to store file hashes (might impact performance nagatively)',action='store_true')
    parser.add_argument('--language', help='Select language for descriptions',nargs=1)
    parser.add_argument('--google', help='Use google translate if description not found in your language',action='store_true')
    parser.add_argument('--country', help='Add country decorator from filename [Sonic (es)]',action='store_true')
    parser.add_argument('--disk', help='Add disk decorator from filename [Sonic (disk 1/2)]',action='store_true')
    parser.add_argument('--version', help='Add version decorator from filename [Sonic V1.10]',action='store_true')
    parser.add_argument('--hack', help='Add hack decorator from filename [Sonic (madhedgehog hack)]',action='store_true')
    parser.add_argument('--brackets', help='Add brackets decorator from filename (Sonic [TT])',action='store_true')
    parser.add_argument('--bezels', help='Download bezels for games',action='store_true')
    parser.add_argument('--sysbezels', help='Download system bezel if game bezel is not found',action='store_true')
    parser.add_argument('--cleanmedia', help='Clean media directroies before downloading',action='store_true')
    #parser.add_argument('--linkmedia', help='Creat media links to save space (only in Linux/RPI)',action='store_true')
    parser.add_argument('--systems', help='List of systems to scan (comma separated values)',nargs=1)
    parser.add_argument('--debug', help='Use for debugging purposes',action='store_true')
    parser.add_argument('--listsystems', help='Return a list of available systems',action='store_true')
    parser.add_argument('--listlangs', help='List available languages',action='store_true')
    parser.add_argument('--appver', help='Display retroscraper version and stop',action='store_true')
    parser.add_argument('--sort', help='Sort your roms by system, put all your roms in one directory and output structure to second directory',nargs=2,metavar=('ORIG','DEST'))
    parser.add_argument('--olderthan', help='Skip gamelists that are not older than X days',nargs=1)
    try:
        args = parser.parse_args()
        argsvals = vars(args)
    except argparse.ArgumentError as exc:
        print (exc.message, '\n', exc.argument)
    try:
        listsys = argsvals['listsystems']
    except:
        listsys=False
    try:
        listlangs = argsvals['listlangs']
    except:
        listlangs=False
    logging.info ('###### LOADING RETROSCRAPER CONFIG')
    q=Queue()
    apikey =globalapikey
    uuid = scrapfunctions.getUniqueID()
    config = scrapfunctions.loadConfig(logging,q,apikey,uuid,'MAIN')

    cli = True
    silent = True

    try:
        config['config']['sort']=dict()
        config['config']['sort']['indir'] = argsvals['sort'][0]
        config['config']['sort']['outdir'] = argsvals['sort'][1]
        if config['config']['sort']['indir'][-1]!='/':
            config['config']['sort']['indir'] = config['config']['sort']['indir']+'/'
        if config['config']['sort']['outdir'][-1]!='/':
            config['config']['sort']['outdir']=config['config']['sort']['outdir']+'/'
    except:
        config['config']['sort']['indir'] = ''
    try:
        showver = argsvals['appver']
        if showver:
            print (str(version))
            sys.exit()
    except Exception as e:
        pass

    try:
        debug = argsvals['debug']
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)
    except:
        pass
    try:
        config['config']['relative'] = argsvals['relativepaths']
    except:
        config['config']['relative'] = False
    try:
        config['config']['recursive'] = argsvals['recursive']
    except:
        config['config']['recursive'] = False
    try:
        if 'decorators' in config['config'].keys:
            pass
    except:
        config['config']['decorators']=dict()
    try:
        config['config']['decorators']['country']= argsvals['country']
    except:
        config['config']['decorators']['country']= False
    try:
        config['config']['decorators']['disk']= argsvals['disk']
    except:
        config['config']['decorators']['disk']= False
    try:
        config['config']['decorators']['version']= argsvals['version']
    except:
        config['config']['decorators']['version']= False
    try:
        config['config']['decorators']['hack']= argsvals['hack']
    except:
        config['config']['decorators']['hack']= False
    try:
        config['config']['decorators']['brackets']= argsvals['brackets']
    except:
        config['config']['decorators']['brackets']= False
    try:
        config['config']['usegoogle']= argsvals['google']
    except:
        config['config']['usegoogle']= False
    try:
        config['config']['bezels']= argsvals['bezels']
    except:
        config['config']['bezels']= False
    try:
        config['config']['preferbox']= argsvals['preferbox']
    except:
        config['config']['preferbox']= False
    try:
        config['config']['novideodown']= argsvals['novideodown']
    except:
        config['config']['novideodown']= False
    try:
        config['config']['sysbezels']= argsvals['sysbezels']
    except:
        config['config']['sysbezels']= False
    try:
        config['config']['language']= argsvals['language'][0].lower()
    except:
        config['config']['language']= 'en'
    try:
        config['config']['cleanmedia']= argsvals['cleanmedia']
    except:
        config['config']['cleanmedia']= False
    try:
        config['config']['olderthan']= int(argsvals['olderthan'][0])*24*60*60
    except:
        config['config']['olderthan']= 0

    try:
        fixedmediadir = argsvals['mediadir'][0]
        if fixedmediadir:
            if fixedmediadir[-1] != '/':
                fixedmediadir=fixedmediadir+'/'
            if fixedmediadir[0]!='/':
                if './' not in fixedmediadir:
                    if fixedmediadir[0]!='.':
                        fixedmediadir='.'+fixedmediadir
                    if fixedmediadir[1]!='/':
                        fixedmediadir=fixedmediadir[0]+'/'+fixedmediadir[1:]
            else:
                if not os.path.exists(fixedmediadir):
                    try:
                        result = os.makedirs(fixedmediadir)
                    except Exception as e:
                        print ('CANNOT CREATE DIRECTORY ['+fixedmediadir+'] - ERROR ['+str(e)+'] - PLS VERIFY AND TRY AGAIN')
                        sysexit(1)
    except:
        fixedmediadir =''
    config['config']['fixedmediadir']=fixedmediadir
    try:
        systemstoscanstr = argsvals['systems'][0].lower()
        if systemstoscanstr[-1]==',':
            systemstoscanstr=systemstoscanstr[:-1]
        systemstoscan=systemstoscanstr.split(',')
    except:
        systemstoscan = []
    
    try:
        config['config']['SystemsFile']= argsvals['systemsfile'][0]
    except:
        pass
    try:
        config['config']['nodb']= argsvals['nodb']
    except:
        config['config']['nodb']= False
    try:
        config['config']['keepdata']= argsvals['keepdata']
    except:
        config['config']['keepdata']= False
    try:
        config['config']['nobackup']= argsvals['nobackup']
    except:
        config['config']['nobackup']= False
    complete = apicalls.getLanguagesFromAPI(apikey,uuid,'MAIN')
    try:
        trans = complete['en']
    except:
        print ("CANNOT CONNECT TO THE BACKEND, PLEASE TRY AGAIN LATER")
        sysexit()
    scanqueue = Queue()
    q=Queue()
    if not scrapfunctions.isValidVersion(version,apikey,uuid,'MAIN'):
        print ('SORRY! YOU NEED TO UPGRADE TO THE LATEST VERSION '+apicalls.backendURL()+'/download.html')
        logging.error('###### THIS IS NOT THE LATEST VERSION OF RETROSCRAPER')
        sysexit()
    logging.debug('###### CONFIG :'+str(config))
    if not os.path.isfile(config['config']['SystemsFile']) or '.retroscraper' in config['config']['SystemsFile']:
        ### Try to locate es_systems:
        if os.path.isfile('~/.emulationstation/es_systems.cfg'):
            config['config']['SystemsFile'] = '~/.emulationstation/es_systems.cfg'
        if os.path.isfile('/etc/emulationstation/es_systems.cfg'):
            config['config']['SystemsFile'] = '/etc/emulationstation/es_systems.cfg'
        if not os.path.isfile(config['config']['SystemsFile']):
            print ('I cannot find your systems file, please use the "--systemsfile" flag to point to the es_systems.cfg file in your system')
            logging.error('###### SYSTEMS FILE CANNOT BE FOUND '+str(config['config']['SystemsFile']))
            sysexit()
    logging.info ('###### LOADING SYSTEMS FROM BACKEND')
    remoteSystems = apicalls.getSystemsFromAPI(apikey,uuid,'MAIN')
    ## SYSTEM SELECTION TOGGLER
    systems = scrapfunctions.loadSystems(config,apikey,uuid,remoteSystems,q,trans,logging)
    if listsys:
        for system in systems:
            print (system['name'])
        sysexit(0)
    if listlangs:
        for short,desc in supportedlanguages.items():
            print (short+','+desc)
        sysexit(0)
    logging.info ('###### LOADING COMPANIES FROM BACKEND THREAD[MAIN]')
    companies = scrapfunctions.loadCompanies(apikey,uuid,'MAIN')
    rompath = scrapfunctions.getAbsRomPath(systems[0]['path'],'MAIN')
    print ('Starting scraping', flush=True)
    logging.info ('###### STARTING SCRAPPING ')
    logging.info ('STARTING THREADS')
    if config['config']['sort']['indir']:
        print ("Going to sort your roms from "+config['config']['sort']['indir']+" to "+config['config']['sort']['outdir'])
        thread = Thread(target= scrapfunctions.sortRoms,args=(q,remoteSystems,apikey,uuid,companies,config,logging,'MAIN'))
    else:
        thread = Thread(target= scrapfunctions.scanSystems,args=(q,systems,apikey,uuid,companies,config,logging,remoteSystems,systemstoscan,scanqueue,rompath,trans,'MAIN',True))
    thread.start()
    system =''
    game=''
    scrapping = True
    while scrapping:
        #try:
        #    qu = q.get_nowait()
        #    if qu[0].lower()=='scrappb' and qu[1].lower()=='max':
        #        pass
        #    if qu[0].lower()=='scrappb' and qu[1].lower()=='valueincrease':
        #        pass
        #    if qu[0].lower()=='syslabel':
        #        system = qu[2].strip().replace('\n',' ')
        #         print ('SYSTEM '+system, flush=True)
        #    if qu[0].lower()=='gamelabel':
        #        game = qu[2].strip().replace('\n',' ')
        #        print (game, flush=True)
        #except Exception as e:
        #    pass
        sleep(0.01)
        if not thread.is_alive():
            scrapping= False
    print('SCRAPPING ENDED --- Thank you for using retroscraper!!\n')
    logging.info ('###### ALL DONE!')
    sysexit(0)
