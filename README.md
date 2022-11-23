# retroscraper-rpie
Trimmed down version of retroscrpaer, designed for a lighter experience and RetroPie Integration

## Install

### Standalone

Log in via ssh to your RetroPie machine

Cange to the home directory
```
cd
```
Recomemnded: update your system
```
sudo apt update
sudo apt upgrade
```
Install pip and update
```
wget https://bootstrap.pypa.io/get-pip.py
python3 get-pip.py
python3 -m pip install --upgrade pip wheel setuptools
```
Get the latest version of retroscraper
```
git clone https://github.com/zayamatias/retroscraper-rpie.git
```
Change dirctory to retroscraper location
```
cd retroscraper-rpie
```
Install dependencies
```
python3 -m pip install -r dependencies.txt
```
You're done

### To be used with retropie_setup

Download retroscraper.sh and copy it to your RetroPie supplemetary directory, usually:

/home/pi/RetroPie/scriptmodules/supplementary

Run retropie setup and go to manage optiona packages. By the bottom of the list you should see the retroscraper function.

Install it and once done go to configure/options to run it.

You're done

## Running 

Go to the retropie-rpie directoy
```
cd retroscraper-rpie
```
run the software 
```
python3 retroscraper.py
```
Wait until your whole system is scraped.

## Command modifiers:


#### --systemsfile FILE

Location of the, usually called, es_systems.cfg file, this is the emulation station file that holds the information for the systems ands roms directories you have set up. If you do not use this flag, retroscraper will look into the usual places.

#### --recursive

Scan subfloders in your system folder

#### --relativepaths

Store relative paths in the gamelist

#### --mediadir DIR

This commabd gives you the option to chose the destination of the media files, you have three options:

- Leave it blank, and by default it will save the edia under 3 directories (images, marquees and videos) within the system directory, for example ~/RetroPie/roms/amiga/images, ~/RetroPie/roms/amiga/videos,~/RetroPie/roms/amiga/marquees

- Put an absolute path (DIR starting by /) and it will save everything under that absolute path, but appending the system name to avoid clashing of names, for example, if DIR is '/home/pi/medias' it will create '/home/pi/medias/amiga' and save media there.

- Put a relative path (DIR not starting bye /), and it will create this path under the system roms directory, for example, if DIR is 'emulationstation/medias' it will save under ~/RetroPie/roms/amiga/images/emulationstation/medias

Of course, amiga has been chosen as an example here, the system name will be taken from your configuration files.

#### --preferbox

Download boxes instead of screenshots for games

#### --novideodown

Do not download videos (to save space if needd)

#### Name Decorators:

The following options allow you to add 'decorators' to the name taht is going to be displayed in your game list. They are disabled by default.

#### --version

Will get any string that matches (Vxxxxx) in the rom filename and insert it in the final name for the game. If your rom is called _ _'My Super Game (v3).zip'_ _ , your game name will be displayed as _ _'My Super Game (v3)'_ _ 

#### --hack 

Similar to previous option, but searching for matches of _ _(xxxx Beta xxxx)_ _ or _ _(xxxx Hack xxxx)_ _

#### --country

Simiular to previous option, but searching for matches of _ _(xx)_ _ where xx is an identified country/language shortname, such as usa,fr, en, es, etc..

#### --disk

Simiilar to previous option, but searching for matches of _ _(Tape xx of yy)_ _ or _ _(Disk xx of yy)_ _ where xx and yy are numbers or letters such as _ _(Tape A)_ _ or _ _(Disk 1 of 2)_ _

#### --brackets

As in previous commands, but this time it will match the brackets '[]' and insert tehm in the game name.

All previous options will relay on the filename, so if the information is not in the filename, it will not show in the final name.

#### --bezels & --sysbezels

This two options allow you to download the game bezels (this is usually a pciture surrounding the playing area) and will allow you to decide if you want to download the generic system bezel if the game bezel is not found.


#### --language LN & --google

Language to use for game names & synposis

If you select to use google translate, the games desciptions which are not available in the selected language, will be translated by google.

Default language is 'en'

#### --nodb

Retroscraper creates a local retroscraper.db file, where it will store all the checksums for yoru files. This is done to avoid losing extra time in subsequent runs, specially fro large files. If you prefer to calculate the hashes on teh fly, use this.

#### --nobackup

Since latest version, RetroScraper will autoamtically generate a backup of your gamelist.xml file for each system, by adding a number to it (gamelist.xml.1, gamelist.xml.2 and so forth). If you want to avoid having these backups created, use this command.

#### --systems sys1,sys2,sys3...

Provide a list of systems you will like to have scanned, separated by comma [_,_].The names are the same as the ones found in your es_systems.cfg file, under the _\<system\>\<name\>SYSTEMNAME\</name\>\</system\>_ tag.


