#-------------------------------------------------------------------------------
# Name:        module1
# Purpose:
#
# Author:      m.reboux
#
# Created:     10/01/2018
# Copyright:   (c) m.reboux 2018
# Licence:     <your licence>
#-------------------------------------------------------------------------------


import linecache

# ATTENTION : fichier encodé en UCS-2 little endian // UTF-16
# passer le fichier en UTF-8 pour le lire

f_to_import = './fichiers_a_importer/test'

# variables globales
station_code = ""
station_sens = ""
campagne_date_deb = ""
campagne_heure_deb = ""



def lectureMetadonnees():

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


def lectureDonnees():

  print "Les donnees de comptage"

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
      intervalle = calculIntervalle(i_data)

      # on caclul le total TV pour la ligne en cours
      total_TV = lectureLigneTV(line[:-1])

      # pour les données PL on envoie le numéro de la ligne en cours
      total_PL = lectureLignePL(i)

      # on fait un calcul simple pour retrouver le nb de véhicules légers
      total_VL = total_TV - total_PL

      print "   [" + str(i) + ' ' + str(i_data) + '] | jour ' + str(j_courant) + ' h ' + str(h_courante) + ' | ' + date_tmst + ' | ' + intervalle + '  TV = '  + str(total_TV) + '  ( ' + str(total_VL) + ' VL + ' + str(total_PL) + ' PL )'
      # on peut incrémenter le compteur des valeurs de trafic
      i_data = i_data + 1



      # for debug : stop line
      if i == 80:
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



def main():

  print "++++++++ debut "

  lectureMetadonnees()

  lectureDonnees()

  print "++++++++ fin "

  pass

if __name__ == '__main__':
  main()




