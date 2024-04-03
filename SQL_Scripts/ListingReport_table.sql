DROP TABLE IF EXISTS ListingReport;

CREATE TABLE ListingReport(
	report_id INT AUTO_INCREMENT PRIMARY KEY,
    reporter_id INT,
    foreign key (reporter_id) references User(user_id),
    submit_time DATETIME,
    description TEXT(5000) NOT NULL,
    listing_id INT,
	FOREIGN KEY (listing_id) references CarListing(listid)
);

INSERT INTO ListingReport(reporter_id, submit_time, description, listing_id) VALUES(5, NOW(), "Something wrong with this car", 1);
INSERT INTO ListingReport(reporter_id, submit_time, description, listing_id) VALUES(6, NOW(), "Something wrong with this car", 1);
