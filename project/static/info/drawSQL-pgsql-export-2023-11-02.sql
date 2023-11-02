CREATE TABLE "song_search"(
    "song_id" BIGINT NOT NULL,
    "search_id" BIGINT NOT NULL
);
ALTER TABLE
    "song_search" ADD PRIMARY KEY("song_id", "search_id");
CREATE TABLE "user"(
    "user_id" SERIAL NOT NULL,
    "first_name" VARCHAR(25) NOT NULL,
    "last_name" VARCHAR(25) NOT NULL,
    "email" VARCHAR(50) NOT NULL,
    "password" VARCHAR(75) NOT NULL
);
ALTER TABLE
    "user" ADD PRIMARY KEY("user_id");
ALTER TABLE
    "user" ADD CONSTRAINT "user_email_unique" UNIQUE("email");
CREATE TABLE "search"(
    "search_id" SERIAL NOT NULL,
    "search_term" VARCHAR(50) NOT NULL
);
ALTER TABLE
    "search" ADD PRIMARY KEY("search_id");
CREATE TABLE "song"(
    "song_id" SERIAL NOT NULL,
    "title" VARCHAR(50) NOT NULL,
    "lyric_url" VARCHAR(255) NOT NULL,
    "tab_url" VARCHAR(255) NOT NULL,
    "mp3_url" VARCHAR(255) NOT NULL,
    "karaoke_url" VARCHAR(255) NOT NULL,
    "search_id" INTEGER NOT NULL,
    "lyric_check" BOOLEAN NOT NULL DEFAULT '0',
    "tab_check" BOOLEAN NOT NULL DEFAULT '0',
    "mp3_check" BOOLEAN NOT NULL DEFAULT '0',
    "karaoke_check" BOOLEAN NOT NULL DEFAULT '0'
);
ALTER TABLE
    "song" ADD PRIMARY KEY("song_id");
ALTER TABLE
    "song" ADD CONSTRAINT "song_title_unique" UNIQUE("title");
CREATE TABLE "user_song"(
    "user_id" INTEGER NOT NULL,
    "song_id" INTEGER NOT NULL
);
ALTER TABLE
    "user_song" ADD PRIMARY KEY("user_id", "song_id");
ALTER TABLE
    "song_search" ADD CONSTRAINT "song_search_song_id_foreign" FOREIGN KEY("song_id") REFERENCES "song"("song_id");
ALTER TABLE
    "song_search" ADD CONSTRAINT "song_search_search_id_foreign" FOREIGN KEY("search_id") REFERENCES "search"("search_id");
ALTER TABLE
    "song" ADD CONSTRAINT "song_search_id_foreign" FOREIGN KEY("search_id") REFERENCES "song_search"("search_id");
ALTER TABLE
    "user_song" ADD CONSTRAINT "user_song_song_id_foreign" FOREIGN KEY("song_id") REFERENCES "song"("song_id");
ALTER TABLE
    "user_song" ADD CONSTRAINT "user_song_user_id_foreign" FOREIGN KEY("user_id") REFERENCES "user"("user_id");