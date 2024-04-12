SELECT 
    c.listid, c.licenseNumber, c.engineSerialNumber, c.make, c.model, 
    c.year, c.mileage, c.city, c.color, c.additionalFeatures, 
    c.description, c.startingPrice, c.biddingDeadline, c.highestBid, 
    c.highestBidHolder, c.image
FROM  
    CarListing c
WHERE 
    c.sellerID = (SELECT user_id FROM User WHERE user_id = %s);
