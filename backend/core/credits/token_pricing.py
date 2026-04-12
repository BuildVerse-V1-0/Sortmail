"""
Token Pricing Utilities
-----------------------
Centralized token cost and credit conversion formulas.
"""

from __future__ import annotations

from dataclasses import dataclass
from app.config import settings


# 1 credit = $0.001
CREDIT_USD_VALUE = 0.001
MILLI_CREDITS_PER_CREDIT = 1000

# Provider rates (company cost)
PROVIDER_INPUT_PER_MILLION_USD = 0.30
PROVIDER_OUTPUT_PER_MILLION_USD = 2.50

# User-facing rates (4x markup)
USER_INPUT_PER_MILLION_USD = 1.20
USER_OUTPUT_PER_MILLION_USD = 10.00

# Nova Micro provider rates from user specification (per 1,000 tokens):
# input:  $0.000035
# output: $0.000140
# Converted to per 1,000,000 tokens for internal consistency.
NOVA_MICRO_PROVIDER_INPUT_PER_MILLION_USD = 0.035
NOVA_MICRO_PROVIDER_OUTPUT_PER_MILLION_USD = 0.14
# Keep the same 4x markup policy for user billable rates.
NOVA_MICRO_USER_INPUT_PER_MILLION_USD = NOVA_MICRO_PROVIDER_INPUT_PER_MILLION_USD * 4.0
NOVA_MICRO_USER_OUTPUT_PER_MILLION_USD = NOVA_MICRO_PROVIDER_OUTPUT_PER_MILLION_USD * 4.0

# Embedding rates (Titan Text Embeddings V2 by default)
EMBEDDING_PROVIDER_INPUT_PER_MILLION_USD = float(
    getattr(settings, "EMBEDDING_PROVIDER_INPUT_PER_MILLION_USD", 0.02) or 0.02
)
EMBEDDING_USER_INPUT_PER_MILLION_USD = float(
    getattr(settings, "EMBEDDING_USER_INPUT_PER_MILLION_USD", 0.08) or 0.08
)


def _per_token(rate_per_million: float) -> float:
    return float(rate_per_million) / 1_000_000.0


PROVIDER_INPUT_PER_TOKEN_USD = _per_token(PROVIDER_INPUT_PER_MILLION_USD)
PROVIDER_OUTPUT_PER_TOKEN_USD = _per_token(PROVIDER_OUTPUT_PER_MILLION_USD)
USER_INPUT_PER_TOKEN_USD = _per_token(USER_INPUT_PER_MILLION_USD)
USER_OUTPUT_PER_TOKEN_USD = _per_token(USER_OUTPUT_PER_MILLION_USD)


@dataclass(frozen=True)
class TokenBillingBreakdown:
    input_tokens: int
    output_tokens: int
    provider_cost_usd: float
    user_billable_usd: float
    credits_exact: float
    milli_credits_exact: int


@dataclass(frozen=True)
class EmbeddingBillingBreakdown:
    input_tokens: int
    provider_cost_usd: float
    user_billable_usd: float
    credits_exact: float
    milli_credits_exact: int


@dataclass(frozen=True)
class TokenModelPricing:
    provider_input_per_million_usd: float
    provider_output_per_million_usd: float
    user_input_per_million_usd: float
    user_output_per_million_usd: float


def _resolve_token_model_pricing(model_name: str | None = None) -> TokenModelPricing:
    model = str(model_name or "").lower()
    if "amazon.nova-micro-v1:0" in model or "nova-micro" in model:
        return TokenModelPricing(
            provider_input_per_million_usd=NOVA_MICRO_PROVIDER_INPUT_PER_MILLION_USD,
            provider_output_per_million_usd=NOVA_MICRO_PROVIDER_OUTPUT_PER_MILLION_USD,
            user_input_per_million_usd=NOVA_MICRO_USER_INPUT_PER_MILLION_USD,
            user_output_per_million_usd=NOVA_MICRO_USER_OUTPUT_PER_MILLION_USD,
        )
    return TokenModelPricing(
        provider_input_per_million_usd=PROVIDER_INPUT_PER_MILLION_USD,
        provider_output_per_million_usd=PROVIDER_OUTPUT_PER_MILLION_USD,
        user_input_per_million_usd=USER_INPUT_PER_MILLION_USD,
        user_output_per_million_usd=USER_OUTPUT_PER_MILLION_USD,
    )


def calculate_token_billing(input_tokens: int, output_tokens: int, model_name: str | None = None) -> TokenBillingBreakdown:
    safe_in = max(int(input_tokens or 0), 0)
    safe_out = max(int(output_tokens or 0), 0)

    pricing = _resolve_token_model_pricing(model_name)
    provider_input_per_token_usd = _per_token(pricing.provider_input_per_million_usd)
    provider_output_per_token_usd = _per_token(pricing.provider_output_per_million_usd)
    user_input_per_token_usd = _per_token(pricing.user_input_per_million_usd)
    user_output_per_token_usd = _per_token(pricing.user_output_per_million_usd)

    provider_cost_usd = (safe_in * provider_input_per_token_usd) + (safe_out * provider_output_per_token_usd)
    user_billable_usd = (safe_in * user_input_per_token_usd) + (safe_out * user_output_per_token_usd)
    credits_exact = user_billable_usd / CREDIT_USD_VALUE
    milli_credits_exact = int(round(credits_exact * MILLI_CREDITS_PER_CREDIT))

    return TokenBillingBreakdown(
        input_tokens=safe_in,
        output_tokens=safe_out,
        provider_cost_usd=provider_cost_usd,
        user_billable_usd=user_billable_usd,
        credits_exact=credits_exact,
        milli_credits_exact=milli_credits_exact,
    )


def calculate_embedding_billing(input_tokens: int) -> EmbeddingBillingBreakdown:
    safe_in = max(int(input_tokens or 0), 0)

    provider_cost_usd = safe_in * _per_token(EMBEDDING_PROVIDER_INPUT_PER_MILLION_USD)
    user_billable_usd = safe_in * _per_token(EMBEDDING_USER_INPUT_PER_MILLION_USD)
    credits_exact = user_billable_usd / CREDIT_USD_VALUE
    milli_credits_exact = int(round(credits_exact * MILLI_CREDITS_PER_CREDIT))

    return EmbeddingBillingBreakdown(
        input_tokens=safe_in,
        provider_cost_usd=provider_cost_usd,
        user_billable_usd=user_billable_usd,
        credits_exact=credits_exact,
        milli_credits_exact=milli_credits_exact,
    )


def credits_to_milli(credits: float | int) -> int:
    return int(round(float(credits) * MILLI_CREDITS_PER_CREDIT))


def milli_to_credits(milli: int | float | None) -> float:
    if milli is None:
        return 0.0
    return float(milli) / float(MILLI_CREDITS_PER_CREDIT)
