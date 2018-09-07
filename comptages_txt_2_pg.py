# coding: utf8
#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      m.reboux
#
# Created:     23/01/2018
# Copyright:   (c) m.reboux 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import linecache
import encodings
import codecs
import psycopg2
import pprint
import argparse
from argparse import RawTextHelpFormatter
import sys
import os.path
import configparser


# ATTENTION : fichier encodé en UCS-2 little endian // utf_16_le
# passer le fichier en UTF-8 pour pouvoir le lire
rep_import = './fichiers_a_importer/'

# répertoire courant
script_dir = os.path.dirname(__file__)

# lecture du fichier de configuration
config = configparser.ConfigParser()
config.read( script_dir + '/config.ini')

# la base de données
strConnDB = "host="+ config.get('postgresql', 'host') +" dbname="+ config.get('postgresql', 'db') +" user="+ config.get('postgresql', 'user') +" password="+ config.get('postgresql', 'passwd')
# le schéma
DB_schema = config.get('postgresql', 'schema')



# variables globales
mode_debug = False

enquete_id          = 0
enquete_comm_insee  = ""
enquete_description = ""
enquete_site        = ""
enquete_datedeb     = ""

stationsArray = []


station_id          = 0
station_code        = ""
station_description = ""
station_commune     = 0
station_sens        = ""
campagne_date_deb   = ""
campagne_heure_deb  = ""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def Logguer(logString):

  # cette fonction permet de sortir correctement les print() en mode dev (console python) et terminal

  if (mode_debug == False):
    # sortie console en UTF-8
    utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)
    print( logString, file=utf8stdout)
  else:
    # sortie dans la console python
    print( logString )


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def TraiterDonneesFIM():

  Logguer("")
  Logguer("Lecture et import des données de comptage routier")
  Logguer("Les noms et coordonnées des stations seront récupérées depuis un flux GeoJSON" )
  Logguer("Les données de comptage seront récupérées depuis les fichiers FIM" )
  Logguer("")

  # on commence par lire le fichier des stations en geojson pour en faire un tableau
  LectureStations()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def LectureStations():

  Logguer("")
  Logguer("Lecture des infos des stations")
  Logguer("Les noms et coordonnées des stations seront récupérées depuis un flux GeoJSON" )
  Logguer("")

  import requests
  import json

  # mode url
  url_station = config.get('umap', 'poste_comptage_auto')

  # on ouvre une session
  r = requests.Session()

  # on voit si on est en mode proxy ou pas
  if (config.get('proxy', 'enable') == "true" ):
    # oui alors on va lire la configuration
    proxyConfig = {
      'http': ''+config.get('proxy','http')+'',
      'https': ''+config.get('proxy','https')+'',
    }
    r.proxies = proxyConfig


  # on récupère le geojson
  try:
    # requête HTTP à travers le proxy si proxy configuré
    geojson_content = r.get(url_station).text

    # test du début pour voir si c'est du JSON
    if (geojson_content[0:26] != "{\"type\":\"FeatureCollection"):
      Logguer( "ERREUR ! Le contenu récupérer ne semble pas être du json. Un pb de proxy ?" )
      Logguer("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
      Logguer(geojson_content)
      sys.exit()

  except Exception as err:
    print( str(err) )


  # pas de pb : on continue
  #print(geojson_content)
  # parse
  stations = json.loads(geojson_content)

  i = 0
  for feature in stations['features'] :
    i = i +1
    #print( feature['properties']['nom'] +' | '+ feature['properties']['description'] +' | '+ str(feature['geometry']['coordinates']) )
    # on remplit le tableau
    #stationsArray.append(feature['properties']['nom'], feature['properties']['description'])

    # la structure du JSON de umap pouvant être bizare : on essaie sur chaque attribut
    commune_insee = "*"
    nom = "*"
    description = "*"
    coordonnees = "*"

    try: commune_insee = feature['properties']['commune_insee']
    except: pass
    try: nom = feature['properties']['nom']
    except: pass
    try: description = feature['properties']['description']
    except: pass
    try: coordonnees = str(feature['geometry']['coordinates'])
    except: pass

    Logguer( commune_insee + " | " + nom  + " | " + description + " | " + coordonnees)


    # debug
    #if (i == 3) :  sys.exit()

  Logguer( str(i) + " stations lues depuis la couche umap")






# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def lectureMetadonneesFIM():

  # on déclare ces variables comme globales
  global station_commune
  global station_code
  global station_sens
  global campagne_date_deb
  global campagne_heure_deb


  # on lit la première ligne pour récupéer les métadonnées
  L_metadata = linecache.getline(f_to_import,1)
  # on splitte
  metadata = L_metadata.split('.')

  # on met en mémoire
  # code de la station de comptage
  station_commune = "35" + metadata[1].strip()
  station_code = station_commune + "_" + metadata[2]
  station_sens = metadata[4].strip()
  campagne_date_deb = '20' + metadata[5].strip() +'-'+ metadata[6].strip() +'-'+ metadata[7].strip()
  campagne_heure_deb = metadata[8].strip()   # '  09' -> '09'
  campagne_heure_deb_jolie = metadata[8].strip() + ':' + metadata[9].strip() + ':00'

  Logguer( " Infos sur la station" )
  Logguer( "   " + station_commune + ' | ' + station_code + ' | ' + station_sens + ' | ' + campagne_date_deb + ' ' + campagne_heure_deb_jolie )
  Logguer( "" )



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def lectureDonneesFIM():

  Logguer( u"Les données de comptage" )

  f = open(f_to_import,'r')

  f_content = f.readlines()

  # on pointe les lignes qui ne sont pas des données
  metadata = [0, 1, 170, 171]

  # numéro de ligne dans le fichier entier
  i = 0
  # numéro de ligne de données comptage
  i_data = 0
  # numéro du jour
  j_courant = 0
  # heure du jour
  h_courante = 0


  # on boucle sur les lignes
  for line in f_content:

    if not i in metadata:
      # print line[:-1]


      # il faut gérer le changement de jour calendaire
      # on va utiliser le modulo pour ça
      if i_data > 0 :  # on ne regarde la toute première donnée
        modulo = (i_data) % 24
        #print '## ' + str(modulo)

        # si modulo = 0 => on est le début d'un nouveau jour
        if modulo == 0 :
          # on incrémente un jour
          j_courant = j_courant + 1
          # et on remet à zéro le compteur des heures
          h_courante = 0
        else:
          # on incrémente le compteur des heures de la journée
          h_courante = h_courante + 1


      # le timestamp  '2016-10-11 09:00:00'
      date_tmst = calculTimeStamp(j_courant, h_courante)

      # on calcule l'intervalle de mesure
      intervalle = calculIntervalle(h_courante)

      # on caclul le total TV pour la ligne en cours
      total_TV = lectureLigneTV(line[:-1])

      # pour les données PL on envoie le numéro de la ligne en cours
      total_PL = lectureLignePL(i)

      # on fait un calcul simple pour retrouver le nb de véhicules légers
      total_VL = total_TV - total_PL

      # sortie console
      Logguer( "   [" + str(i) + ' ' + str(i_data) + '] | jour ' + str(j_courant).zfill(2) + ' heure ' + str(h_courante).zfill(2) + ' | ' + date_tmst + ' | ' + intervalle + '  TV = '  + str(total_TV) + '  ( ' + str(total_VL) + ' VL + ' + str(total_PL) + ' PL )' )

      # on peut incrémenter le compteur des valeurs de trafic
      i_data = i_data + 1



      # on arrête à une ligne précise
      if i > 168:
        break


    i = i + 1

  # fermeture du fichier
  f.close()



def lectureLigneTV(ligne):

  #print "   Donnees Tout Vehicule"

  i = 0
  totalTV = 0

  # on splite sur le .
  hits = ligne.split('.')

  for hit in hits:
    # on dépadde les zéros  0003 -> 3
    value = hit.lstrip('0')

    # pour garder une valeur à 0
    if value == '': value = '0'
    #print str(i) + ' : ' + value

    # on additionne
    totalTV = totalTV + int(value)

    i = i + 1
  # fin de la boucle

  #print ' total ligne = ' + str(total)

  # on retourne le total
  return totalTV



def lectureLignePL(num_ligneTV):

  #print "   Donnees Tout Vehicule"
  #print "num ligne PL = " + str(num_ligneTV)

  i = 0
  totalPL = 0

  # on va à la ligne TV + le décalage dans le fichier
  ligne = linecache.getline(f_to_import, num_ligneTV + 171)

  # on splite sur le .
  hits = ligne[:-1].split('.')

  for hit in hits:
    # on dépadde les zéros  0003 -> 3
    value = hit.lstrip('0')

    # pour garder une valeur à 0
    if value == '': value = '0'
    #print str(i) + ' : ' + value

    # on additionne
    totalPL = totalPL + int(value)

    i = i + 1
  # fin de la boucle


  return totalPL


def calculIntervalle(h_deb):

  #print "h_deb horodatage = " + str(h_deb)

  # on calcule la chaîne qui représente l'intervalle ex :  08H00-09H00
  # on commence par calculer l'heure de fin : facile
  h_fin = h_deb + 1

  # sauf si on change de jour
  if h_fin == 24: h_fin = 0

  # on formate les 2 heures sur 2 digit
  s_h_deb = str(h_deb).zfill(2)
  s_h_fin = str(h_fin).zfill(2)

  s_intervalle = s_h_deb + 'H00-' + s_h_fin + 'H00'
  #print s_intervalle

  return s_intervalle



def calculTimeStamp(jour, heure):

  # format = 2016-10-11 09:00:00
  # l'heure = fin de l'intervalle de mesure + formatage '9' -> '09:00:00'

  # gestion du changement de jour
  # jour
  if jour == 0:
    date = campagne_date_deb
  else:
    date = campagne_date_deb[0:8] + str(int(campagne_date_deb[-2:]) + jour)

  # heure
  if heure == 23: h_fin = 0
  else: h_fin = heure + 1

  h_fin = str(h_fin).zfill(2) + ':00:00'

  TimeStamp = str(date) + ' ' + h_fin

  return TimeStamp



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def insertEnqueteInDB ():

  # on va lire le fichier csv /fichiers_a_importer/_enquete_a_creer.csv
  # pour insérer ces infos en base

  Logguer( "Création d'une enquête" )

  f_enquete = './fichiers_a_importer/_enquete_a_creer.csv'
  f = open(f_enquete,'r')
  f_content = f.readlines()

  # on compte le nb de lignes car on attend au moins 2, ent-ête y compris
  if len(f_content) == 1 :
    Logguer( "  aucune enquête à insérer : arrêt" )
    f.close()
    sys.exit("")
  else:
    i = 0
    # on boucle sur les lignes
    for line in f_content :

      # pour sauter la première ligne
      if i != 0 :
        #Logguer( line )
        # récupération de l'intégralité de la ligne pour requête insertion
        SQL_insert_requete = "INSERT INTO "+DB_schema+".comptage_enquete VALUES ( nextval('mobilite_transp.comptage_enquete_enquete_uid_seq')," + line.replace('"','\'') + " );"
        #Logguer( SQL_insert_requete )


         # connection à la base
        try:
          # connexion à la base, si plante, on sort
          conn = psycopg2.connect(strConnDB)
          cursor = conn.cursor()

        except:
          Logguer( "connexion à la base impossible")

        try:
          # on lance la requête
          cursor.execute(SQL_insert_requete)
          conn.commit()
          Logguer( "  1 enquête insérée" )

        except Exception as err:
          if err.pgcode == "23505":
            Logguer( "  erreur : cette campagne existe déjà (ligne " + str(i) + ")" )
          else:
            Logguer( "  impossible d'exécuter la requête INSERT")
            Logguer( "  PostgreSQL error code : " + err.pgcode )

        # si on est là c'est que tout s'est bien passé
        try:
          cursor.close()
          conn.close()
        except:
          Logguer("")

      # incrément du compteur
      i = i + 1

  # on ferme le fichier
  f.close()



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



if __name__ == '__main__':


  parser = argparse.ArgumentParser(description="""
Ce script permet de lire des données de comptages routiers et de les importer dans une base de données.
  étape 1 : créer une enquête (si besoin)
  étape 2 : lire les infos sur les stations depuis la couche qui localise les stations de comptage
  étape 3 : lire le fichier de comptage
  étape 4 : écriture dans la base de données : la station sera créée si nécessaire et les données de comptage insérées.

Les fichiers à importer sont à placer dans le répertoire "fichiers_a_importer".

Scénario classique :
  1. insérer une enquête ->  comptages_txt_2_pg.py -enquete
  2. insérer les données de comptage ->  comptages_txt_2_pg.py -donnees_fim x  où x = id d'enquête

""", formatter_class=RawTextHelpFormatter)


  parser.add_argument("-enquete", help="""Pour créer des enquêtes dans la base de données. Va lire le fichier _enquete_a_creer.csv""")

  parser.add_argument("-donnees_fim", help="""Va lire les fichier au format FIM dans le répertoire "fichiers_a_importer". Les stations de comptage seront créées si nécessaire.""")


  #Logguer( "++++++++++++++++++++++++++++++++++++++++ " )

  # debug for coding
  #insertEnqueteInDB()
  #lectureMetadonneesFIM()
  #lectureDonneesFIM()
  #lectureInfosStation()
  #sys.exit("arret dedug")

  # for debug
  #print( 'Number of arguments:', len(sys.argv), 'arguments.' )
  #print( 'Argument List:', str(sys.argv) )

  testIdEnquete = 2

  # mode debug optionnel pur sortie console
  if ('-debug' in sys.argv):
    mode_debug = True
    testIdEnquete = 3
    pass

  # pour insérer une enquête
  if ('-enquete' in sys.argv):
    # on passe directemnt à la fonction
    insertEnqueteInDB()
    # et on arrête car elle ne doit faire que ça
    sys.exit()

  # pour traiter les fichiers FIM
  if ('-donnees_fim' in sys.argv):
    # on verifie qu'un id d'enquête a bien été passé
    if ( len(sys.argv) == testIdEnquete +1 ):
      # on vérifie maintenant que c'est numérique
      if str(sys.argv[testIdEnquete]).isnumeric() :
        # tout est ok : on appelle la fonction
          TraiterDonneesFIM()
          # et on arrête car cette fonction ne doit faire que ça
          sys.exit()
      else:
        Logguer("erreur : l'identifiant d'enquête n'est pas numérique")
        sys.exit()
    else:
      Logguer("erreur : il manque l'identifiant de l'enquête")
      sys.exit()

  # si on est là c'est que aucune commande n'a été demandée -> on affiche l'aide
  Logguer(parser.print_help())

  #Logguer( "++++++++++++++++++++++++++++++++++++++++ " )



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# https://fastkml.readthedocs.io/en/latest/
