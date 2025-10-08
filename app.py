from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_login import LoginManager, login_user, logout_user, login_required, current_user
from models import db, User, Book, CartItem, Order, OrderItem
from config import Config

app = Flask(__name__)
app.config.from_object(Config)

# Initialize extensions
db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Tạo database và tables
with app.app_context():
    db.create_all()
    # Thêm sách mẫu nếu chưa có
    if Book.query.count() == 0:
        sample_books = [
            Book(title='Đắc Nhân Tâm', author='Dale Carnegie', 
                 description='Cuốn sách về nghệ thuật giao tiếp và ứng xử', 
                 price=89000, stock=50, category='Kỹ năng sống', 
                 image_url='dac_nhan_tam.jpg'),
            Book(title='Nhà Giả Kim', author='Paulo Coelho', 
                 description='Câu chuyện về hành trình tìm kiếm kho báu', 
                 price=79000, stock=30, category='Tiểu thuyết',
                 image_url='nha_gia_kim.jpg'),
            Book(title='Sapiens', author='Yuval Noah Harari', 
                 description='Lược sử loài người', 
                 price=199000, stock=20, category='Khoa học',
                 image_url='sapiens.jpg'),
            Book(title='Tôi Tài Giỏi, Bạn Cũng Thế', author='Adam Khoo', 
                 description='Phương pháp học tập hiệu quả', 
                 price=95000, stock=40, category='Kỹ năng học tập',
                 image_url='toi_tai_gioi.jpg'),
        ]
        db.session.add_all(sample_books)
        db.session.commit()

# Routes
@app.route('/')
def index():
    books = Book.query.limit(8).all()
    return render_template('index.html', books=books)

@app.route('/books')
def books():
    category = request.args.get('category')
    search = request.args.get('search')
    
    query = Book.query
    
    if category:
        query = query.filter_by(category=category)
    
    if search:
        query = query.filter(Book.title.contains(search) | Book.author.contains(search))
    
    books = query.all()
    categories = db.session.query(Book.category).distinct().all()
    
    return render_template('books.html', books=books, categories=categories)

@app.route('/book/<int:book_id>')
def book_detail(book_id):
    book = Book.query.get_or_404(book_id)
    return render_template('book_detail.html', book=book)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        email = request.form.get('email')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Tên đăng nhập đã tồn tại!', 'danger')
            return redirect(url_for('register'))
        
        if User.query.filter_by(email=email).first():
            flash('Email đã được sử dụng!', 'danger')
            return redirect(url_for('register'))
        
        user = User(username=username, email=email)
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        
        flash('Đăng ký thành công! Vui lòng đăng nhập.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        user = User.query.filter_by(username=username).first()
        
        if user and user.check_password(password):
            login_user(user)
            flash('Đăng nhập thành công!', 'success')
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('index'))
        else:
            flash('Tên đăng nhập hoặc mật khẩu không đúng!', 'danger')
    
    return render_template('login.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Đã đăng xuất!', 'info')
    return redirect(url_for('index'))

@app.route('/cart')
@login_required
def cart():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    total = sum(item.book.price * item.quantity for item in cart_items)
    return render_template('cart.html', cart_items=cart_items, total=total)

@app.route('/add_to_cart/<int:book_id>', methods=['POST'])
@login_required
def add_to_cart(book_id):
    book = Book.query.get_or_404(book_id)
    quantity = int(request.form.get('quantity', 1))
    
    cart_item = CartItem.query.filter_by(user_id=current_user.id, book_id=book_id).first()
    
    if cart_item:
        cart_item.quantity += quantity
    else:
        cart_item = CartItem(user_id=current_user.id, book_id=book_id, quantity=quantity)
        db.session.add(cart_item)
    
    db.session.commit()
    flash(f'Đã thêm "{book.title}" vào giỏ hàng!', 'success')
    return redirect(url_for('books'))

@app.route('/update_cart/<int:item_id>', methods=['POST'])
@login_required
def update_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    
    if cart_item.user_id != current_user.id:
        flash('Không có quyền truy cập!', 'danger')
        return redirect(url_for('cart'))
    
    quantity = int(request.form.get('quantity', 1))
    
    if quantity > 0:
        cart_item.quantity = quantity
    else:
        db.session.delete(cart_item)
    
    db.session.commit()
    flash('Đã cập nhật giỏ hàng!', 'success')
    return redirect(url_for('cart'))

@app.route('/remove_from_cart/<int:item_id>')
@login_required
def remove_from_cart(item_id):
    cart_item = CartItem.query.get_or_404(item_id)
    
    if cart_item.user_id != current_user.id:
        flash('Không có quyền truy cập!', 'danger')
        return redirect(url_for('cart'))
    
    db.session.delete(cart_item)
    db.session.commit()
    flash('Đã xóa sản phẩm khỏi giỏ hàng!', 'success')
    return redirect(url_for('cart'))

@app.route('/checkout', methods=['POST'])
@login_required
def checkout():
    cart_items = CartItem.query.filter_by(user_id=current_user.id).all()
    
    if not cart_items:
        flash('Giỏ hàng trống!', 'warning')
        return redirect(url_for('cart'))
    
    try:
        total_amount = sum(item.book.price * item.quantity for item in cart_items)
        
        # Tạo đơn hàng
        order = Order(user_id=current_user.id, total_amount=total_amount)
        db.session.add(order)
        db.session.flush()  # Lấy order.id
        
        # Tạo chi tiết đơn hàng - thêm từng item một để tránh lỗi bulk insert
        for item in cart_items:
            order_item = OrderItem(
                order_id=order.id,
                book_id=item.book_id,
                quantity=item.quantity,
                price=item.book.price
            )
            db.session.add(order_item)
            db.session.flush()  # Flush sau mỗi item
            
            # Giảm số lượng sách trong kho
            book = Book.query.get(item.book_id)
            if book:
                book.stock -= item.quantity
        
        # Xóa giỏ hàng
        for item in cart_items:
            db.session.delete(item)
        
        db.session.commit()
        flash('Đặt hàng thành công!', 'success')
        return redirect(url_for('order_success', order_id=order.id))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Có lỗi xảy ra: {str(e)}', 'danger')
        return redirect(url_for('cart'))

@app.route('/order_success/<int:order_id>')
@login_required
def order_success(order_id):
    order = Order.query.get_or_404(order_id)
    
    if order.user_id != current_user.id:
        flash('Không có quyền truy cập!', 'danger')
        return redirect(url_for('index'))
    
    return render_template('order_success.html', order=order)

@app.route('/my_orders')
@login_required
def my_orders():
    orders = Order.query.filter_by(user_id=current_user.id).order_by(Order.created_at.desc()).all()
    return render_template('my_orders.html', orders=orders)

if __name__ == '__main__':
    app.run(debug=True)