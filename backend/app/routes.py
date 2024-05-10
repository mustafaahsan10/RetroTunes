from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from .forms import LoginForm, RegisterForm, PurchaseItemForm, SellItemForm
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
    if request.method == "POST":
        if 'purchase' in request.form and purchase_form.validate_on_submit():
            item_obj = Item.query.filter_by(name=request.form.get('purchased_item')).first()
            if item_obj and current_user.can_purchase(item_obj):
                item_obj.buy(current_user)
                flash(f"Congratulations! You purchased {item_obj.name} for {item_obj.price}$", category='success')
            else:
                flash("Unfortunately, you don't have enough money to purchase this item!", category='danger')

        elif 'sell' in request.form and sell_form.validate_on_submit():
            item_obj = Item.query.filter_by(name=request.form.get('sold_item')).first()
            if item_obj and current_user.can_sell(item_obj):
                item_obj.sell(current_user)
                flash(f"Congratulations! You sold {item_obj.name} back to market!", category='success')
            else:
                flash("Something went wrong with selling this item!", category='danger')

        return redirect(url_for('market_page'))

    items = Item.query.filter(Item.owner_id == None).all()
    owned_items = Item.query.filter_by(owner_id=current_user.id).all()

    return render_template('MARKET.html', title='Market', item=items, owned_item=owned_items, purchase_form=purchase_form, sell_form=sell_form)

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
