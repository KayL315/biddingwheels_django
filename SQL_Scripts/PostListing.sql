INSERT INTO CarListing
		(sellerID, licenseNumber, engineSerialNumber, make, model, year, mileage, city, color, additionalFeatures, 
        description, startingPrice, biddingDeadline, highestBid, highestBidHolder, image)
		VALUES (user_id, licenseNumber, engineSerialNumber, make, model, year, mileage, city, color, additionalFeatures, 
        description, startingPrice, STR_TO_DATE(biddingDeadline, '%%Y-%%m-%%dT%%H:%%i:%%sZ'), highestBid, highestBidHolder, 
        image);