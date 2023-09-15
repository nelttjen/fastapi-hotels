my_db = db.getSiblingDB('bookings');
test_db = db.getSiblingDB('test');

my_db.createCollection('verification_codes');
my_db.createCollection('email_code_sent');
test_db.createCollection('email_code_sent');
test_db.createCollection('email_code_sent');

my_db.createUser({
    "user": "admin",
    "pwd": "adminpass123",
    "roles": [{
        "role": "readWrite",
        "db": "bookings"
    }]
})

test_db.createUser({
    "user": "tester",
    "pwd": "test_db",
    "roles": [{
        "role": "readWrite",
        "db": "test"
    }]
})
