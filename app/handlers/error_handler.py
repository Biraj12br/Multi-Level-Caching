from flask import jsonify

from app.exceptions.exceptions import RuleNotFoundException


def register_error_handlers(app):

    @app.errorhandler(RuleNotFoundException)
    def handle_rule_not_found(error):

        return jsonify(
            {
                "status": "failed",
                "message": str(error)
            }
        ), 404

    @app.errorhandler(Exception)
    def handle_generic_exception(error):

        return jsonify(
            {
                "status": "failed",
                "message": str(error)
            }
        ), 500