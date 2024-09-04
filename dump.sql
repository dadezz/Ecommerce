--
-- PostgreSQL database dump
--

-- Dumped from database version 16.3 (Debian 16.3-1.pgdg120+1)
-- Dumped by pg_dump version 16.3 (Debian 16.3-1.pgdg120+1)

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: public; Type: SCHEMA; Schema: -; Owner: postgres
--

-- *not* creating schema, since initdb creates it

--creo il ruolo utente da amministratore.
create role utente login password 'password';

REVOKE CREATE ON SCHEMA public FROM utente;
REVOKE ALL ON DATABASE "Ecommerce" FROM utente;

ALTER SCHEMA public OWNER TO postgres;

--
-- Name: elimina_carrelli_orfani(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.elimina_carrelli_orfani() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Controlla se ci sono ancora riferimenti in ProdottiCarrelli
    IF NOT EXISTS (
        SELECT 1
        FROM public."ProdottiCarrelli"
        WHERE id_carrello_entry = OLD.id_carrello_entry
    ) AND NOT EXISTS (
        -- Controlla se ci sono ancora riferimenti in CarrelloUtenti
        SELECT 1
        FROM public."CarrelloUtenti"
        WHERE id_carrello_entry = OLD.id_carrello_entry
    ) THEN
        -- Se non ci sono riferimenti, elimina l'entry corrispondente nella tabella Carrelli
        DELETE FROM public."Carrello"
        WHERE id_carrello_entry = OLD.id_carrello_entry;

        RAISE NOTICE 'Recensione con id % eliminata perché orfana.', OLD.id_carrello_entry;
    ELSE
        -- Visualizza un messaggio quando non ci sono recensioni orfane da eliminare
        RAISE NOTICE 'Nessuna recensione orfana trovata per id %.', OLD.id_carrello_entry;
    END IF;

    RETURN OLD;
END;
$$;


ALTER FUNCTION public.elimina_carrelli_orfani() OWNER TO postgres;

--
-- Name: elimina_recensioni_orfane(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.elimina_recensioni_orfane() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Controlla se ci sono ancora riferimenti a id_recensione_entry in Prodotti_recensioni
    -- Cancella dalla tabella intermedia le entry con gli id a NULL.
    DELETE FROM public."ProdottiRecensioni"
    WHERE id_prodotto IS NULL;

    DELETE FROM public."Recensioni"
    WHERE id_recensione_entry NOT IN (
        SELECT id_recensione_entry
        FROM public."ProdottiRecensioni"
    );
    RAISE NOTICE 'Recensioni eliminate per il prodotto';

    RETURN NULL;
END;
$$;


ALTER FUNCTION public.elimina_recensioni_orfane() OWNER TO postgres;

--
-- Name: elimina_recensioni_orfane_utenti(); Type: FUNCTION; Schema: public; Owner: postgres
--

CREATE FUNCTION public.elimina_recensioni_orfane_utenti() RETURNS trigger
    LANGUAGE plpgsql
    AS $$
BEGIN
    -- Controlla se ci sono ancora riferimenti a id_recensione_entry in Prodotti_recensioni
    -- Cancella dalla tabella intermedia le entry con gli id a NULL.
    DELETE FROM public."Recensioni"
    WHERE "Recensioni"."user" IS NULL;

    DELETE FROM public."ProdottiRecensioni"
    WHERE id_recensione_entry NOT IN (SELECT id_recensione_entry
                  FROM "Recensioni"
        );

    RAISE NOTICE 'Recensioni eliminate per il utente';

    RETURN NULL;
END;
$$;


ALTER FUNCTION public.elimina_recensioni_orfane_utenti() OWNER TO postgres;

--
-- Name: id_carrello_entry_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.id_carrello_entry_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.id_carrello_entry_seq OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: Carrello; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Carrello" (
    id_carrello_entry bigint DEFAULT nextval('public.id_carrello_entry_seq'::regclass) NOT NULL,
    qta bigint NOT NULL
);


ALTER TABLE public."Carrello" OWNER TO postgres;

--
-- Name: carutenti; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.carutenti
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.carutenti OWNER TO postgres;

--
-- Name: CarrelloUtenti; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."CarrelloUtenti" (
    id_carrello_entry bigint NOT NULL,
    "user" text NOT NULL,
    pk_carutenti integer DEFAULT nextval('public.carutenti'::regclass) NOT NULL
);


ALTER TABLE public."CarrelloUtenti" OWNER TO postgres;

--
-- Name: prodotti_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prodotti_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prodotti_id_seq OWNER TO postgres;

--
-- Name: Prodotti; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Prodotti" (
    id_prodotto bigint DEFAULT nextval('public.prodotti_id_seq'::regclass) NOT NULL,
    "Titolo" character varying(256) NOT NULL,
    "Descrizione" text NOT NULL,
    data_pubblicazione date NOT NULL,
    nuovo boolean DEFAULT true NOT NULL,
    "Prezzo" double precision DEFAULT 0.0 NOT NULL,
    visa boolean NOT NULL,
    autore character varying(256) NOT NULL,
    contanti boolean NOT NULL,
    baratto boolean NOT NULL,
    luogo text NOT NULL,
    disponibilita integer NOT NULL,
    spedizione boolean,
    tag text DEFAULT 'altro'::text NOT NULL
);


ALTER TABLE public."Prodotti" OWNER TO postgres;

--
-- Name: TABLE "Prodotti"; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public."Prodotti" IS 'Schema Prodotti';


--
-- Name: COLUMN "Prodotti".tag; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public."Prodotti".tag IS 'categoria';


--
-- Name: carprod; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.carprod
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.carprod OWNER TO postgres;

--
-- Name: ProdottiCarrelli; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."ProdottiCarrelli" (
    id_prodotto bigint NOT NULL,
    id_carrello_entry bigint NOT NULL,
    pk_prodotticarreli bigint DEFAULT nextval('public.carprod'::regclass) NOT NULL
);


ALTER TABLE public."ProdottiCarrelli" OWNER TO postgres;

--
-- Name: prodrec_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prodrec_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prodrec_seq OWNER TO postgres;

--
-- Name: ProdottiRecensioni; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."ProdottiRecensioni" (
    id_recensione_entry bigint,
    id_prodotto bigint,
    "PK_ProdottiRecensioni" bigint DEFAULT nextval('public.prodrec_seq'::regclass) NOT NULL
);


ALTER TABLE public."ProdottiRecensioni" OWNER TO postgres;

--
-- Name: TABLE "ProdottiRecensioni"; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public."ProdottiRecensioni" IS 'Tabella che assoccia ad un prodotto una recensione';


--
-- Name: prodotti_storici_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.prodotti_storici_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.prodotti_storici_seq OWNER TO postgres;

--
-- Name: ProdottiStorici; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."ProdottiStorici" (
    id_prodotto bigint,
    id_storico_entry bigint,
    "PK_ProdottiStorici" bigint DEFAULT nextval('public.prodotti_storici_seq'::regclass) NOT NULL
);


ALTER TABLE public."ProdottiStorici" OWNER TO postgres;

--
-- Name: recensioni_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.recensioni_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.recensioni_seq OWNER TO postgres;

--
-- Name: Recensioni; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Recensioni" (
    numero_stelle bigint DEFAULT 0 NOT NULL,
    titolo text,
    descrizione text,
    id_recensione_entry bigint DEFAULT nextval('public.recensioni_seq'::regclass) NOT NULL,
    "user" character varying(256)
);


ALTER TABLE public."Recensioni" OWNER TO postgres;

--
-- Name: TABLE "Recensioni"; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public."Recensioni" IS 'tabella Recensioni';


--
-- Name: Storico; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Storico" (
    "Data" date NOT NULL,
    "Nome" text NOT NULL,
    id_storico_entry bigint DEFAULT nextval('public.id_carrello_entry_seq'::regclass) NOT NULL,
    "user" text NOT NULL
);


ALTER TABLE public."Storico" OWNER TO postgres;

--
-- Name: TABLE "Storico"; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public."Storico" IS 'Tabella storici base';


--
-- Name: COLUMN "Storico"."user"; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON COLUMN public."Storico"."user" IS 'user';


--
-- Name: Utenti; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public."Utenti" (
    "user" character varying(256) NOT NULL,
    password bytea,
    contatto_mail character varying(256) NOT NULL,
    contatto_tel character varying(11),
    venditore boolean DEFAULT false
);


ALTER TABLE public."Utenti" OWNER TO postgres;

--
-- Name: TABLE "Utenti"; Type: COMMENT; Schema: public; Owner: postgres
--

COMMENT ON TABLE public."Utenti" IS 'Schema Utenti 
';


--
-- Name: id_storico_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.id_storico_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.id_storico_seq OWNER TO postgres;

--
-- Name: prodotti_disponibili; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.prodotti_disponibili AS
 SELECT id_prodotto,
    "Titolo",
    "Descrizione",
    data_pubblicazione,
    nuovo,
    "Prezzo",
    visa,
    autore,
    contanti,
    baratto,
    luogo,
    disponibilita,
    spedizione,
    tag
   FROM public."Prodotti"
  WHERE (disponibilita > 0);


ALTER VIEW public.prodotti_disponibili OWNER TO postgres;

--
-- Data for Name: Carrello; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Carrello" (id_carrello_entry, qta) FROM stdin;
\.


--
-- Data for Name: CarrelloUtenti; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."CarrelloUtenti" (id_carrello_entry, "user", pk_carutenti) FROM stdin;
\.


--
-- Data for Name: Prodotti; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Prodotti" (id_prodotto, "Titolo", "Descrizione", data_pubblicazione, nuovo, "Prezzo", visa, autore, contanti, baratto, luogo, disponibilita, spedizione, tag) FROM stdin;
1	Sedie - 5 foto	annuncio di prova con 5 foto	2024-09-04	f	21	t	username	f	f	Milano	6	f	altro
2	annuncio con recensioni	annuncio con tante recensioni, senza immagini	2024-09-04	f	1	f	username	t	f	Milano	789	f	altro
3	auto - 1 foto, disponibilità 0	annuncio di prova in categoria automobili, 1 foto, no recensioni, disponibilità 0 (non visibile in homepage ma solo in "i miei annunci"	2024-09-04	f	12864	f	username	f	t	Londra	0	t	motori
\.


--
-- Data for Name: ProdottiCarrelli; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."ProdottiCarrelli" (id_prodotto, id_carrello_entry, pk_prodotticarreli) FROM stdin;
\.


--
-- Data for Name: ProdottiRecensioni; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."ProdottiRecensioni" (id_recensione_entry, id_prodotto, "PK_ProdottiRecensioni") FROM stdin;
1	2	1
2	2	2
3	2	3
4	2	4
5	2	5
6	2	6
7	2	7
8	2	8
9	2	9
\.


--
-- Data for Name: ProdottiStorici; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."ProdottiStorici" (id_prodotto, id_storico_entry, "PK_ProdottiStorici") FROM stdin;
\.


--
-- Data for Name: Recensioni; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Recensioni" (numero_stelle, titolo, descrizione, id_recensione_entry, "user") FROM stdin;
5	molto bello	recensione 1	1	username
4	bello	recensione 2	2	username
1	molto brutto	recensione 3	3	username
3	medio	recensione 4	4	username
2	brutto	recensione 5	5	username
2	ancora brutto	recensione 6	6	username
5	ancora molto bello	recensione 7	7	username
5	ancora molto bello	recensione 8	8	username
5	ancora molto bello	recensione 9	9	username
\.


--
-- Data for Name: Storico; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Storico" ("Data", "Nome", id_storico_entry, "user") FROM stdin;
\.


--
-- Data for Name: Utenti; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public."Utenti" ("user", password, contatto_mail, contatto_tel, venditore) FROM stdin;
username	\\xf298e8ecac575a920bdded5a966a89617a04eec3a2c4245b3a437a7c91caaac21cf8bac48d87e48fb26549591f5095e7	email@email.com	\N	t
\.


--
-- Name: carprod; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.carprod', 1, false);


--
-- Name: carutenti; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.carutenti', 1, false);


--
-- Name: id_carrello_entry_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.id_carrello_entry_seq', 1, false);


--
-- Name: id_storico_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.id_storico_seq', 1, false);


--
-- Name: prodotti_id_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.prodotti_id_seq', 3, true);


--
-- Name: prodotti_storici_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.prodotti_storici_seq', 1, false);


--
-- Name: prodrec_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.prodrec_seq', 9, true);


--
-- Name: recensioni_seq; Type: SEQUENCE SET; Schema: public; Owner: postgres
--

SELECT pg_catalog.setval('public.recensioni_seq', 9, true);


--
-- Name: ProdottiCarrelli PK_ProdottiCarrelli; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ProdottiCarrelli"
    ADD CONSTRAINT "PK_ProdottiCarrelli" PRIMARY KEY (pk_prodotticarreli);


--
-- Name: ProdottiRecensioni PK_ProdottiRecensioni; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ProdottiRecensioni"
    ADD CONSTRAINT "PK_ProdottiRecensioni" PRIMARY KEY ("PK_ProdottiRecensioni");


--
-- Name: ProdottiStorici PK_ProdottiStorici; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ProdottiStorici"
    ADD CONSTRAINT "PK_ProdottiStorici" PRIMARY KEY ("PK_ProdottiStorici");


--
-- Name: CarrelloUtenti Pk_CarrelloUtenti; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."CarrelloUtenti"
    ADD CONSTRAINT "Pk_CarrelloUtenti" PRIMARY KEY (pk_carutenti);


--
-- Name: Prodotti Prodotti_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Prodotti"
    ADD CONSTRAINT "Prodotti_pkey" PRIMARY KEY (id_prodotto);


--
-- Name: Recensioni Recensioni_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Recensioni"
    ADD CONSTRAINT "Recensioni_pkey" PRIMARY KEY (id_recensione_entry);


--
-- Name: Carrello carrello_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Carrello"
    ADD CONSTRAINT carrello_pkey PRIMARY KEY (id_carrello_entry);


--
-- Name: Storico id_storico_entry; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Storico"
    ADD CONSTRAINT id_storico_entry PRIMARY KEY (id_storico_entry) INCLUDE (id_storico_entry);


--
-- Name: Utenti pk_user; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Utenti"
    ADD CONSTRAINT pk_user PRIMARY KEY ("user");


--
-- Name: Utenti delete_review_after_account; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER delete_review_after_account AFTER DELETE ON public."Utenti" FOR EACH ROW EXECUTE FUNCTION public.elimina_recensioni_orfane_utenti();


--
-- Name: Prodotti remove_review; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER remove_review AFTER DELETE ON public."Prodotti" FOR EACH ROW EXECUTE FUNCTION public.elimina_recensioni_orfane();


--
-- Name: CarrelloUtenti trigger_elimina_carrelli_da_utenti; Type: TRIGGER; Schema: public; Owner: postgres
--

CREATE TRIGGER trigger_elimina_carrelli_da_utenti AFTER DELETE ON public."CarrelloUtenti" FOR EACH ROW EXECUTE FUNCTION public.elimina_carrelli_orfani();


--
-- Name: Prodotti autore_fk; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Prodotti"
    ADD CONSTRAINT autore_fk FOREIGN KEY (autore) REFERENCES public."Utenti"("user") ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: CarrelloUtenti carrelloutenti__user_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."CarrelloUtenti"
    ADD CONSTRAINT carrelloutenti__user_fkey FOREIGN KEY ("user") REFERENCES public."Utenti"("user") ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: CarrelloUtenti carrelloutenti_id_carrello_entry_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."CarrelloUtenti"
    ADD CONSTRAINT carrelloutenti_id_carrello_entry_fkey FOREIGN KEY (id_carrello_entry) REFERENCES public."Carrello"(id_carrello_entry) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: ProdottiStorici id_prodotto; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ProdottiStorici"
    ADD CONSTRAINT id_prodotto FOREIGN KEY (id_prodotto) REFERENCES public."Prodotti"(id_prodotto) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: ProdottiRecensioni id_prodotto; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ProdottiRecensioni"
    ADD CONSTRAINT id_prodotto FOREIGN KEY (id_prodotto) REFERENCES public."Prodotti"(id_prodotto) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: ProdottiRecensioni id_recensioni_entry; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ProdottiRecensioni"
    ADD CONSTRAINT id_recensioni_entry FOREIGN KEY (id_recensione_entry) REFERENCES public."Recensioni"(id_recensione_entry) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: ProdottiStorici id_storico_entry; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ProdottiStorici"
    ADD CONSTRAINT id_storico_entry FOREIGN KEY (id_storico_entry) REFERENCES public."Storico"(id_storico_entry) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: Storico pk_user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Storico"
    ADD CONSTRAINT pk_user FOREIGN KEY ("user") REFERENCES public."Utenti"("user") ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: ProdottiCarrelli prodotticarrelli_id_carrello_entry_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ProdottiCarrelli"
    ADD CONSTRAINT prodotticarrelli_id_carrello_entry_fkey FOREIGN KEY (id_carrello_entry) REFERENCES public."Carrello"(id_carrello_entry) ON DELETE CASCADE;


--
-- Name: ProdottiCarrelli prodotticarrelli_id_prodotto_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."ProdottiCarrelli"
    ADD CONSTRAINT prodotticarrelli_id_prodotto_fkey FOREIGN KEY (id_prodotto) REFERENCES public."Prodotti"(id_prodotto) ON UPDATE CASCADE ON DELETE CASCADE;


--
-- Name: Recensioni user; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public."Recensioni"
    ADD CONSTRAINT "user" FOREIGN KEY ("user") REFERENCES public."Utenti"("user") ON UPDATE SET NULL ON DELETE SET NULL;


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: postgres
--

GRANT USAGE ON SCHEMA public TO utente;


--
-- Name: FUNCTION elimina_carrelli_orfani(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.elimina_carrelli_orfani() TO utente WITH GRANT OPTION;


--
-- Name: FUNCTION elimina_recensioni_orfane(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.elimina_recensioni_orfane() TO utente WITH GRANT OPTION;


--
-- Name: FUNCTION elimina_recensioni_orfane_utenti(); Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON FUNCTION public.elimina_recensioni_orfane_utenti() TO utente WITH GRANT OPTION;


--
-- Name: SEQUENCE id_carrello_entry_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.id_carrello_entry_seq TO utente WITH GRANT OPTION;


--
-- Name: TABLE "Carrello"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."Carrello" TO utente WITH GRANT OPTION;


--
-- Name: SEQUENCE carutenti; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.carutenti TO utente WITH GRANT OPTION;


--
-- Name: TABLE "CarrelloUtenti"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."CarrelloUtenti" TO utente WITH GRANT OPTION;


--
-- Name: SEQUENCE prodotti_id_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.prodotti_id_seq TO utente WITH GRANT OPTION;


--
-- Name: TABLE "Prodotti"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."Prodotti" TO utente WITH GRANT OPTION;


--
-- Name: SEQUENCE carprod; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.carprod TO utente WITH GRANT OPTION;


--
-- Name: TABLE "ProdottiCarrelli"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."ProdottiCarrelli" TO utente WITH GRANT OPTION;


--
-- Name: SEQUENCE prodrec_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.prodrec_seq TO utente WITH GRANT OPTION;


--
-- Name: TABLE "ProdottiRecensioni"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."ProdottiRecensioni" TO utente WITH GRANT OPTION;


--
-- Name: SEQUENCE prodotti_storici_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.prodotti_storici_seq TO utente WITH GRANT OPTION;


--
-- Name: TABLE "ProdottiStorici"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."ProdottiStorici" TO utente WITH GRANT OPTION;


--
-- Name: SEQUENCE recensioni_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.recensioni_seq TO utente WITH GRANT OPTION;


--
-- Name: TABLE "Recensioni"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."Recensioni" TO utente WITH GRANT OPTION;


--
-- Name: TABLE "Storico"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."Storico" TO utente WITH GRANT OPTION;


--
-- Name: TABLE "Utenti"; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public."Utenti" TO utente WITH GRANT OPTION;


--
-- Name: SEQUENCE id_storico_seq; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON SEQUENCE public.id_storico_seq TO utente WITH GRANT OPTION;


--
-- Name: TABLE prodotti_disponibili; Type: ACL; Schema: public; Owner: postgres
--

GRANT ALL ON TABLE public.prodotti_disponibili TO utente WITH GRANT OPTION;


--
-- PostgreSQL database dump complete
--

