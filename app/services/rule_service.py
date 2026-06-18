import json
import logging

from app.cache.memory_cache import memory_cache
from app.cache.redis_cache import redis_client
from app.repository.biller_repository import BillerRepository
from app.exceptions.exceptions import RuleNotFoundException


class RuleService:

    @staticmethod
    def get_rules(tenant_name):

        cache_key = f"rules:{tenant_name}"

        # -------------------
        # L1 Cache
        # -------------------

        if cache_key in memory_cache:

            logging.info(
                f"L1 Cache Hit : {tenant_name}"
            )

            return memory_cache[cache_key]

        logging.info(
            f"L1 Cache Miss : {tenant_name}"
        )

        # -------------------
        # L2 Cache
        # -------------------

        redis_data = redis_client.get(cache_key)

        if redis_data:

            logging.info(
                f"L2 Redis Hit : {tenant_name}"
            )

            response = json.loads(redis_data)

            memory_cache[cache_key] = response

            return response

        logging.info(
            f"L2 Redis Miss : {tenant_name}"
        )

        # -------------------
        # DB Query
        # -------------------

        rows = BillerRepository.get_rules_by_tenant(
            tenant_name
        )

        if not rows:
            raise RuleNotFoundException(
                f"No rules found for {tenant_name}"
            )

        response = {
            "tenant": tenant_name,
            "rules": []
        }

        for row in rows:

            response["rules"].append(
                {
                    "rule_name": row.rule_name,
                    "rule_value": row.rule_value
                }
            )

        # -------------------
        # Update Redis
        # -------------------

        redis_client.setex(
            cache_key,
            86400,
            json.dumps(response)
        )

        # -------------------
        # Update Memory
        # -------------------

        memory_cache[cache_key] = response

        return response

    @staticmethod
    def invalidate_cache(tenant_name):

        cache_key = f"rules:{tenant_name}"

        l1_removed = False

        if cache_key in memory_cache:
            del memory_cache[cache_key]
            l1_removed = True

        redis_removed = redis_client.delete(cache_key)

        logging.info(
            f"Cache invalidated for tenant : {tenant_name}"
        )

        return {
            "tenant": tenant_name,
            "l1_cache_removed": l1_removed,
            "redis_cache_removed": bool(redis_removed)
        }

