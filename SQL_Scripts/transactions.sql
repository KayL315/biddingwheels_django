CREATE TABLE Transactions (
  transaction_id INT PRIMARY KEY AUTO_INCREMENT,
  owner_id INT,
  buyer_id INT,
  list_id INT NOT NULL,
  amount FLOAT NOT NULL,
  date DATE NOT NULL,
  payment_id INT,
  address_id INT,
  done BOOLEAN NOT NULL DEFAULT 0,
  FOREIGN KEY (owner_id) REFERENCES user(user_id),
  FOREIGN KEY (buyer_id) REFERENCES user(user_id),
  FOREIGN KEY (list_id) REFERENCES CarListing(listid),
  FOREIGN KEY (payment_id) REFERENCES Payment(payment_id),
  FOREIGN KEY (address_id) REFERENCES Address(address_id)
)