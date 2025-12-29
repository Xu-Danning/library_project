-- library_db 初始化脚本
-- 使用: mysql -u root -p < db_init.sql

DROP DATABASE IF EXISTS library_db;
CREATE DATABASE library_db CHARACTER SET utf8mb4 COLLATE utf8mb4_general_ci;
USE library_db;

-- 读者表
CREATE TABLE IF NOT EXISTS readers (
  reader_id INT AUTO_INCREMENT PRIMARY KEY,
  name VARCHAR(100) NOT NULL,
  address VARCHAR(255),
  gender ENUM('M','F','Other') DEFAULT 'Other',
  age INT,
  organization VARCHAR(255),
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 图书表
CREATE TABLE IF NOT EXISTS books (
  book_id INT AUTO_INCREMENT PRIMARY KEY,
  isbn VARCHAR(30) UNIQUE,
  title VARCHAR(255) NOT NULL,
  author VARCHAR(255),
  publisher VARCHAR(255),
  total_copies INT NOT NULL DEFAULT 1,
  available_copies INT NOT NULL DEFAULT 1,
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
) ENGINE=InnoDB;

-- 借阅表
CREATE TABLE IF NOT EXISTS loans (
  loan_id INT AUTO_INCREMENT PRIMARY KEY,
  book_id INT NOT NULL,
  reader_id INT NOT NULL,
  borrow_date DATE NOT NULL,
  due_date DATE NOT NULL,
  return_date DATE DEFAULT NULL,
  fine DECIMAL(8,2) DEFAULT 0.00,
  status ENUM('borrowed','returned') NOT NULL DEFAULT 'borrowed',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  FOREIGN KEY (book_id) REFERENCES books(book_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  FOREIGN KEY (reader_id) REFERENCES readers(reader_id) ON DELETE RESTRICT ON UPDATE CASCADE,
  INDEX idx_book (book_id),
  INDEX idx_reader (reader_id),
  INDEX idx_status (status)
) ENGINE=InnoDB;

-- 权限: 确保用于操作的 MySQL 用户有相应权限

-- 存储过程：借书
DELIMITER //
CREATE PROCEDURE BorrowBook(IN p_reader INT, IN p_book INT, IN p_borrow DATE, IN p_due DATE)
BEGIN
  DECLARE avail INT;
  SELECT available_copies INTO avail FROM books WHERE book_id = p_book FOR UPDATE;
  IF avail IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Book not found';
  ELSEIF avail <= 0 THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'No copies available';
  ELSE
    INSERT INTO loans (book_id, reader_id, borrow_date, due_date, status) VALUES (p_book, p_reader, p_borrow, p_due, 'borrowed');
    UPDATE books SET available_copies = available_copies - 1 WHERE book_id = p_book;
  END IF;
END;
//
DELIMITER ;

-- 存储过程：还书
DELIMITER //
CREATE PROCEDURE ReturnBook(IN p_loan INT, IN p_return DATE)
BEGIN
  DECLARE b_id INT;
  DECLARE d_date DATE;
  DECLARE current_status ENUM('borrowed','returned');
  DECLARE days_over INT DEFAULT 0;
  SELECT book_id, due_date, status INTO b_id, d_date, current_status FROM loans WHERE loan_id = p_loan FOR UPDATE;
  IF b_id IS NULL THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Loan not found';
  ELSEIF current_status = 'returned' THEN
    SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = 'Already returned';
  ELSE
    IF p_return > d_date THEN
      SET days_over = DATEDIFF(p_return, d_date);
    ELSE
      SET days_over = 0;
    END IF;
    UPDATE loans SET return_date = p_return, fine = days_over * 1.00, status = 'returned' WHERE loan_id = p_loan;
    UPDATE books SET available_copies = available_copies + 1 WHERE book_id = b_id;
  END IF;
END;
//
DELIMITER ;

-- 可选：视图/索引等后续优化
