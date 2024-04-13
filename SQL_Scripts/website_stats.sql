SELECT 
	COUNT(*) as Total_Sales, 
	 date
FROM Transactions
GROUP BY 
	date;
    
SELECT COUNT(model)as model_sales, model
FROM
(SELECT 
	COUNT(*) as Total_Sales, 
	model, date
FROM (
	SELECT * 
	FROM Transactions t
	INNER JOIN CarListing c ON t.list_id = c.listid
) as joint
GROUP BY 
	date, 
	model) as sub
	GROUP BY model
ORDER BY model_sales DESC;