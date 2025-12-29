USE library_db;

-- 示例读者
INSERT INTO readers (name, address, gender, age, organization) VALUES
('张三','北京市朝阳区','M',28,'某公司'),
('李四','上海市浦东区','F',34,'某大学');

-- 示例图书
INSERT INTO books (isbn, title, author, publisher, total_copies, available_copies) VALUES
('978-123','数据库原理','王五','清华出版社',3,3),
('978-456','Python 编程','赵六','机械出版社',2,2);

-- 测试借书
-- CALL BorrowBook(1, 1, CURDATE(), DATE_ADD(CURDATE(), INTERVAL 30 DAY));

-- 测试还书（假设 loan_id=1）
-- CALL ReturnBook(1, DATE_ADD(CURDATE(), INTERVAL 35 DAY));

-- 方便查询示例
SELECT * FROM readers;
SELECT book_id, title, available_copies FROM books;
SELECT * FROM loans;
