from django.db import models
from django.db.models.constraints import CheckConstraint
from decimal import Decimal

MIN_NOTIONAL_MARGIN_COEFFICIENT = 1.2
MIN_NOTIONAL_MARGIN_CONST = 5.0


def get_margined_min_notional(min_notional: float) -> float:
    return min_notional * MIN_NOTIONAL_MARGIN_COEFFICIENT + MIN_NOTIONAL_MARGIN_CONST


def ExactlyOneNonNullConstraint(*, fields: list[str]) -> CheckConstraint:
    # Ref: https://stackoverflow.com/questions/69014785/compare-expression-with-constant-in-check-constraint
    return CheckConstraint(
        check=models.expressions.ExpressionWrapper(
            models.Q(
                models.lookups.Exact(
                    lhs=models.expressions.Func(
                        *fields,
                        function="num_nonnulls",
                        output_field=models.IntegerField(),
                    ),
                    rhs=models.Value(1),
                )
            ),
            output_field=models.BooleanField(),
        ),
        name=f"exactly_one_non_null__{'__'.join(fields)}",
    )
