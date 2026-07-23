"""Synchronous Groq integration boundary for structured complaint AI."""

from __future__ import annotations

import json
import re
import time
from typing import Any

from groq import Groq

from app.core.config import Settings
from app.utils.prompts import EXTRACTION_SYSTEM_PROMPT, RISK_ASSESSMENT_SYSTEM_PROMPT

INVALID_HEADING_VALUES = {
    "customer complaint report",
    "incident intake form",
    "complaint form",
    "qa intake sheet",
    "header",
    "incident report",
    "customer complaint",
    "complaint report",
}


def _sanitize_field_value(value: object) -> str:
    if not value or not isinstance(value, str):
        return ""
    cleaned = value.strip()
    if cleaned.lower() in INVALID_HEADING_VALUES:
        return ""
    return cleaned


def _extract_regex_fallback(raw_text: str, keywords: list[str]) -> str:
    for kw in keywords:
        pattern = re.compile(rf"{kw}[:\s]+([A-Za-z0-9\s/,\.-]{{3,40}})", re.IGNORECASE)
        match = pattern.search(raw_text)
        if match:
            val = match.group(1).strip()
            val = re.split(r"[\n\r]", val)[0].strip()
            val = _sanitize_field_value(val)
            if val:
                return val
    return ""


def _infer_dosage_unit(product_name: str, description: str) -> str:
    text = (product_name + " " + description).lower()
    if "tablet" in text:
        return "tablets"
    if "capsule" in text:
        return "capsules"
    if "injection" in text or "vial" in text:
        return "vial"
    if "syrup" in text or "liquid" in text or "suspension" in text:
        return "ml"
    return ""


def _infer_product_type(product_name: str, description: str, dosage_unit: str) -> str:
    text = (product_name + " " + description + " " + dosage_unit).lower()
    if any(k in text for k in ["api", "raw material", "bulk powder", "kilogram", "drum"]):
        return "API"
    return "FDF"


def _infer_impacted_material(description: str, category: str) -> str:
    text = (description + " " + category).lower()
    if "blister" in text or "tablet" in text or "capsule" in text:
        return "Primary Blister Packaging"
    if "bottle" in text or "leak" in text:
        return "Bottle"
    if "label" in text or "print" in text or "misprint" in text:
        return "Label"
    return "Packaging"


class GroqService:
    """Own Groq client construction and structured complaint calls."""

    def __init__(self, application_settings: Settings) -> None:
        self.settings = application_settings
        self._client = Groq(api_key=self.settings.groq_api_key) if self.is_configured() else None

    def is_configured(self) -> bool:
        """Report whether a Groq key is available without making a network call."""
        return bool(self.settings.groq_api_key)

    def extract_complaint_fields(self, raw_text: str, current_form_state: dict) -> dict:
        """Extract explicitly supplied complaint fields from source text with validation."""
        payload = {"raw_complaint_text": raw_text, "current_form_state": current_form_state}
        result = self._complete(EXTRACTION_SYSTEM_PROMPT, payload, self.settings.model_name)
        return self._validate_and_enrich_extraction(raw_text, result)

    def _validate_and_enrich_extraction(self, raw_text: str, result: dict) -> dict:
        """Enforce validation rules, re-extract missing fields, and infer missing values."""
        updated_fields = result.get("updated_fields", {})
        if not isinstance(updated_fields, dict):
            updated_fields = {}

        # 1. Sanitize all field values against document titles/headings
        for field, value in list(updated_fields.items()):
            updated_fields[field] = _sanitize_field_value(value)

        # 2. Manufacturing site / Originating site mapping & fallback
        mfg_site_fallback = _extract_regex_fallback(raw_text, ["Manufacturing Site", "Manufactured at", "Plant Location", "Manufacturing Plant"])
        if mfg_site_fallback:
            updated_fields["manufacturing_site"] = mfg_site_fallback
            updated_fields["originating_site"] = mfg_site_fallback
        else:
            site = updated_fields.get("manufacturing_site") or updated_fields.get("originating_site")
            if not site or site == updated_fields.get("customer_name"):
                site = _extract_regex_fallback(raw_text, ["Facility", "Site", "Plant"])
            if site:
                updated_fields["originating_site"] = site
                updated_fields["manufacturing_site"] = site

        # 3. Manufacturing Date validation & fallback
        if not updated_fields.get("manufacturing_date"):
            mfg_date = _extract_regex_fallback(raw_text, ["Manufacturing Date", "Mfg Date", "Mfg. Date", "Manufactured On", "Mfg"])
            if mfg_date:
                updated_fields["manufacturing_date"] = mfg_date

        # 4. Expiry Date validation & fallback
        if not updated_fields.get("expiry_date"):
            exp_date = _extract_regex_fallback(raw_text, ["Expiry Date", "Exp Date", "Exp. Date", "Expires On", "Exp"])
            if exp_date:
                updated_fields["expiry_date"] = exp_date

        # 5. Product Name fallback
        if not updated_fields.get("product_name"):
            prod = _extract_regex_fallback(raw_text, ["Product Name", "Product", "Drug Name"])
            if prod:
                updated_fields["product_name"] = prod

        # 6. Batch Number fallback
        if not updated_fields.get("batch_number") and not updated_fields.get("batch_lot_number"):
            batch = _extract_regex_fallback(raw_text, ["Batch Number", "Batch No", "Batch / lot number", "Lot Number", "Batch"])
            if batch:
                updated_fields["batch_number"] = batch
                updated_fields["batch_lot_number"] = batch

        # 7. Dosage Unit Inferencing
        prod_name = updated_fields.get("product_name", "")
        desc = updated_fields.get("complaint_description", raw_text)
        if not updated_fields.get("dosage_unit") and prod_name:
            inferred_unit = _infer_dosage_unit(prod_name, desc)
            if inferred_unit:
                updated_fields["dosage_unit"] = inferred_unit

        # 8. Product Type Inferencing (FDF vs API)
        unit = updated_fields.get("dosage_unit", "")
        if not updated_fields.get("product_type") and prod_name:
            updated_fields["product_type"] = _infer_product_type(prod_name, desc, unit)

        # 9. Impacted Material Inferencing
        cat = updated_fields.get("complaint_category", "")
        if not updated_fields.get("impacted_material") and (prod_name or cat or updated_fields.get("complaint_description")):
            updated_fields["impacted_material"] = _infer_impacted_material(desc, cat)

        # 10. AI Generated fields fallback defaults
        if not updated_fields.get("severity") and updated_fields.get("complaint_description"):
            updated_fields["severity"] = "Major" if "critical" not in desc.lower() else "Critical"
        if not updated_fields.get("capa_priority") and updated_fields.get("severity"):
            updated_fields["capa_priority"] = "High" if updated_fields.get("severity") in ["Critical", "Major"] else "Medium"

        result["updated_fields"] = updated_fields
        return result

    def assess_risk(self, fields: dict) -> dict:
        """Assess complaint risk using the reasoning-oriented Groq model."""
        return self._complete(RISK_ASSESSMENT_SYSTEM_PROMPT, fields, "llama-3.3-70b-versatile")

    def _complete(self, system_prompt: str, user_payload: Any, model: str) -> dict:
        if self._client is None:
            raise RuntimeError("GROQ_API_KEY is not configured")

        last_error: Exception | None = None
        for attempt in range(2):
            try:
                response = self._client.chat.completions.create(
                    model=model,
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": json.dumps(user_payload, default=str)},
                    ],
                    temperature=0,
                    response_format={"type": "json_object"},
                )
                content = response.choices[0].message.content or ""
                try:
                    return self._parse_json(content)
                except json.JSONDecodeError as exc:
                    if attempt == 0:
                        continue
                    raise RuntimeError("Groq returned invalid JSON after one retry") from exc
            except RuntimeError:
                raise
            except Exception as exc:
                last_error = exc
                if attempt == 0:
                    time.sleep(0.25)
                    continue
                raise RuntimeError("Groq request failed after one retry") from exc

        raise RuntimeError("Groq request failed") from last_error

    @staticmethod
    def _parse_json(content: str) -> dict:
        cleaned = content.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.removeprefix("```json").removeprefix("```").strip()
            cleaned = cleaned.removesuffix("```").strip()
        parsed = json.loads(cleaned)
        if not isinstance(parsed, dict):
            raise json.JSONDecodeError("Expected a JSON object", cleaned, 0)
        return parsed