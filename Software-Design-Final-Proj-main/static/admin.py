from flask_admin import Admin 
from flask_admin.contrib.sqla import ModelView
from static.entities import *
from flask_admin.model import filters
from wtforms import TextAreaField

admin = Admin()

class AddressView(ModelView):
    form_columns = ['streetName', 'streetNumber', 'city', 'province', 'postalCode']
    form_lists = {
        'streetName': ['streetName', 'streetNumber', 'city', 'province', 'postalCode']
    }
    column_labels = {'streetName': 'Street Name', 'streetNumber': 'Street Number', 'city': 'City',
                     'province': 'Province', 'postalCode': 'Postal Code'}
    column_searchable_list = ['streetName', 'city', 'province', 'postalCode']
    column_filters = [
        'city',
        'province',
        'postalCode',
        'province',  # Add province to the list of filters
    ]
    column_sortable_list = ['city', 'province', 'postalCode']
    page_size = 50
    form_overrides = dict(postalCode=TextAreaField)
    form_widget_args = {'postalCode': {'rows': 5}}

class CarView(ModelView):
    form_columns = ['carMake', 'carModel', 'yearMade', 'carColor', 'licensePlate', 'classID']
    form_lists = {
        'carMake': ['carMake', 'carModel', 'yearMade', 'carColor', 'licensePlate', 'classID']
    }
    column_searchable_list = ['carMake', 'carModel', 'carColor', 'licensePlate']
    column_filters = ['yearMade', 'carColor']

class PromotionalView(ModelView):
    form_columns = ['classID', 'discountRate', 'startPromoDate', 'endPromoDate', 'duration']
    form_lists = {'classID': ['classID', 'discountRate', 'startPromoDate', 'endPromoDate', 'duration'] }
    column_filters = ['startPromoDate', 'endPromoDate']

class RentView(ModelView):
    form_columns = ['carID', 'locationRentedID', 'locationDropOffID', 'odometerRented', 'odometerReturned',
                    'gasVolume', 'dateRented', 'dateReturned', 'requestedClass', 'receivedClass', 'promotionalID', 'driverLicense']
    form_lists = {
        'carID': ['carID', 'locationRentedID', 'locationDropOffID', 'odometerRented', 'odometerReturned',
                  'gasVolume', 'dateRented', 'dateReturned', 'requestedClass', 'receivedClass', 'promotionalID', 'driverLicense']
    }

class UserView(ModelView):
    form_columns = ['name', 'addressID', 'type']
    form_lists = {
        'name': ['name', 'addressID', 'type']
    }

class PhoneNumberView(ModelView):
    form_columns = ['phoneNumbers', 'owner']
    form_lists = {
        'phoneNumbers': ['phoneNumbers', 'owner']
    }

class EmployeeView(ModelView):
    form_columns = ['locationAssignedID', 'category', 'isPresident', 'isVicePresident']
    form_lists = {
        'locationAssignedID': ['locationAssignedID', 'category', 'isPresident', 'isVicePresident']
    }

class CustomerView(ModelView):
    form_columns = ['description']
    form_lists = {
        'description': ['description']
    }

admin.add_view(AddressView(Address, db.session))
admin.add_view(CarView(Car, db.session))
admin.add_view(PromotionalView(Promotional, db.session))
admin.add_view(RentView(Rent, db.session))
admin.add_view(UserView(User, db.session))
admin.add_view(PhoneNumberView(PhoneNumber, db.session))
admin.add_view(EmployeeView(Employee, db.session))
admin.add_view(CustomerView(Customer, db.session))
