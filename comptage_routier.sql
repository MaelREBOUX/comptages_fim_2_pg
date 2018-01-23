
-- 23/01/2018 Maël REBOUX
-- SIG Rennes Métropole


-- DROP TABLE mobilite_transp.comptage_enquete ;
CREATE TABLE mobilite_transp.comptage_enquete
(
  enquete_id serial NOT NULL,
  comm_insee varchar(5) NOT NULL,
  description text NOT NULL,
  site text,
  date_deb timestamp without time zone,
  date_fin timestamp without time zone,
  moa text, -- maîtrise d'ouvrage
  moe text, -- maîtrise d'œuvre
  d_occupation varchar(3),
  d_rotation varchar(3),
  d_routier varchar(3),
  d_vitesse varchar(3),
  -- pk
  CONSTRAINT mobilite_transp_comptage_enquete_pkey PRIMARY KEY (enquete_id)
)
WITH (
  OIDS=FALSE
);

-- indexes



-- DROP TABLE mobilite_transp.comptage_station ;
CREATE TABLE mobilite_transp.comptage_station
(
  station_id serial NOT NULL,
  comm_insee varchar(5) NOT NULL,
  materiel text,
  type integer,
  sens integer,
  description text,
  date_mes timestamp without time zone,
  date_mhs timestamp without time zone,
  x real,
  y real,
  long real,
  lat real,
  angle_symbole integer,
  -- géométrie
  shape geometry,
  CONSTRAINT enforce_geotype_shape CHECK (geometrytype(shape) = 'POINT'::text),
  CONSTRAINT enforce_srid_shape CHECK (st_srid(shape) = 3948),
  -- pk
  CONSTRAINT mobilite_transp_comptage_station_pkey PRIMARY KEY (station_id)
)
WITH (
  OIDS=FALSE
);

-- indexes



-- DROP TABLE mobilite_transp.comptage_automatique ;
CREATE TABLE mobilite_transp.comptage_automatique
(
  enquete_id integer, -- NOT NULL,
  station_id integer NOT NULL,
  date_tmst timestamp without time zone, -- 2016-10-11 00:00:00
  date_str varchar(10),  -- 11/10/2016
  heure_deb integer,
  heure_fin integer,
  heure_intervalle varchar(12),
  nb_total integer,
  nb_vl integer,
  nb_pl integer,
  nb_tc integer,
  nb_2rm integer,
  nb_2r integer,
  nb_pieton integer,
  -- pk
  CONSTRAINT mobilite_transp_comptage_automatique_pkey PRIMARY KEY (enquete_id, station_id, date_tmst, heure_deb)
)
WITH (
  OIDS=FALSE
);

-- indexes



-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
-- les tables de domaines

-- DROP TABLE mobilite_transp.comptage_dom_station_sens ;
CREATE TABLE mobilite_transp.comptage_dom_station_sens
(
  sens_id integer,
  sens_libelle varchar(15)
)
WITH (
  OIDS=FALSE
);
GRANT SELECT ON TABLE mobilite_transp.comptage_dom_station_sens TO consult;

INSERT INTO mobilite_transp.comptage_dom_station_sens VALUES (1,'dans le sens 1');
INSERT INTO mobilite_transp.comptage_dom_station_sens VALUES (1,'dans le sens 2');
INSERT INTO mobilite_transp.comptage_dom_station_sens VALUES (3,'dans les 2sens');

-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

-- DROP TABLE mobilite_transp.comptage_dom_station_type
CREATE TABLE mobilite_transp.comptage_dom_station_type
(
  type_id integer,
  type_libelle varchar(25)
)
WITH (
  OIDS=FALSE
);
GRANT SELECT ON TABLE mobilite_transp.comptage_dom_station_type TO consult;

INSERT INTO mobilite_transp.comptage_dom_station_type VALUES (1,'PL + VL');
INSERT INTO mobilite_transp.comptage_dom_station_type VALUES (2,'vélo sur aménagement');
INSERT INTO mobilite_transp.comptage_dom_station_type VALUES (3,'vélo hors aménagement');
INSERT INTO mobilite_transp.comptage_dom_station_type VALUES (4,'piéton sur passage');
INSERT INTO mobilite_transp.comptage_dom_station_type VALUES (5,'piéton hors passage');

-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++



-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
-- les vues

-- DROP VIEW mobilite_transp.v_comptage_station_automatique ;
CREATE VIEW mobilite_transp.v_comptage_station_automatique AS
  SELECT
    row_number() over() as uid,
    b.station_id,
    b.comm_insee,
    b.type,
    b.sens,
    b.description,
    a.date_tmst,
    a.date_str,
    a.heure_intervalle,
    a.heure_deb,
    a.heure_fin,
    a.nb_total,
    a.nb_vl,
    a.nb_pl,
    a.nb_tc,
    a.nb_2rm,
    a.nb_2r,
    a.nb_pieton,
    b.shape::geometry(Point,3948) AS shape
  FROM mobilite_transp.comptage_automatique a
    LEFT JOIN mobilite_transp.comptage_station b ON a.station_id = b.station_id ;


-- ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
-- les permissions

-- les droits pour le compte geocarto en écriture
GRANT USAGE ON SCHEMA mobilite_transp TO geocarto ;
GRANT ALL ON SEQUENCE mobilite_transp.comptage_enquete_enquete_id_seq TO geocarto;
GRANT ALL ON SEQUENCE mobilite_transp.comptage_station_station_id_seq TO geocarto;
GRANT ALL ON TABLE mobilite_transp.comptage_automatique TO geocarto;
GRANT ALL ON TABLE mobilite_transp.comptage_dom_station_sens TO geocarto;
GRANT ALL ON TABLE mobilite_transp.comptage_dom_station_type TO geocarto;
GRANT ALL ON TABLE mobilite_transp.comptage_enquete TO geocarto;
GRANT ALL ON TABLE mobilite_transp.comptage_station TO geocarto;
GRANT ALL ON TABLE mobilite_transp.v_comptage_station_automatique TO geocarto;

-- les droits en lecture pour consult
GRANT USAGE ON SCHEMA mobilite_transp TO consult ;
GRANT SELECT ON SEQUENCE mobilite_transp.comptage_enquete_enquete_id_seq TO consult;
GRANT SELECT ON SEQUENCE mobilite_transp.comptage_station_station_id_seq TO consult;
GRANT SELECT ON TABLE mobilite_transp.comptage_automatique TO consult;
GRANT SELECT ON TABLE mobilite_transp.comptage_dom_station_sens TO consult;
GRANT SELECT ON TABLE mobilite_transp.comptage_dom_station_type TO consult;
GRANT SELECT ON TABLE mobilite_transp.comptage_enquete TO consult;
GRANT SELECT ON TABLE mobilite_transp.comptage_station TO consult;
GRANT SELECT ON TABLE mobilite_transp.v_comptage_station_automatique TO consult;

