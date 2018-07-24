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
import geojson


# ATTENTION : fichier encodé en UCS-2 little endian // UTF-16
# passer le fichier en UTF-8 pour pouvoir le lire
f_to_import = './fichiers_a_importer/test'

# url vers le GeoJSON en ligne dans uMap
url_stations_geojson = "http://umap.openstreetmap.fr/fr/datalayer/497861/"
f_geojson = './fichiers_a_importer/stations.geojson'

# le fichier de correspondance
f_corres_stations = './fichiers_a_importer/stations_correspondances.txt'

# la base de données
strConnDB = "host='localhost' dbname='bdu' user='geocarto' password='geocarto'"


# variables globales
mode_verbeux = False

enquete_id          = 0
enquete_comm_insee  = ""
enquete_description = ""
enquete_site        = ""
enquete_datedeb     = ""

station_commune     = 0
station_id          = 0
station_code        = ""
station_sens        = ""
campagne_date_deb   = ""
campagne_heure_deb  = ""

# pour avoir une sortie console en UTF-8
utf8stdout = open(1, 'w', encoding='utf-8', closefd=False)


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def lectureInfosStation():

  print("")
  print("Lecture des infos des stations")
  print("Les noms et coordonnées des stations seront récupérées depuis un flux GeoJSON" )
  print("")

  geojson_content = open(f_geojson,'r').read()
  #print(geojson_content)

  stations = geojson.loads(geojson_content)
  print(stations)

  # ça ça marche
  #print( stations[0].properties['identifiant']  )

  # il faut boucler
  #for station in stations:
  #  print( station[0].properties['identifiant'] )




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

  print( " Infos sur la station" )
  print( "   " + station_commune + ' | ' + station_code + ' | ' + station_sens + ' | ' + campagne_date_deb + ' ' + campagne_heure_deb_jolie )
  print( "" )



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def lectureDonneesFIM():

  print( u"Les données de comptage" )

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
      print( "   [" + str(i) + ' ' + str(i_data) + '] | jour ' + str(j_courant).zfill(2) + ' heure ' + str(h_courante).zfill(2) + ' | ' + date_tmst + ' | ' + intervalle + '  TV = '  + str(total_TV) + '  ( ' + str(total_VL) + ' VL + ' + str(total_PL) + ' PL )' )

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

  print( "Création d'une enquête", file=utf8stdout )
  print( "Création d'une enquête" )

  f_enquete = './fichiers_a_importer/_enquete_a_creer.csv'
  f = open(f_enquete,'r')
  f_content = f.readlines()

  # on compte le nb de lignes car on attend au moins 2, ent-ête y compris
  if len(f_content) == 1 :
    print( "  aucune enquête à insérer : arrêt", file=utf8stdout )
    print( "  aucune enquête à insérer : arrêt" )
    f.close()
    sys.exit("")
  else:
    i = 0
    # on boucle sur les lignes
    for line in f_content :

      # pour sauter la première ligne
      if i != 0 :
        #print( line )
        # récupération de l'intégralité de la ligne pour requête insertion
        SQL_insert_requete = "INSERT INTO mobilite_transp.comptage_enquete VALUES ( nextval('mobilite_transp.comptage_enquete_enquete_uid_seq')," + line.replace('"','\'') + " );"
        #print( SQL_insert_requete )


         # connection à la base
        try:
          # connexion à la base, si plante, on sort
          conn = psycopg2.connect(strConnDB)
          cursor = conn.cursor()

        except:
          print( "connexion à la base impossible")

        try:
          # on lance la requête
          cursor.execute(SQL_insert_requete)
          conn.commit()
          print( "1 enquête insérée" )

        except Exception as err:
          if err.pgcode == "23505":
            print( "  erreur : cette campagne existe déjà" )
          else:
            print( "  impossible d'exécuter la requête INSERT")
            print( "  PostgreSQL error code : " + err.pgcode )

        # si on est là c'est que tout s'est bien passé
        try:
          cursor.close()
          conn.close()
        except:
          print("")

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
  étape 4 : écriture dans la base de données : la sation sera créée si nécessaire et les données de comptage insérées.

Les fichiers à importer sont à placer dans le répertoire "fichiers_a_importer".

""", formatter_class=RawTextHelpFormatter)


  # debug for coding
  #insertEnqueteInDB()
  #lectureMetadonneesFIM()
  #lectureDonneesFIM()
  #lectureInfosStation()
  #sys.exit("arret dedug")

  print( "++++++++++++++++++++++++++++++++++++++++ " )

  # mode verbeux
  parser.add_argument("-v", help="mode verbeux")

  # lecture des infos sur les stations
  parser.add_argument("-c", help="""Pour lancer une commande spécifique""")

  # print help
  #parser.print_help()

  # for debug
  #print 'Number of arguments:', len(sys.argv), 'arguments.'
  #print( 'Argument List:', str(sys.argv))


  # pour insérer une enquête
  if ('-enquete' in sys.argv):
    # on passe directemnt à la fonction
    insertEnqueteInDB()
    pass


  print( "++++++++++++++++++++++++++++++++++++++++ " )



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# https://fastkml.readthedocs.io/en/latest/
