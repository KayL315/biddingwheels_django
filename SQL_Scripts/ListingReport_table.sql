DROP TABLE IF EXISTS ListingReport;

CREATE TABLE ListingReport(
	report_id INT AUTO_INCREMENT PRIMARY KEY,
    reporter_id INT,
    foreign key (reporter_id) references user(user_id),
    submit_time DATETIME,
    description TEXT(5000) NOT NULL,
    listing_id INT,
	FOREIGN KEY (listing_id) references CarListing(listid)
);


