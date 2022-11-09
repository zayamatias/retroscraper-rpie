import os
import sys
import argparse
import scrapfunctions
from sys import exit as sysexit
from platform import system
from threading import Thread
from queue import Queue
from time import sleep
from random import randint,randrange
from signal import signal,SIGINT
import logging
import apicalls
from pathlib import Path as sysPath

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
    if not os.path.isdir(str(sysPath.home())+'/.retroscraper/imgtmp/'):
        os.makedirs(str(sysPath.home())+'/.retroscraper/imgtmp/')
        print ('Starting retroscraper - be Patient :-)')
    if not os.path.isdir(str(sysPath.home())+'/.retroscraper/filetmp/'):
        os.makedirs(str(sysPath.home())+'/.retroscraper/filetmp/')
        print ('Starting retroscraper - be Patient :-)')
    logging.basicConfig(filename='retroscraper.log', level=logging.DEBUG)
    parser = ArgumentParser(description='RetroScraper...supercharge your roms with metadata!')
    parser.add_argument('--systemsfile', help='location of the es_systems.cfg file)',nargs=1)
    parser.add_argument('--nobackup', help='Do not backup gamelist.xml file',action='store_true')
    parser.add_argument('--keepdata', help='Keep favprites and play count of your games',action='store_true')
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
    parser.add_argument('--linkmedia', help='Creat media links to save space (only in Linux/RPI)',action='store_true')
    parser.add_argument('--remote', help='Scan a remote RetroPie intsallation add USER and PASSWORD (--remote USER PASSWD)',nargs=2)
    parser.add_argument('--systems', help='List of systems to scan (comma separated values)',nargs=1)
    try:
        args = parser.parse_args()
        argsvals = vars(args)
    except argparse.ArgumentError as exc:
        print (exc.message, '\n', exc.argument)
    print ('Loading RetroScraper config File')
    logging.info ('###### LOADING RETROSCRAPER CONFIG')
    q=Queue()
    apikey =globalapikey
    uuid = scrapfunctions.getUniqueID()
    config = scrapfunctions.loadConfig(logging,q,apikey,uuid,'MAIN')
    cli = True
    silent = True
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
        systemstoscan = argsvals['systems'][0].lower().split(',')
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
    trans = complete['en']
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
            print ('There seems to be an error in your retroscraper config file, I cannot find the systems configuration file (usually something like es_systems.cfg)')
            logging.error('###### SYSTEMS FILE CANNOT BE FOUND '+str(config['config']['SystemsFile']))
            sysexit()
    scrapfunctions.saveConfig(config,scanqueue)
    print ('Loading systems from Backend')
    logging.info ('###### LOADING SYSTEMS FROM BACKEND')
    remoteSystems = apicalls.getSystemsFromAPI(apikey,uuid,'MAIN')
    ## SYSTEM SELECTION TOGGLER
    systems = scrapfunctions.loadSystems(config,apikey,uuid,remoteSystems,q,trans,logging)
    if not systemstoscan:
        print ('Scanning All Systems')
    else:
        print ('Scanning Systems '+str(systemstoscan))
    print ('Loading companies from backend')
    logging.info ('###### LOADING COMPANIES FROM BACKEND THREAD[MAIN]')
    companies = scrapfunctions.loadCompanies(apikey,uuid,'MAIN')
    rompath = scrapfunctions.getAbsRomPath(systems[0]['path'],'MAIN')
    print ('Starting scraping')
    logging.info ('###### STARTING SCRAPPING ')
    logging.info ('STARTING THREADS')
    thread = Thread(target= scrapfunctions.scanSystems,args=(q,systems,apikey,uuid,companies,config,logging,remoteSystems,systemstoscan,scanqueue,rompath,trans,'MAIN',True))
    thread.start()
    system =''
    game=''
    scrapping = True
    while scrapping:
        try:
            qu = q.get_nowait()
            if qu[0].lower()=='scrappb' and qu[1].lower()=='max':
                pass
            if qu[0].lower()=='scrappb' and qu[1].lower()=='valueincrease':
                pass
            if qu[0].lower()=='syslabel':
                system = qu[2].strip().replace('\n',' ')
                print ('SYSTEM '+system)
            if qu[0].lower()=='gamelabel':
                game = qu[2].strip().replace('\n',' ')
                print (game)
        except Exception as e:
            pass
        sleep(0.01)
        if not thread.is_alive():
            scrapping= False
    print('SCRAPPING ENDED --- Thank you for using retroscraper!!\n')
    logging.info ('###### ALL DONE!')
    sysexit(0)
