SELECT transaction_id FROM Transactions
WHERE owner_id = {owner_id} AND buyer_id = {buyer_id};
                
SELECT id FROM User_ratings
WHERE rater_id = {rater} AND rated_user_id = {rated};