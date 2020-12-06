
/* CREATE DATABASE */
CREATE DATABASE school WITH OWNER = admin ENCODING = 'UTF8' LC_CTYPE = 'ru_RU.utf8' LC_COLLATE = 'ru_RU.utf8' TABLESPACE = pg_default  CONNECTION LIMIT = -1 TEMPLATE template0;

\c school

/* CREATE ALL TABLES (TABLE live LAST because it depands on all others) */

CREATE TABLE public.clients
(
    id  SERIAL NOT NULL ,
    fio character varying(100)  NOT NULL,
    tel character varying(12) NOT NULL,
    job character varying(50) NOT NULL,
    homeadress character varying(50)  NOT NULL,
    salary numeric(9,2) NOT NULL,
    call_back boolean NOT NULL,
    CONSTRAINT clients_pkey PRIMARY KEY (id)
);

CREATE TABLE public.statuses
(
    id SERIAL NOT NULL,
    status character varying(20) COLLATE pg_catalog."default" NOT NULL,
    CONSTRAINT statuses_pkey PRIMARY KEY (id),
    CONSTRAINT statuses_status_key UNIQUE (status)
);

CREATE TABLE public.services
(
    id SERIAL NOT NULL,
    service character varying(20) COLLATE pg_catalog."default" NOT NULL,
    service_description text COLLATE pg_catalog."default",
    CONSTRAINT services_pkey PRIMARY KEY (id),
    CONSTRAINT services_service_key UNIQUE (service)
);

CREATE TABLE public.live
(
    client_id integer NOT NULL,
    service_id integer NOT NULL,
    status_id integer NOT NULL,
    CONSTRAINT live_client_id_service_id_status_id_key UNIQUE (client_id, service_id),
    CONSTRAINT fk_client FOREIGN KEY (client_id)
        REFERENCES public.clients (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT fk_service FOREIGN KEY (service_id)
        REFERENCES public.services (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE,
    CONSTRAINT fk_status FOREIGN KEY (status_id)
        REFERENCES public.statuses (id) MATCH SIMPLE
        ON UPDATE NO ACTION
        ON DELETE CASCADE
);

/* CREATE ALL INDEPENDANT FUNCTIONS EXCEPT THOSE FOR USER CREATION*/

/* INSERT CLIENT */
CREATE OR REPLACE PROCEDURE insert_client(fio_p VARCHAR(100), tel_p VARCHAR(12), job_p VARCHAR(50), homeadress_p VARCHAR(50), salary_p numeric(9,2))
LANGUAGE plpgsql
AS $$
BEGIN
INSERT INTO clients (fio, tel, job, homeadress, salary, call_back) VALUES (fio_p, tel_p, job_p, homeadress_p, salary_p, true);
END;
$$;


/*UPDATE CLIENT*/
CREATE OR REPLACE PROCEDURE update_client(client_id_p INTEGER,fio_p VARCHAR(100) DEFAULT NULL ,tel_p VARCHAR(12) DEFAULT NULL, job_p VARCHAR(50) DEFAULT NULL, homeadress_p VARCHAR(50) DEFAULT NULL, salary_p numeric(9,2) DEFAULT NULL, call_back_p BOOLEAN DEFAULT NULL)
LANGUAGE plpgsql
AS $$
BEGIN
CASE
WHEN fio_p IS NOT NULL
THEN
UPDATE clients SET fio = fio_p WHERE id = client_id_p;
ELSE
END CASE;
CASE
WHEN tel_p IS NOT NULL
THEN
UPDATE clients SET tel = tel_p WHERE id = client_id_p;
ELSE
END CASE;
CASE
WHEN job_p IS NOT NULL
THEN
UPDATE clients SET job = job_p WHERE id = client_id_p;
ELSE
END CASE;
CASE
WHEN homeadress_p IS NOT NULL
THEN
UPDATE clients SET homeadress = homeadress_p WHERE id = client_id_p;
ELSE
END CASE;
CASE
WHEN salary_p IS NOT NULL 
THEN
UPDATE clients SET salary = salary_p WHERE id = client_id_p;
ELSE
END CASE;
CASE
WHEN call_back_p IS NOT NULL 
THEN
UPDATE clients SET call_back = call_back_p WHERE id = client_id_p;
ELSE
END CASE;
END;
$$;


/* DELETE CLIENT */
CREATE OR REPLACE PROCEDURE delete_client(client_id_p INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
DELETE FROM clients WHERE id = client_id_p;
END;
$$;

/* INSERT SERVICES */
CREATE OR REPLACE FUNCTION insert_service(service_p VARCHAR(20), service_description_p TEXT)
RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
INSERT INTO services (service, service_description) VALUES (service_p, service_description_p);
RETURN TRUE;
EXCEPTION WHEN OTHERS THEN
RETURN FALSE;
END;
$$;

/*DELETE SERVICES*/
CREATE OR REPLACE PROCEDURE delete_service(service_id_p INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
DELETE FROM services WHERE id = service_id_p;
END;
$$;

/*UPDATE LIVE*/
CREATE OR REPLACE PROCEDURE update_live_status(client_id_p INTEGER, service_id_p INTEGER, status_id_p INTEGER)
LANGUAGE plpgsql
AS $$
BEGIN
UPDATE live SET status_id = status_id_p WHERE client_id = client_id_p AND service_id = service_id_p;
END;
$$;

/*ADMINISTRATOR VIEW FOR CLIENTS*/

CREATE OR REPLACE VIEW administrator_client_view AS
SELECT * FROM clients ORDER BY id;


/*LIST ALL NON SUPERUSERS*/

CREATE OR REPLACE VIEW administrator_user_view AS
SELECT usename FROM pg_catalog.pg_user WHERE usesuper = false ORDER BY usename desc;

/*LIST ALL SERVICES*/

CREATE OR REPLACE VIEW administrator_service_view AS
SELECT * FROM services ORDER BY id;



/* CREATE ALL TRIGGERS EXCEPT INSERT SERVICES*/

/*ON INSERT CLIENTS*/
CREATE OR REPLACE FUNCTION on_insert_clients()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE
    id_ INTEGER;
BEGIN
FOR id_ IN (SELECT id FROM services) LOOP
INSERT INTO live VALUES(NEW.id, id_, (SELECT id FROM statuses WHERE status LIKE 'call back'));
END LOOP;
RETURN NEW;
END;
$$;

CREATE TRIGGER on_insert_clients_trigger AFTER INSERT ON clients FOR EACH ROW EXECUTE PROCEDURE on_insert_clients();

/*UTILITY FUNCTION*/

CREATE OR REPLACE FUNCTION get_id_for_update(client_name VARCHAR(100), client_number VARCHAR(12), service_name VARCHAR(50), status_name VARCHAR(20))
RETURNS TABLE (
    client_id INTEGER,
    service_id INTEGER,
    status_id INTEGER
)
LANGUAGE plpgsql
AS $$
DECLARE
    client INTEGER;
    service INTEGER;
    status INTEGER;
BEGIN
SELECT INTO client clients.id FROM clients WHERE clients.fio LIKE client_name AND clients.tel LIKE client_number;
SELECT INTO service services.id FROM services WHERE services.service LIKE service_name;
SELECT INTO status statuses.id FROM statuses WHERE statuses.status LIKE status_name;
RETURN QUERY SELECT client, service, status;
END;
$$;



/*ON UPDATE LIVE*/
CREATE OR REPLACE FUNCTION on_update_status_live()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
BEGIN
RAISE NOTICE 'FUNCTION IS CALLED AND THE AMOUT IS %',
(SELECT count(client_id) FROM live WHERE client_id = NEW.client_id AND status_id = (SELECT id FROM statuses WHERE status LIKE 'call back'));
CASE 
(SELECT count(client_id) FROM live WHERE client_id = NEW.client_id AND status_id = (SELECT id FROM statuses WHERE status LIKE 'call back'))
WHEN 0 THEN
UPDATE clients SET call_back = false WHERE id = NEW.client_id;
RETURN NEW;
ELSE
UPDATE clients SET call_back = true WHERE id = NEW.client_id;
RETURN NEW;
END CASE;
END;
$$;


CREATE TRIGGER on_update_status_live_trigger AFTER UPDATE OF status_id ON live FOR EACH ROW EXECUTE FUNCTION on_update_status_live();


/*CREATE TRIGGER ON SERVICE INSERTATION*/
CREATE  OR REPLACE FUNCTION on_insert_services()
RETURNS TRIGGER
LANGUAGE plpgsql
AS $$
DECLARE 
local_id INTEGER;
BEGIN
FOR local_id IN (SELECT id FROM clients) LOOP
INSERT INTO live VALUES(local_id, NEW.id, 2);
END LOOP;
UPDATE clients SET call_back = true;
RETURN NEW;
END;
$$;

CREATE TRIGGER on_insert_services_trigger AFTER INSERT ON services FOR EACH ROW EXECUTE FUNCTION on_insert_services();

/*CREATE FUNCTION FOR CHECKING SUPER*/
CREATE OR REPLACE FUNCTION is_super() RETURNS BOOLEAN
LANGUAGE plpgsql
AS $$
BEGIN
RETURN (SELECT usesuper FROM pg_user WHERE usename = CURRENT_USER);
END;
$$;


/*CREATE VIEW FOR MANAGERS*/
CREATE OR REPLACE FUNCTION managers_view_function()
RETURNS TABLE (
    fio_p VARCHAR(100),
    tel_p VARCHAR(12),
    homeadress_p VARCHAR(100),
    salary_p NUMERIC(9,2)
)
LANGUAGE plpgsql
AS $$
BEGIN
RETURN QUERY SELECT fio, tel, homeadress, salary FROM clients WHERE call_back = true ORDER BY id;
END;
$$;


CREATE OR REPLACE VIEW managers_view AS
SELECT * FROM managers_view_function();

CREATE OR REPLACE VIEW managers_live_view AS
SELECT status FROM statuses INNER JOIN live ON id = status_id and client_id NOT IN (SELECT id FROM clients WHERE call_back = false) ORDER BY client_id, service_id;

/*CREATE PROCEDURES FOR USER CREATION*/

/*CREATE GROUP*/
CREATE OR REPLACE PROCEDURE add_group(group_name VARCHAR(50))
LANGUAGE plpgsql
AS $$
BEGIN
execute 'CREATE ROLE ' ||group_name;
execute 'GRANT SELECT, UPDATE ON live, clients TO ' ||group_name;
execute 'GRANT DELETE ON live TO ' ||group_name;
execute 'GRANT SELECT ON statuses, services TO ' ||group_name;
execute 'GRANT SELECT ON managers_view, managers_live_view TO ' ||group_name;
END;
$$;

/*CREATE USER*/
CREATE OR REPLACE PROCEDURE add_user(username VARCHAR(50), password VARCHAR(50))
LANGUAGE plpgsql
AS $$
BEGIN
execute  'CREATE ROLE ' ||username|| ' WITH LOGIN PASSWORD ''' ||password|| ''' IN GROUP managers';
END;
$$;

/*DELET USER*/
CREATE OR REPLACE PROCEDURE delete_user(role_name VARCHAR(100))
LANGUAGE plpgsql
AS $$
BEGIN
EXECUTE format('DROP ROLE %I', role_name);
END;
$$;

/* BULK INSERT DUMMY DATA FROM FILES  (CLIENTS LAST)*/

/* BULK INSERT STATUSES*/
\copy statuses (status) FROM '/dummy-data/statuses.csv' WITH CSV DELIMITER ',' ENCODING 'UTF-8';

/*BULK INSERT SERVICES*/
\copy services (service, service_description) FROM '/dummy-data/services.csv' WITH CSV DELIMITER ',' ENCODING 'UTF-8';

/*BULK INSERT CLIENTS*/
\copy clients (fio,tel,job,homeadress,salary,call_back) FROM '/dummy-data/clients.csv' WITH CSV DELIMITER ',' HEADER ENCODING 'UTF8';


/*CREATE 'MANAGERS' GROUP*/ 
call add_group('managers');

/*CREATE ONE USER*/
call add_user('vlado','vlado');

call add_user('pero','pero');
