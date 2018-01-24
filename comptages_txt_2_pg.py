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
import psycopg2
#import xml.etree.ElementTree as ET
from lxml import etree
from pykml import parser
import pprint


# ATTENTION : fichier encodé en UCS-2 little endian // UTF-16
# passer le fichier en UTF-8 pour le lire
f_to_import = './fichiers_a_importer/test'

# le fichier qui contient le code et nom de la station de comptage et ses coordonnées
kml_stations = './fichiers_a_importer/stations.kml'

# la base de données
strConnDB = "host='localhost' dbname='bdu' user='geocarto' password='geocarto'"


# variables globales
enquete_id = 0
station_id = 0
station_code = ""
station_sens = ""
campagne_date_deb = ""
campagne_heure_deb = ""



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def lectureMetadonneesFIM():

  # on déclare ces variables comme globales
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
  station_code = metadata[2]
  station_sens = metadata[4].strip()
  campagne_date_deb = '20' + metadata[5].strip() +'-'+ metadata[6].strip() +'-'+ metadata[7].strip()
  campagne_heure_deb = metadata[8].strip()   # '  09' -> '09'
  campagne_heure_deb_jolie = metadata[8].strip() + ':' + metadata[9].strip() + ':00'

  print " Infos sur la station"
  print "   " + station_code + ' | ' + station_sens + ' | ' + campagne_date_deb + ' ' + campagne_heure_deb_jolie
  print ""


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def lectureKMLStations():

  # /kml/Document/Folder/name  = 'Betton'
  # /kml/Document/Folder/Placemark/name  =  '1 CR  Becherel'
  # /kml/Document/Folder/Placemark/Point/coordinates


##  <ns0:kml xmlns:ns0="http://www.opengis.net/kml/2.2">
##  <ns0:Document>
##    <ns0:name>Campagne Comptage Octobre 2017</ns0:name>
##    <ns0:description />
##    <ns0:Folder>
##      <ns0:name>Mordelles</ns0:name>
##      <ns0:Placemark>
##        <ns0:name>1 CR Mordelles
##</ns0:name>
##        <ns0:styleUrl>#icon-1899-4E342E-nodesc</ns0:styleUrl>
##        <ns0:Point>
##          <ns0:coordinates>
##            -1.8326381,48.0751041,0
##          </ns0:coordinates>
##        </ns0:Point>
##      </ns0:Placemark>


  # ------------------------------------------------
  # essai 3  pyKml

  print "pykml"

  root = parser.fromstring(open(kml_stations, 'r').read())

  #print root.Document.Folder.Placemark.Point.coordinates  #  renvoie    -1.6471728,48.1627498,0
  #print root.Document.Folder.Placemark[0].name  #  renvoie    1 CR Mesures de vitesse Betton
  #print root.Document.Folder.Placemark[1].name  #  renvoie    2 CR Mesures e Vitesse Betton

  iFolder = 0
  iPlacemark = 0

  # une première boucle sur les Folder
  for Folder in root.Document.Folder:
    print "Folder " + str(iFolder) + " : " +  root.Document.Folder[iFolder].name

    # 2e boucle sur les placemark
    # on cherche le nb de Placemark dans un Folder
    iPlacemark = len(Folder[iFolder].Placemark)

    # et on boucle
    for i in range(iPlacemark):
      print( i )

    return

    try:
      for Placemark in Folder:
        station_name = root.Document.Folder[iFolder].Placemark[iPlacemark].name
        station_name2 = str(station_name).replace('\n','')

        print "  Placemark " + str(iPlacemark) + " : " +  station_name2
        iPlacemark = iPlacemark + 1

    except NameError:
      print("La variable numerateur ou denominateur n'a pas été définie.")
    except TypeError:
      print("La variable numerateur ou denominateur possède un type incompatible avec la division.")
    except ZeroDivisionError:
      print("La variable denominateur est égale à 0.")
    else:
      print("Le résultat obtenu est", resultat)
    finally:
      iPlacemark = 0

    iFolder = iFolder + 1

  return

  # ------------------------------------------------
  # essai 1

  # le namespace du KML fourni
  ns = {'kml': 'http://www.opengis.net/kml/2.2'}

  tree = etree.parse(kml_stations)
  root = tree.getroot()
  #print (ET.tostring(root))

  document = root[0]


  #children = list(document)
  #for child in children:
  #  print(child.tag)

  # sans namespace
  #placemarks = root.findall('.//{http://www.opengis.net/kml/2.2}Folder')
  # avec namespace
  placemarks = root.findall('.//kml:Placemark', ns)

  print placemarks
  print placemarks[0].tag[0]

  for place in placemarks:
    place.findall('.//kml:name', ns)
    print place.tag  # on obtient {http://www.opengis.net/kml/2.2}Placemark


  return

  # ------------------------------------------------
  # essai 2

  xmlns="http://www.opengis.net/kml/2.2"

  result=tree.xpath('//Placemark/name/text()')

  for child in result:
    print child.tag

  #result = document.xpath('//Folder/Placemark/name/text()')

# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def lectureDonneesFIM():

  print u"Les données de comptage"

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
      print "   [" + str(i) + ' ' + str(i_data) + '] | jour ' + str(j_courant).zfill(2) + ' heure ' + str(h_courante).zfill(2) + ' | ' + date_tmst + ' | ' + intervalle + '  TV = '  + str(total_TV) + '  ( ' + str(total_VL) + ' VL + ' + str(total_PL) + ' PL )'

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

  global enquete_id

  try:
    # connexion à la base, si plante, on sort
    conn = psycopg2.connect(strConnDB)

    cursor = conn.cursor()


    # TODO
    # faire le code qui lit un fichier contenant les infos sur l'enquête à insérer
    #
    #
    #
    #

    # on vérifie si l'enquête existe déjà en base ou pas
    SQLVerif = u"""SELECT COUNT(*)
    FROM mobilite_transp.comptage_enquete
    WHERE
     comm_insee = '35022'
     AND site = 'Bécherel'
     AND date_deb::date = '2017-10-09';"""

    try:
      cursor.execute(SQLVerif)
      result = cursor.fetchone()
      enquete_test = result[0]
      #print str(enquete_test)

      # si diffèrent de 0 alors on insère pas
      if enquete_test > 0 :
        print u"L'enquête existe déjà !"

        # TODO
        # récupérer l'ID de cette enquête


        return 0
        pass
      else:
        # pas de doublon -> on peut insérer la nouvelle enquête
        print u"Pas d'enquête pré-existante dans la base avec ces infos."

        try:
            # on insert la nouvelle enquête

            fakeSQLEnquete = u"""INSERT INTO mobilite_transp.comptage_enquete
            VALUES (nextval('mobilite_transp.comptage_enquete_enquete_uid_seq'), '35022', 'campagne automne 2017', 'Bécherel',
            '2017-10-09 01:00:00', '2017-10-15 00:00:00', 'RM DMT SMU', 'Alyce', 'non', 'non', 'oui', 'oui');"""

            cursor.execute(fakeSQLEnquete)
            conn.commit()

            # et on récupère son identifiant
            SQL = "SELECT last_value FROM mobilite_transp.comptage_enquete_enquete_uid_seq ;"
            cursor.execute(SQL)

            result = cursor.fetchone()
            enquete_id = result[0]

            print u"Enquête n° " + str(enquete_id) +  u" créée"

            # on retourne cette valeur
            return enquete_id

        except:
            print u"Impossible d'exécuter la requête d'insertion d'une enquête"

    except:
      print u"Impossible d'exécuter la requête de contrôle de l'enquête"

  except:
      print "Impossible de se connecter à la base de données"


  cursor.close()
  conn.close()


# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

def main():

  print "++++++++ debut "

  #insertEnqueteInDB()


  #lectureMetadonneesFIM()

  lectureKMLStations()

  #lectureDonneesFIM()

  print "++++++++ fin "

  pass

if __name__ == '__main__':
  main()



# +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

# https://fastkml.readthedocs.io/en/latest/
