SELECT highestBid FROM CarListing WHERE listid = listid;
SELECT * FROM Transactions WHERE buyer_id = user_id AND list_id = listid;
UPDATE Transactions SET amount = bid, date = datetime.now() WHERE buyer_id = user_id AND list_id = listid;
UPDATE CarListing SET highestBid = bid, highestBidHolder = user_id WHERE listid = listid;