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


def lectureDonnees():

  f = open(f_to_import,'r')

  f_content = f.readlines()

  # on supprime les lignes qui ne sont pas des données
  # Tout véhicules
  f_content.pop(0)
  f_content.pop(1)
  # Poids-lourds
  f_content(171)
  f_content(172)

  # on boucle sur les lignes
  for line in f_content:
    print line[:-1]

  # fermeture du fichier
  f.close()


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






def main():

  print "++++++++ debut "

  lectureMetadonnees()

  lectureDonnees()

  print "++++++++ fin "

  pass

if __name__ == '__main__':
  main()




