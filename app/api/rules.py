from flask import Blueprint
from flask import jsonify

from app.services.rule_service import RuleService

rules_bp = Blueprint(
    "rules",
    __name__
)


@rules_bp.route(
    "/getRules/<tenant_name>",
    methods=["GET"]
)
def get_rules(tenant_name):

    response = RuleService.get_rules(
        tenant_name
    )

    return jsonify(response)


@rules_bp.route(
    "/invalidateCache/<tenant_name>",
    methods=["POST"]
)
def invalidate_cache(tenant_name):

    response = RuleService.invalidate_cache(
        tenant_name
    )

    return jsonify(
        {
            "status": "success",
            "message": f"Cache invalidated for {tenant_name}",
            "data": response
        }
    )
