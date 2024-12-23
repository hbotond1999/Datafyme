\c fulfillment
CREATE TABLE fulfillment.movements (
	movement_id int4 NULL,
	location_from varchar(50) NULL,
	location_to varchar(50) NULL,
	product_id varchar(50) NULL,
	quantity int4 NULL,
	movement_date varchar(50) NULL,
	dolgozo_id varchar(50) NULL,
	PRIMARY KEY(movement_id),
    CONSTRAINT fk_product FOREIGN KEY(product_id) REFERENCES fulfillment.products(product_id)
);
