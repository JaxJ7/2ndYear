import random
from sqlalchemy import desc
from static import app, db
from flask import jsonify, render_template, redirect, url_for, request, flash, get_flashed_messages
from static.entities import *
import locale
from datetime import datetime
from static.forms import *
from flask_login import current_user, login_user,logout_user,login_required
from sqlalchemy.orm import aliased

def CheckFormError(form):
    if form.errors != {}:
        for err_msg in form.errors.values():
            flash(f'Error: {err_msg}', category='danger')
            
@app.route('/')
@app.route('/main')
def index():
    return render_template('main.html')

@app.route("/login", methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        attempted_user = User.query.filter_by(email=form.email.data).first()
        if attempted_user and attempted_user.checkPassword(attemptedPassword=form.password.data):
            login_user(attempted_user) 
            flash(f'Success. You are logged in as: {attempted_user.name}', category='success')
            return redirect(url_for('index'))
        else:
            flash('Email and password does not exist in the database!',category='danger')
    return render_template('login.html', form=form)

@app.route("/registerAddress", methods=['GET','POST'])
def registerAddress():
    addressForm = AddressForm()
    print(f"Request method: {request.method}")
    
    if request.method == 'POST':
        print("Form data received:")
        print(addressForm.data)
        
        if addressForm.validate_on_submit():
            print("Address form is valid")
            address_to_create = Address(
                streetName=addressForm.streetName.data,
                streetNumber=addressForm.streetNumber.data,
                city=addressForm.city.data,
                province=addressForm.province.data,
                postalCode=addressForm.postalCode.data
            )
            similarAddress = Address.query.filter(Address.fullAddressName == address_to_create.fullAddressName).all()
            if similarAddress:
                flash(f'Address {address_to_create.fullAddressName} is already in the database!',category='warning')
                return redirect(url_for('index'))
            else:
                db.session.add(address_to_create)
                db.session.commit()  # Commit the Address object to get the generated addressID
                flash(f'Success! Address {address_to_create.fullAddressName} has been saved!', category='success')
                return redirect(url_for('signup', address_id = address_to_create.addressID))
                
        else:
            print("Address form is invalid")
            CheckFormError(addressForm)          
    else:
        print("GET Method, Rendering signup template")
    return render_template('registerAddress.html', addressForm=addressForm)
    

@app.route("/signup/<int:address_id>", methods=['GET', 'POST'])
def signup(address_id):
    userForm = UserForm()
    print(f"Request method: {request.method}")
    
    userAddress = Address.query.filter_by(addressID=address_id).first()
    userForm.address.choices = [(userAddress.addressID, f'{userAddress.fullAddressName}')]
    
    if request.method == 'POST':
        print("Form data received:")
        print(userForm.data)
        
        if userForm.validate_on_submit():
            print("User form is valid")
            verification_code = userForm.verification_code.data
            
            user_to_create = User.create_user(
                driverLicense=userForm.driverLicense.data,
                name=userForm.name.data,
                email=userForm.email.data,
                addressID=userForm.address.data,  
                passwordHash=userForm.password1.data,
                verification_code=verification_code
            )
            if user_to_create is None:
                # Invalid verification code, display the error message
                flash('Invalid verification code', category='danger')
            else:
                db.session.add(user_to_create)
                db.session.commit()
                flash(f'Success! User has been created!', category='success')
                return redirect(url_for('login'))
        else:
            print("User form is invalid")
            CheckFormError(userForm)
             
    else:
        print("GET Method, Rendering signup template")
    return render_template('signup.html', userForm=userForm, address_id = userAddress.addressID)

def randomize_odometer():
    # Generate a random number between 3 and 100 (inclusive) and multiply by 10
    return random.randint(3, 100) * 10

@app.route("/registerRent/<int:car_id>", methods=['GET', 'POST']) 
@login_required 
def registerRent(car_id): 
    car = Car.query.get(car_id) 
    rentForm = RentForm() 
    
    carClasses = CarClass.query.all() 
    rentForm.requestedClass.choices = [(carClass.carClassID, f'{carClass.type}') for carClass in carClasses] 
    
    receivedClass = CarClass.query.filter_by(carClassID=car.classID).first() 
    rentForm.receivedClass.choices = [(receivedClass.carClassID, f'{receivedClass.type}')] 
    
    rentForm.odometerRented.default = randomize_odometer() 
    rentForm.process(request.form) 
    
    locations = Address.query.filter_by(isStoreLocation=True) 
    rentForm.locationRentedID.choices = [(location.addressID, f'{location.fullAddressName}') for location in locations] 
    rentForm.locationDropOffID.choices = [(location.addressID, f'{location.fullAddressName}') for location in locations] 
    
    date_rented = rentForm.dateRented.data
    if date_rented is not None:
        promos = Promotional.query.filter(Promotional.startPromoDate <= date_rented, Promotional.endPromoDate >= date_rented).all()
        rentForm.promotionalID.choices = [('', 'No promo available')] + [(promo.promotionalID, f'{promo.promoTitle}') for promo in promos]
    else:
        rentForm.promotionalID.choices = [('', 'No promo available')]
        
    if request.method == 'POST': 
        print("Form data received:") 
        print(rentForm.data) 
        
        if rentForm.validate_on_submit(): 
            print("Rent form is valid") 
            rent_to_create = Rent( 
                                  carID = car.carID, 
                                  locationRentedID = rentForm.locationRentedID.data, 
                                  locationDropOffID = rentForm.locationDropOffID.data, 
                                  odometerRented = rentForm.odometerRented.data, 
                                  odometerReturned = rentForm.odometerReturned.data, 
                                  gasVolume = rentForm.gasVolume.data, 
                                  dateRented = rentForm.dateRented.data, 
                                  dateReturned = rentForm.dateReturned.data, 
                                  requestedClass = rentForm.requestedClass.data, 
                                  receivedClass = rentForm.receivedClass.data, 
                                  promotionalID = rentForm.promotionalID.data, 
                                  driverLicense = current_user.driverLicense 
                                  ) 
            db.session.add(rent_to_create) 
            db.session.commit() 
            flash(f'Success! Rent record has been added!', category='success') 
            return redirect(url_for('Shop')) 
        else: 
            print("Rent form is invalid")
            for field, errors in rentForm.errors.items():
                print(f"Errors for field '{field}': {', '.join(errors)}") 
            CheckFormError(rentForm) 
    # Render registerRent.html template with car details 
    return render_template('registerRent.html', car=car, rentForm=rentForm) 

@app.route("/get_promos") 
def get_promos(): 
    date_rented = request.args.get("date_rented") 
    if date_rented: 
        promos = Promotional.query.filter(Promotional.startPromoDate <= date_rented, Promotional.endPromoDate >= date_rented).all() 
        if promos: 
            promo_data = [{"promotionalID": promo.promotionalID, "promoName": promo.promoName, "discountRate": promo.discountRate} for promo in promos] 
            return jsonify(promo_data) 



@app.route('/shop', methods=['GET', 'POST'])
@login_required
def Shop():
    query = request.args.get('query', '').strip()
    car_type = request.args.get('type')

    if query:
        carsWithClass = db.session.query(Car, CarClass.price).join(CarClass).filter(
            (Car.carMake.ilike(f'%{query}%') | Car.carModel.ilike(f'%{query}%') | Car.carColor.ilike(f'%{query}%'))
        ).all()
    elif car_type:
        carsWithClass = db.session.query(Car, CarClass.price).join(CarClass).filter(CarClass.type == car_type).all()
    else:
        carsWithClass = db.session.query(Car, CarClass.price).join(CarClass).all()

    results = [{'car': car, 'price': price} for car, price in carsWithClass]

    if not car_type:
        car_type = "All"
    else:
        car_type = car_type.capitalize() if car_type != "None" else "All"

    return render_template('shop.html', cars=results, car_type=car_type)


@app.route('/car_info/<int:car_id>', methods=['GET','POST'])
@login_required
def CarInfo(car_id):
    car = Car.query.get(car_id)  # Fetch the car using the car_id
    car_class = CarClass.query.get(car.classID) # Access the CarClass associated with the car object
    # Render the CarInfo.html template with the fetched information
    return render_template('CarInfo.html', car=car, car_class=car_class)

@app.route('/logout')
@login_required
def logout_page():
    logout_user()
    flash("You have been logged out!", category='info')
    return redirect(url_for('index'))

@app.route('/User/<string:user_id>', methods=['GET', 'POST'])
@login_required
def userPage(user_id):
    EmployeeLocation = None
    locations = Address.query.all()
    location_choices = [(location.addressID, f'{location.fullAddressName}') for location in locations]
                        
    user = User.query.get(user_id)
    AddressAlias = aliased(Address)
    rentsWithAll = db.session.query(Rent, Car,  Address.addressID.label('pickupAddressID'), AddressAlias.addressID.label('dropoffAddressID'),Address, AddressAlias, Promotional, CarClass) \
                                            .outerjoin(Promotional, Rent.promotionalID == Promotional.promotionalID) \
                                            .join(Car, Rent.carID == Car.carID) \
                                            .join(CarClass, Car.classID == CarClass.carClassID) \
                                            .outerjoin(Address, Rent.locationRentedID == Address.addressID) \
                                            .outerjoin(AddressAlias, Rent.locationDropOffID == AddressAlias.addressID) \
                                            .join(User, Rent.driverLicense == User.driverLicense) \
                                            .filter(User.driverLicense == user_id) \
                                            .all()

    rents = []
    for rent, car,pickupAddressID,dropoffAddressID, pickupAddress, dropoffAddress, promo, carClass in rentsWithAll:
        rentalDuration = (rent.dateReturned - rent.dateRented).days + 1
        rentalPrice = calculateRentalPrice(rentalDuration, carClass, promo)
        totalPrice = rentalPrice

        rent_data = {
            'rent': rent,
            'car': car,
            'pickupAddress': pickupAddress,
            'dropoffAddress': dropoffAddress,
            'promo': promo,
            'rentalPrice': rentalPrice,
            'totalPrice': totalPrice
        }
        rents.append(rent_data)
        
    if user.type == 'employee':
        user = Employee.query.get(user_id)
        EmployeeLocation = Address.query.get(user.locationAssignedID)


    phoneNumbers = PhoneNumber.query.filter_by(owner=user_id, isDeleted=False).all()
    return render_template('User.html', user=user, rents=rents, phoneNumbers=phoneNumbers, location_choices=location_choices, EmployeeLocation=EmployeeLocation)

def calculateRentalPrice(rentalDuration, carClass, promo):
    base_price = getPrice(rentalDuration, carClass)
    if promo:
        discount_rate = promo.discountRate
        discount_amount = base_price * discount_rate
        total_price = base_price - discount_amount
    else:
        total_price = base_price

    return total_price

def getPrice(rentalDuration, carClass):
    if rentalDuration <= 1:
        base_price = carClass.price
    elif rentalDuration <= 7:
        base_price = carClass.oneWeekPrice
    elif rentalDuration <= 14:
        base_price = carClass.twoWeekPrice
    else:
        base_price = carClass.oneMonthPrice + (rentalDuration - 30) * carClass.price

    return base_price

@app.route('/update_profile/<string:user_id>', methods=['GET','POST'])
@login_required
def update_profile(user_id):
    locations = Address.query.all()

    location_choices = [(location.addressID, f'{location.fullAddressName}') for location in locations]

    if request.method == 'POST':
        name = request.form['name']
        email = request.form['email']
        locationAssignedID = request.form['location']
        user = User.query.filter_by(driverLicense=user_id).first()
        if user:
            user.name = name
            user.email = email
            if user.type == 'employee':
                user = Employee.query.get(user_id)
                user.locationAssignedID = locationAssignedID
            db.session.commit()
            flash('Profile updated successfully!', category='success')
            return redirect(url_for('userPage', user_id=user_id))
        else:
            flash('User not found!', category='error')
        return redirect(url_for('userPage', user_id=user_id, ))
    else:
        pass

@app.route('/register_phone/<string:user_id>', methods=['POST'])
def registerPhone(user_id):
    if request.method == 'POST':
        # Get the phone number from the form
        phone_number = request.form['PhoneNumber']

        # Define a regular expression pattern for a valid 11-digit Philippines phone number
        pattern = r'^\d{11}$'  # Matches exactly 11 digits

        # Check if the phone number matches the pattern
        if re.match(pattern, phone_number):
            phoneNumber = PhoneNumber(phoneNumbers=phone_number, owner=user_id)
            db.session.add(phoneNumber)
            db.session.commit()
            return redirect(url_for('userPage', user_id=user_id))
        else:
            flash('Invalid phone number. Please enter a valid 11-digit phone number.', category='danger')
            return redirect(url_for('userPage', user_id=user_id))
    else:
        pass
    
@app.route('/deletePhone/<int:phone_id>', methods=['GET','POST'])
def deletePhone(phone_id):
    phone = PhoneNumber.query.get(phone_id)
    if phone:
        phone.isDeleted = True
        db.session.commit()
        flash('Phone number deleted successfully', 'success')
    else:
        flash('Phone number not found', 'error')
    return redirect(url_for('userPage', user_id=phone.owner))

@app.route('/promo', methods=['GET', 'POST'])
def promo():
    promos = db.session.query(Promotional).all()
    return render_template('promo.html', promos=promos)

