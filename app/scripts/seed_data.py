from datetime import datetime

from app import create_app
from app.extensions import db
from app.models.biller_master import BillerMaster

app = create_app()

with app.app_context():

    db.create_all()

    if not BillerMaster.query.first():

        records = [
            BillerMaster(
                key=1,
                biller_name="Jio",
                rule_name="GST_NO",
                rule_value="12345",
                created_at=datetime.now(),
                created_by="Admin",
                modified_at=datetime.now(),
                modified_by="Admin"
            ),
            BillerMaster(
                key=2,
                biller_name="Airtel",
                rule_name="GST_NO",
                rule_value="5463",
                created_at=datetime.now(),
                created_by="Admin",
                modified_at=datetime.now(),
                modified_by="Admin"
            )
        ]

        db.session.add_all(records)
        db.session.commit()

        print("Data inserted")