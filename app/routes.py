from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, RegisterForm, PurchaseItemForm, SellItemForm, AddItemForm, SetBudgetForm
from .models import User, Item
from .extensions import db

# Blueprint for authentication related routes
auth_bp = Blueprint('auth', __name__)

# Blueprint for market related routes
market_bp = Blueprint('market', __name__)

# Market-related routes
@market_bp.route("/market", methods=['GET', 'POST'])
@login_required
def market_page():
    purchase_form = PurchaseItemForm()
    sell_form = SellItemForm()

    # Handle POST request for buying or selling items
    if request.method == "POST":
        purchased_item_name = request.form.get('purchased_item')
        sold_item_name = request.form.get('sold_item')

        if purchased_item_name:
            item_obj = Item.query.filter_by(name=purchased_item_name).first()
            if item_obj and current_user.can_purchase(item_obj):
                item_obj.buy(current_user)
                db.session.commit()
                flash(f"Congratulations! You purchased {item_obj.name} for {item_obj.price}$", category='success')
            else:
                flash("Not enough money to purchase this item or item not found.", category='danger')

        if sold_item_name:
            item_obj = Item.query.filter_by(name=sold_item_name).first()
            if item_obj and current_user.can_sell(item_obj):
                item_obj.sell(current_user)
                db.session.commit()
                flash(f"Congratulations! You sold {item_obj.name} back to market!", category='success')
            else:
                flash("Something went wrong with selling this item!", category='danger')

        return redirect(url_for('market.market_page'))

    # Retrieve items for GET request
    items = Item.query.filter(Item.owner_id.is_(None)).all()  # Items available for purchase
    owned_items = Item.query.filter_by(owner_id=current_user.id).all()  # Items owned by current user

    return render_template('MARKET.html', items=items, owned_items=owned_items, purchase_form=purchase_form, sell_form=sell_form)


@market_bp.route("/add_item", methods=['GET', 'POST'])
@login_required
def add_item():
    if not current_user.is_admin:
        flash("Only admin users can access this page.", category="error")
        return redirect(url_for('market_page'))
    
    form = AddItemForm()
    if form.validate_on_submit():
        new_item = Item(
            name=form.name.data,
            barcode=form.barcode.data,
            price=form.price.data,
            description=form.description.data,
            owner_id=None  # Assuming items are owned by the store/admin initially
        )
        db.session.add(new_item)
        db.session.commit()
        flash('New item added successfully!', category='success')
        return redirect(url_for('market.market_page'))
    
    return render_template('add_item.html', form=form)



# Authentication and administration routes
@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login URL"""
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            return redirect(next_page if next_page else url_for('market.market_page'))
        flash('Invalid username or password')
    return render_template('LOGIN.html', form=form)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    """Registration URL"""
    form = RegisterForm()
    if form.validate_on_submit():
        user = User(username=form.username.data, email_address=form.email_address.data)
        # Assuming password is hashed within the model or before saving
        user.password = form.password1.data
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Account created successfully! You are now logged in.')
        return redirect(url_for('market.market_page'))
    return render_template('REGISTER.html', form=form)

@market_bp.route('/set_budget', methods=['GET', 'POST'])
@login_required
def set_budget():
    form = SetBudgetForm()
    if form.validate_on_submit():
        if current_user.check_password(form.password.data):  # Assuming there's a password field in SetBudgetForm to confirm changes
            current_user.budget = form.budget.data
            db.session.commit()
            flash('Your budget has been updated successfully!', 'success')
            return redirect(url_for('market.market_page'))
        else:
            flash('Invalid password. Please try again.', 'danger')
    return render_template('set_budget.html', form=form)


@auth_bp.route('/logout')
def logout():
    """Used to log out a user"""
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('auth.login'))

@auth_bp.route("/admin")
@login_required
def admin_page():
    """Admin panel access"""
    if not current_user.is_admin:
        flash('Access denied: Admins only.', category='danger')
        return redirect(url_for('auth.login'))
    users = User.query.all()
    items = Item.query.all()
    return render_template('ADMIN.html', users=users, items=items)

# Main application setup should import and register these Blueprints
