from app.models.biller_master import BillerMaster


class BillerRepository:

    @staticmethod
    def get_rules_by_tenant(tenant_name):

        return BillerMaster.query.filter(
            BillerMaster.biller_name == tenant_name
        ).all()