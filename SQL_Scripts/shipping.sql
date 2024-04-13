CREATE TABLE Shipping (
  shipping_id INT PRIMARY KEY AUTO_INCREMENT,
  user_id INT,
  transaction_id INT,
  tracking_number VARCHAR(255) NOT NULL,
  address_id INT,
  status VARCHAR(255) NOT NULL,
  date DATE NOT NULL,
  FOREIGN KEY (user_id) REFERENCES user(user_id),
  FOREIGN KEY (transaction_id) REFERENCES Transactions(transaction_id),
  FOREIGN KEY (address_id) REFERENCES Address(address_id)
)