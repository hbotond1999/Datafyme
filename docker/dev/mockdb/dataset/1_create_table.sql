CREATE TABLE fulfillment.products (
	id int4 NULL,
	product_id varchar(50) NULL,
	product_name varchar(50) NULL,
	storage_size int4 NULL,
	price int4 NULL,
	PRIMARY KEY(product_id)
);
