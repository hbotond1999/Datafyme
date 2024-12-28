\c movies
CREATE TABLE movies_metadata.movies_metadata (
	movie_id varchar(50) NULL,
	title varchar(50) NULL,
	description varchar(128) NULL,
	release_date varchar(50) NULL,
	running_time int4 NULL,
	production_budget int4 NULL,
	age_limit varchar(50) NULL,
	imdb_rating float4 NULL,
	country_of_origin varchar(50) NULL
);