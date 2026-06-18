from app.extensions import db


class BillerMaster(db.Model):

    __tablename__ = "biller_master_data"

    key = db.Column(db.Integer, primary_key=True)

    biller_name = db.Column(db.String(100), nullable=False)

    rule_name = db.Column(db.String(100), nullable=False)

    rule_value = db.Column(db.String(255), nullable=False)

    created_at = db.Column(db.DateTime)

    created_by = db.Column(db.String(100))

    modified_at = db.Column(db.DateTime)

    modified_by = db.Column(db.String(100))