my_db = db.getSiblingDB('prod_bookings');

my_db.createCollection('verification_codes');
my_db.createCollection('email_code_sent');

my_db.createUser({
    "user": "admin",
    "pwd": "adminpass123",
    "roles": [{
        "role": "readWrite",
        "db": "prod_bookings"
    }]
})
