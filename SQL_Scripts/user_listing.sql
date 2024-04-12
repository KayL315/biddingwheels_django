SELECT 
    cl.listid, cl.licenseNumber, cl.engineSerialNumber, cl.make, cl.model, 
    cl.year, cl.mileage, cl.city, cl.color, cl.additionalFeatures, 
    cl.description, cl.startingPrice, cl.biddingDeadline, cl.highestBid, 
    cl.highestBidHolder, cl.image
FROM 
    CarListing cl
JOIN 
    User u ON cl.sellerID = u.user_id
WHERE 
    u.user_id = <user_id>;
