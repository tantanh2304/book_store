-- Script tạo database và cấu hình cho SQL Server
-- Chạy script này trong SQL Server Management Studio

-- 1. Tạo database
CREATE DATABASE BookstoreDB;
GO

-- 2. Sử dụng database vừa tạo
USE BookstoreDB;
GO

-- 3. Tạo bảng users
CREATE TABLE users (
    id INT PRIMARY KEY IDENTITY(1,1),
    username NVARCHAR(80) UNIQUE NOT NULL,
    email NVARCHAR(120) UNIQUE NOT NULL,
    password_hash NVARCHAR(255) NOT NULL,
    created_at DATETIME DEFAULT GETDATE()
);
GO

-- 4. Tạo bảng books
CREATE TABLE books (
    id INT PRIMARY KEY IDENTITY(1,1),
    title NVARCHAR(200) NOT NULL,
    author NVARCHAR(100) NOT NULL,
    description NVARCHAR(MAX),
    price FLOAT NOT NULL,
    stock INT DEFAULT 0,
    image_url NVARCHAR(300) DEFAULT 'default_book.jpg',
    category NVARCHAR(50),
    created_at DATETIME DEFAULT GETDATE()
);
GO

-- 5. Tạo bảng cart_items
CREATE TABLE cart_items (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT DEFAULT 1,
    added_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id) ON DELETE CASCADE
);
GO

-- 6. Tạo bảng orders
CREATE TABLE orders (
    id INT PRIMARY KEY IDENTITY(1,1),
    user_id INT NOT NULL,
    total_amount FLOAT NOT NULL,
    status NVARCHAR(20) DEFAULT 'pending',
    created_at DATETIME DEFAULT GETDATE(),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
GO

-- 7. Tạo bảng order_items
CREATE TABLE order_items (
    id INT PRIMARY KEY IDENTITY(1,1),
    order_id INT NOT NULL,
    book_id INT NOT NULL,
    quantity INT NOT NULL,
    price FLOAT NOT NULL,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (book_id) REFERENCES books(id)
);
GO

-- 8. Thêm dữ liệu mẫu cho bảng books
INSERT INTO books (title, author, description, price, stock, category, image_url) VALUES
(N'Đắc Nhân Tâm', N'Dale Carnegie', N'Cuốn sách về nghệ thuật giao tiếp và ứng xử để thành công trong cuộc sống', 89000, 50, N'Kỹ năng sống', 'dac_nhan_tam.jpg'),
(N'Nhà Giả Kim', N'Paulo Coelho', N'Câu chuyện về hành trình tìm kiếm kho báu và ý nghĩa cuộc đời', 79000, 30, N'Tiểu thuyết', 'nha_gia_kim.jpg'),
(N'Sapiens', N'Yuval Noah Harari', N'Lược sử loài người - từ thời kỳ đồ đá đến kỷ nguyên công nghệ', 199000, 20, N'Khoa học', 'sapiens.jpg'),
(N'Tôi Tài Giỏi, Bạn Cũng Thế', N'Adam Khoo', N'Phương pháp học tập hiệu quả từ học sinh kém đến thủ khoa', 95000, 40, N'Kỹ năng học tập', 'toi_tai_gioi.jpg'),
(N'Tuổi Trẻ Đáng Giá Bao Nhiêu', N'Rosie Nguyễn', N'Sách về định hướng và phát triển bản thân cho tuổi trẻ', 79000, 35, N'Kỹ năng sống', 'tuoi_tre.jpg'),
(N'Cà Phê Cùng Tony', N'Tony Buổi Sáng', N'Những bài học kinh doanh và cuộc sống từ một doanh nhân thành đạt', 85000, 45, N'Kinh doanh', 'ca_phe_tony.jpg'),
(N'Không Diệt Không Sinh Đừng Sợ Hãi', N'Thích Nhất Hạnh', N'Triết lý Phật giáo về cuộc sống và cái chết', 108000, 25, N'Tâm linh', 'khong_diet_khong_sinh.jpg'),
(N'Muôn Kiếp Nhân Sinh', N'Nguyên Phong', N'Những câu chuyện về luân hồi và nghiệp báo', 280000, 15, N'Tâm linh', 'muon_kiep_nhan_sinh.jpg');
GO

-- 9. Tạo user mẫu (password: 123456)
-- Password hash được tạo bởi Werkzeug: pbkdf2:sha256:260000$...
INSERT INTO users (username, email, password_hash) VALUES
(N'admin', N'admin@bookstore.com', N'pbkdf2:sha256:260000$8jxMzQJZkVn0aGvN$8c8e35b1a3d8a7d2e1f9c7b5a3d8c7e1f9a7b5c3d8e7f9a7b5c3d8e7f9a7b5c3');
GO

-- 10. Tạo indexes để tăng hiệu suất truy vấn
CREATE INDEX idx_books_category ON books(category);
CREATE INDEX idx_books_title ON books(title);
CREATE INDEX idx_cart_user ON cart_items(user_id);
CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
GO

-- 11. Tạo stored procedure để kiểm tra tồn kho
CREATE PROCEDURE sp_CheckStock
    @book_id INT,
    @quantity INT
AS
BEGIN
    SELECT CASE 
        WHEN stock >= @quantity THEN 1
        ELSE 0
    END AS is_available
    FROM books
    WHERE id = @book_id;
END;
GO

-- 12. Tạo trigger để cập nhật stock khi đặt hàng
CREATE TRIGGER trg_UpdateStockOnOrder
ON order_items
AFTER INSERT
AS
BEGIN
    UPDATE books
    SET stock = stock - i.quantity
    FROM books b
    INNER JOIN inserted i ON b.id = i.book_id;
END;
GO

-- 13. Tạo view để xem thống kê bán hàng
CREATE VIEW vw_SalesStatistics AS
SELECT 
    b.id,
    b.title,
    b.author,
    b.category,
    COUNT(oi.id) AS total_orders,
    SUM(oi.quantity) AS total_quantity_sold,
    SUM(oi.price * oi.quantity) AS total_revenue
FROM books b
LEFT JOIN order_items oi ON b.id = oi.book_id
GROUP BY b.id, b.title, b.author, b.category;
GO

-- 14. Tạo procedure để lấy top sách bán chạy
CREATE PROCEDURE sp_GetTopSellingBooks
    @top_n INT = 10
AS
BEGIN
    SELECT TOP (@top_n)
        b.id,
        b.title,
        b.author,
        b.price,
        b.image_url,
        COUNT(oi.id) AS order_count,
        SUM(oi.quantity) AS total_sold
    FROM books b
    INNER JOIN order_items oi ON b.id = oi.book_id
    GROUP BY b.id, b.title, b.author, b.price, b.image_url
    ORDER BY total_sold DESC;
END;
GO

-- 15. Hiển thị thông tin database
PRINT N'Database BookstoreDB đã được tạo thành công!';
PRINT N'';
PRINT N'Các bảng đã tạo:';
SELECT TABLE_NAME FROM INFORMATION_SCHEMA.TABLES WHERE TABLE_TYPE = 'BASE TABLE';
PRINT N'';
PRINT N'Số lượng sách mẫu: ';
SELECT COUNT(*) AS total_books FROM books;
GO