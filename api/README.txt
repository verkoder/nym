# Nymology API Python Wrapper
Nymology seeks deeper meaning within language and between ourselves.
By acquiring structured knowledge spanning disciplines, regions and cultures, we strive towards a singularity of meaning and understanding.

Nymology invites the collection and analysis of idea sets – a set of dimensions used to frame a concept.
The resulting “thesaurus” can be used to populate knowledgebase systems for natural language processing.

On the website, the general public can play games & activities using story templates, idea sets and other meaning structures.

The Nymology API is provided so developers can include the data and methods in their products or services.
Nymology is open source. Developers, please contribute activities or improvements!

http://nymology.org

# FILE STRUCTURE:
# api/__init__.py
# api/nymology.py
# api/README.txt
# api/data/

# API ROOT FOLDER = 'api'
# API DATA FOLDER = 'api/data'

# USING THE WRAPPER:
from nymology import NymologyAPI
nym = NymologyAPI(
    username='gus',
    password='nym'
)

# WRAPPER METHODS:
nym.create(dataset, data)
nym.read(dataset, pk)
nym.update(dataset, pk, data)
nym.delete(dataset, pk)
nym.get_page(dataset, page)
nym.get_data(dataset)
nym.get_file(dataset)
nym.save_file(dataset)
nym.save_database()
nym.endpoints()

# Set home data folder:
nym = NymologyAPI(home='data')

# Query local Django server:
nym = NymologyAPI(local=True)


##########################
# INGEST DATA INTO DJANGO:
# From a Django shell, load the API & data ingestor:
from api.nymology import NymologyAPI
from ingestor import *
nym = NymologyAPI()

# Either run a full API ingestion..
mass_ingest(nym)

# ..or use saved JSON files
mass_ingest(nym, saved=True)

##########################
# DATA MINING:
# Fortunes
from spin.crawl import *
mine_fortunes()

##########################
# DEVELOPER GUIDE
##########################

#### WEB COLORS
body        White on Bootstrap-secondary (#292b2c gray)
dropdowns:
  menu      LightGray on Black
  hover     White on Purple
a:          Thistle
a:hover     White on Purple
a:active    White on DarkSlateGray
btn.Create  Bootstrap-outline-success (green)
    Read    Bootstrap-outline-primary (blue)
    Update  Bootstrap-outline-warning (yellow)
    Delete  Bootstrap-outline-danger (red)
    Login   Purple
    Guess   Bootstrap-success (green)
    Feel    DarkRed
    Tell    RoyalBlue
    Flip    Olive

#### templates/bits/ INCLUDES
# .HTML     ARGS                INCLUDE             PAGES (see/ unless noted)
book        qode,spun                               flip/quote+fortune, make/story_xxxs, story, tale, tell/tale+verse+phrase
common      thing,request.user  infocard            make/story_save, make/tale_save
compare     a, b                infocard            poly+quadramath
infocard    thing,text          -                   add/delete, polymap, poly+quadratile, feel/polynym+mood,
                                                           polypuzzle, quadrahuh, thegist, unquote
infogrid    things,plus,useq    infocard            section, find/polynym,quadranym, quizzection, thegist, unquote, poly+quadraset,
                                                           union, feel/site, flip/fortune+quote, tell/phrase
poly_icon   thing                                   polynym, quadramath
poly_systems poly_dict,ttl                          systems, poly_area, poly_src
quad        thing,eros,pos                          flip/quote, quadranym
qode        qode                                    fable, phrase
show        thing,text          infocard
shows       things,plus,useq    infogrid
show_pairs  pairs,              show_story          make/story_xxx
            phrases,quadranyms
show_story  phrases,quadranyms  infogrid x 2        story, tell/verse
show_tale   thing,things        infocard,infogrid   tale, make/tale_xx, tell/tale

#### templates/add/ INCLUDES
# .HTML     ARGS                INCLUDE bits/       PAGES (add/ unless noted)
common      form,msg,spun,thing pick_realm          fable, phrase, poly+quadranym, poly+quadraset, vectornym, make/story_save, make/tale_save
delete      object   ^??^       infocard

#### templates/see/ INCLUDES
# .HTML     ARGS                                    PAGES
commons     table                                   poly+quadranym database

#### templates/play/ INCLUDES
# .HTML     ARGS                INCLUDE bits/       PAGES (add/ unless noted)
fame        app,color,fx,hi,                        gamer
            msg,games
gamer       app,color,                              *ALL* games!
            at,nu,points,user,winner
