from . import db
from sqlalchemy.dialects.postgresql import UUID
import uuid

class User(db.Model):
    userId = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    firstName = db.Column(db.String(50), nullable=False)
    lastName = db.Column(db.String(50), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    phone = db.Column(db.String(15))

    organisations = db.relationship('Organisation', secondary='user_organisation', back_populates='users')

class Organisation(db.Model):
    orgId = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(255))

    users = db.relationship('User', secondary='user_organisation', back_populates='organisations')

class UserOrganisation(db.Model):
    __tablename__ = 'user_organisation'
    user_id = db.Column(UUID(as_uuid=True), db.ForeignKey('user.userId'), primary_key=True)
    org_id = db.Column(UUID(as_uuid=True), db.ForeignKey('organisation.orgId'), primary_key=True)
