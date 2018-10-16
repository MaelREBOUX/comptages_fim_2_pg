# Lecture et chargement de fichiers de données de trafic routier dans une base PostgreSQL / PostGIS

Script permettant de lire des fichiers de comptages routiers au format FIM et de les charger vers une base PostgreSQL.

Seules les informations sur le nombre de véhicules par tranche horaires sont lues. les informations de vitesse ne sont pas prises en compte.


Scénario classique :
1. insérer une enquête ->  ```comptages_txt_2_pg.py -enquete```
2. insérer les données de comptage ->  ```comptages_txt_2_pg.py -donnees_fim x```  où x = id d'enquête

Il faut compléter le fichier `_enquete_a_creer.csv` pour créer des enquêtes et placer les fichier à importer dans le même répertoire.

La strucutre des tables est dans le fichier `comptage_routier.sql `

