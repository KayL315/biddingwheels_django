SELECT 
	c.listid as Listing_id, c.image, c.make as Make, c.model as Model, 
	u.username as Seller, u.user_id as SellerId, 
	with_listid.description, with_listid.Reporter, with_listid.Reporter_id
FROM
	CarListing c
	INNER JOIN (
		SELECT 
			r.listing_id as Lister, r.description, 
			u.username as Reporter, r.reporter_id as Reporter_id
		FROM 
			biddingwheels.ListingReport r
			INNER JOIN user u ON u.user_id = r.reporter_id
	) as with_listid ON c.listid = with_listid.Lister
	INNER JOIN user u ON u.user_id = c.sellerid