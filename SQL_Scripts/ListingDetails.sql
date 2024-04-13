SELECT 
	cl.listid, cl.licenseNumber, cl.engineSerialNumber, cl.make, cl.model, 
	cl.year, cl.mileage, cl.city, cl.color, cl.additionalFeatures, 
	cl.description, cl.startingPrice, cl.biddingDeadline, cl.highestBid, 
	cl.highestBidHolder, u.username, u.user_id as seller, b.username AS highestBidHolderUsername, 
	b.user_id as highestBidHolder, cl.image
FROM 
	CarListing cl
	JOIN user u ON cl.sellerID = u.user_id
	LEFT JOIN user b ON cl.highestBidHolder = b.user_id
WHERE 
	cl.listid = listid；