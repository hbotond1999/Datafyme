\c fulfillment
CREATE TABLE fulfillment.orders (
	order_id int4 NULL,
	order_date varchar(50) NULL,
	product_id varchar(50) NULL,
	closing_date varchar(50) NULL,
	company_id varchar(50) NULL,
	quantity int4 NULL,
	location_id varchar(50) NULL,
	PRIMARY KEY(order_id),
    CONSTRAINT fk_product FOREIGN KEY(product_id) REFERENCES fulfillment.products(product_id)
);
