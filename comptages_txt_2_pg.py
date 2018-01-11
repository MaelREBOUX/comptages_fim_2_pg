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

station = ""


def lectureMetadonnees():

  # on lit la première ligne pour récupéer les métadonnées
  L_metadata = linecache.getline(f_to_import,1)
  # on splitte
  metadata = L_metadata.split('.')

  # on met en mémoire
  # code de la station de comptage
  station = metadata[2]
  sens = metadata[4].strip()
  date_deb = '20' + metadata[5].strip() +'-'+ metadata[6].strip() +'-'+ metadata[7].strip()
  heure_deb = metadata[8].strip() + ':' + metadata[9].strip() + ':00'

  print " Infos sur la station"
  print "   " + station + ' | ' + sens + ' | ' + date_deb + ' ' + heure_deb
  print ""


def lectureDonnees():

  f = open(f_to_import,'r')

  f_content = f.readlines()

  # on pointe les lignes qui ne sont pas des données
  metadata = [0, 1, 170, 171]

  i = 0
  i_intervalle = 0

  # on boucle sur les lignes
  for line in f_content:

    if not i in metadata:
      # print line[:-1]

      # on prend toute la ligne
      total = lectureLigneTV(line[:-1])

      print "   ligne " + str(i_intervalle) + ' TV = '  + str(total)

      # on peut incrémenter le compteur des valeurs de trafic
      i_intervalle = i_intervalle + 1

      if i == 4:
        break


    i = i + 1

  # fermeture du fichier
  f.close()



def lectureLigneTV(ligne):

  #print "   Donnees Tout Vehicule"

  i = 0
  total = 0

  # on splite sur le .
  hits = ligne.split('.')

  for hit in hits:
    # on dépadde les zéros  0003 -> 3
    value = hit.lstrip('0')

    # pour garder une valeur à 0
    if value == '': value = '0'
    #print str(i) + ' : ' + value

    # on additionne
    total = total + int(value)

    i = i + 1
  # fin de la boucle

  #print ' total ligne = ' + str(total)

  # on retourne le total
  return total


def main():

  print "++++++++ debut "

  lectureMetadonnees()

  lectureDonnees()

  print "++++++++ fin "

  pass

if __name__ == '__main__':
  main()




