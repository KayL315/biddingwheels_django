CREATE TABLE Payment (
  payment_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  cardName VARCHAR(255) NOT NULL,
  cardNumber VARCHAR(255) NOT NULL,
  expMonth VARCHAR(255) NOT NULL,
  expYear VARCHAR(255) NOT NULL,
  cvv VARCHAR(255) NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user(user_id)
)