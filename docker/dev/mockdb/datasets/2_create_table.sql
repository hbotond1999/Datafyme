\c fulfillment
CREATE TABLE fulfillment.deliveries (
	delivery_id int4 NULL,
	delivery_date varchar(50) NULL,
	product_id varchar(50) NULL,
	location_id varchar(50) NULL,
	quantity int4 NULL,
	PRIMARY KEY(delivery_id),
    CONSTRAINT fk_product FOREIGN KEY(product_id) REFERENCES fulfillment.products(product_id)
);
