--
-- PostgreSQL database dump
--

-- Dumped from database version 16.0
-- Dumped by pg_dump version 16.0

-- Started on 2023-12-04 23:01:43 EST

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

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- TOC entry 218 (class 1259 OID 17339)
-- Name: attempt; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.attempt (
    song_id bigint NOT NULL,
    lyric_check boolean DEFAULT false NOT NULL,
    tab_check boolean DEFAULT false NOT NULL,
    mp3_check boolean DEFAULT false NOT NULL,
    karaoke_check boolean DEFAULT false NOT NULL
);


ALTER TABLE public.attempt OWNER TO postgres;

--
-- TOC entry 226 (class 1259 OID 17425)
-- Name: party; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.party (
    party_id integer NOT NULL,
    name character varying(255),
    description text
);


ALTER TABLE public.party OWNER TO postgres;

--
-- TOC entry 225 (class 1259 OID 17424)
-- Name: party_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.party_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.party_id_seq OWNER TO postgres;

--
-- TOC entry 3678 (class 0 OID 0)
-- Dependencies: 225
-- Name: party_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.party_id_seq OWNED BY public.party.party_id;


--
-- TOC entry 228 (class 1259 OID 17483)
-- Name: party_song; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.party_song (
    party_id integer NOT NULL,
    song_id integer NOT NULL
);


ALTER TABLE public.party_song OWNER TO postgres;

--
-- TOC entry 227 (class 1259 OID 17468)
-- Name: party_user; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.party_user (
    party_id integer NOT NULL,
    user_id integer NOT NULL,
    accept boolean DEFAULT false,
    administrator boolean DEFAULT false
);


ALTER TABLE public.party_user OWNER TO postgres;

--
-- TOC entry 220 (class 1259 OID 17349)
-- Name: searches; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.searches (
    search_id bigint NOT NULL,
    search_term character varying(50) NOT NULL
);


ALTER TABLE public.searches OWNER TO postgres;

--
-- TOC entry 219 (class 1259 OID 17348)
-- Name: search_search_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.search_search_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.search_search_id_seq OWNER TO postgres;

--
-- TOC entry 3679 (class 0 OID 0)
-- Dependencies: 219
-- Name: search_search_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.search_search_id_seq OWNED BY public.searches.search_id;


--
-- TOC entry 222 (class 1259 OID 17356)
-- Name: song; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.song (
    song_id bigint NOT NULL,
    title character varying(255) NOT NULL,
    artist character varying(255)
);


ALTER TABLE public.song OWNER TO postgres;

--
-- TOC entry 215 (class 1259 OID 17325)
-- Name: song_search; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.song_search (
    song_id bigint NOT NULL,
    search_id bigint NOT NULL
);


ALTER TABLE public.song_search OWNER TO postgres;

--
-- TOC entry 221 (class 1259 OID 17355)
-- Name: song_song_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.song_song_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.song_song_id_seq OWNER TO postgres;

--
-- TOC entry 3680 (class 0 OID 0)
-- Dependencies: 221
-- Name: song_song_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.song_song_id_seq OWNED BY public.song.song_id;


--
-- TOC entry 224 (class 1259 OID 17369)
-- Name: url; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.url (
    song_id bigint NOT NULL,
    lyric_url character varying(255),
    tab_url character varying(255),
    mp3_url character varying(255),
    karaoke_url character varying(255),
    img_url text
);


ALTER TABLE public.url OWNER TO postgres;

--
-- TOC entry 223 (class 1259 OID 17364)
-- Name: user_song; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.user_song (
    user_id integer NOT NULL,
    song_id integer NOT NULL,
    favorite boolean DEFAULT false
);


ALTER TABLE public.user_song OWNER TO postgres;

--
-- TOC entry 217 (class 1259 OID 17331)
-- Name: users; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.users (
    user_id bigint NOT NULL,
    first_name character varying(200) NOT NULL,
    last_name character varying(200) NOT NULL,
    email character varying(255) NOT NULL,
    password character varying(255) NOT NULL,
    username character varying(255),
    site_admin boolean DEFAULT false
);


ALTER TABLE public.users OWNER TO postgres;

--
-- TOC entry 216 (class 1259 OID 17330)
-- Name: user_user_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.user_user_id_seq
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.user_user_id_seq OWNER TO postgres;

--
-- TOC entry 3681 (class 0 OID 0)
-- Dependencies: 216
-- Name: user_user_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.user_user_id_seq OWNED BY public.users.user_id;


--
-- TOC entry 3491 (class 2604 OID 17428)
-- Name: party party_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.party ALTER COLUMN party_id SET DEFAULT nextval('public.party_id_seq'::regclass);


--
-- TOC entry 3488 (class 2604 OID 17352)
-- Name: searches search_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.searches ALTER COLUMN search_id SET DEFAULT nextval('public.search_search_id_seq'::regclass);


--
-- TOC entry 3489 (class 2604 OID 17359)
-- Name: song song_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.song ALTER COLUMN song_id SET DEFAULT nextval('public.song_song_id_seq'::regclass);


--
-- TOC entry 3482 (class 2604 OID 17334)
-- Name: users user_id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users ALTER COLUMN user_id SET DEFAULT nextval('public.user_user_id_seq'::regclass);


--
-- TOC entry 3503 (class 2606 OID 17347)
-- Name: attempt check_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attempt
    ADD CONSTRAINT check_pkey PRIMARY KEY (song_id);


--
-- TOC entry 3515 (class 2606 OID 17432)
-- Name: party party_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.party
    ADD CONSTRAINT party_pkey PRIMARY KEY (party_id);


--
-- TOC entry 3519 (class 2606 OID 17487)
-- Name: party_song party_song_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.party_song
    ADD CONSTRAINT party_song_pkey PRIMARY KEY (party_id, song_id);


--
-- TOC entry 3517 (class 2606 OID 17472)
-- Name: party_user party_user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.party_user
    ADD CONSTRAINT party_user_pkey PRIMARY KEY (user_id, party_id);


--
-- TOC entry 3505 (class 2606 OID 17354)
-- Name: searches search_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.searches
    ADD CONSTRAINT search_pkey PRIMARY KEY (search_id);


--
-- TOC entry 3507 (class 2606 OID 17361)
-- Name: song song_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.song
    ADD CONSTRAINT song_pkey PRIMARY KEY (song_id);


--
-- TOC entry 3495 (class 2606 OID 17329)
-- Name: song_search song_search_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.song_search
    ADD CONSTRAINT song_search_pkey PRIMARY KEY (song_id, search_id);


--
-- TOC entry 3509 (class 2606 OID 17414)
-- Name: song song_title_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.song
    ADD CONSTRAINT song_title_unique UNIQUE (title);


--
-- TOC entry 3497 (class 2606 OID 17422)
-- Name: users unique_username; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT unique_username UNIQUE (username);


--
-- TOC entry 3513 (class 2606 OID 17375)
-- Name: url url_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.url
    ADD CONSTRAINT url_pkey PRIMARY KEY (song_id);


--
-- TOC entry 3499 (class 2606 OID 17420)
-- Name: users user_email_unique; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT user_email_unique UNIQUE (email);


--
-- TOC entry 3501 (class 2606 OID 17336)
-- Name: users user_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.users
    ADD CONSTRAINT user_pkey PRIMARY KEY (user_id);


--
-- TOC entry 3511 (class 2606 OID 17368)
-- Name: user_song user_song_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_song
    ADD CONSTRAINT user_song_pkey PRIMARY KEY (user_id, song_id);


--
-- TOC entry 3522 (class 2606 OID 17386)
-- Name: attempt check_song_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.attempt
    ADD CONSTRAINT check_song_id_foreign FOREIGN KEY (song_id) REFERENCES public.song(song_id);


--
-- TOC entry 3528 (class 2606 OID 17488)
-- Name: party_song party_song_party_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.party_song
    ADD CONSTRAINT party_song_party_id_fkey FOREIGN KEY (party_id) REFERENCES public.party(party_id);


--
-- TOC entry 3529 (class 2606 OID 17493)
-- Name: party_song party_song_song_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.party_song
    ADD CONSTRAINT party_song_song_id_fkey FOREIGN KEY (song_id) REFERENCES public.song(song_id);


--
-- TOC entry 3526 (class 2606 OID 17473)
-- Name: party_user party_user_party_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.party_user
    ADD CONSTRAINT party_user_party_id_fkey FOREIGN KEY (party_id) REFERENCES public.party(party_id);


--
-- TOC entry 3527 (class 2606 OID 17478)
-- Name: party_user party_user_user_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.party_user
    ADD CONSTRAINT party_user_user_id_fkey FOREIGN KEY (user_id) REFERENCES public.users(user_id);


--
-- TOC entry 3520 (class 2606 OID 17396)
-- Name: song_search song_search_search_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.song_search
    ADD CONSTRAINT song_search_search_id_foreign FOREIGN KEY (search_id) REFERENCES public.searches(search_id);


--
-- TOC entry 3521 (class 2606 OID 17376)
-- Name: song_search song_search_song_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.song_search
    ADD CONSTRAINT song_search_song_id_foreign FOREIGN KEY (song_id) REFERENCES public.song(song_id);


--
-- TOC entry 3525 (class 2606 OID 17381)
-- Name: url url_song_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.url
    ADD CONSTRAINT url_song_id_foreign FOREIGN KEY (song_id) REFERENCES public.song(song_id);


--
-- TOC entry 3523 (class 2606 OID 17391)
-- Name: user_song user_song_song_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_song
    ADD CONSTRAINT user_song_song_id_foreign FOREIGN KEY (song_id) REFERENCES public.song(song_id);


--
-- TOC entry 3524 (class 2606 OID 17401)
-- Name: user_song user_song_user_id_foreign; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.user_song
    ADD CONSTRAINT user_song_user_id_foreign FOREIGN KEY (user_id) REFERENCES public.users(user_id);


-- Completed on 2023-12-04 23:01:43 EST

--
-- PostgreSQL database dump complete
--

