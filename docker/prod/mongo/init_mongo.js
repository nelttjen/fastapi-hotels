my_db = db.getSiblingDB('bookings');

my_db.createCollection('verification_codes');
my_db.createCollection('email_code_sent');

my_db.createUser({
    "user": "admin",
    "pwd": "adminpass123",
    "roles": [{
        "role": "readWrite",
        "db": "bookings"
    }]
})
