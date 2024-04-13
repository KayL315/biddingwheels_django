SELECT rated_user_id, AVG(rating) FROM biddingwheels.
User_ratings GROUP BY rated_user_id 
HAVING rated_user_id = {user_id};