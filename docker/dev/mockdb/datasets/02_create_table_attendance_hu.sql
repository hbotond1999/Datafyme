\c movies
CREATE TABLE movies_hu.attendance_hu (
	movie_id varchar(50) NULL,
	attendance int4 NULL,
	g_attendance int4 NULL,
	pg_attendance int4 NULL,
	pg_13_attendance int4 NULL,
	r_attendance int4 NULL,
	nc_17_attendance int4 NULL,
    CONSTRAINT attendance_hu_movies_metadata_fk FOREIGN KEY (movie_id) REFERENCES movies_metadata.movies_metadata(movie_id)
);