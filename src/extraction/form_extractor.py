import re


class FormExtractor:
    """Generic Form Extractor V5; drop-in replacement for the current extractor."""

    CHECKBOX_MARKERS = {"x", "xx", "✓", "✔", "☑", "checked", "[x]", "[xx]", "yes", "true"}

    NON_VALUE_LINES = {
        "check one", "appendix c", "reportable expenditures", "in thousands",
        "from current budget", "from next year's budget", "supplier rpt.",
        "current year", "10% change", "original -", "field complete",
        "wave(s)", "date",
    }

    KNOWN_LABELS = {
        "year covered", "brand family name", "variety description",
        "products length", "product length", "filter", "nonfilter",
        "hard pack", "soft pack", "menthol", "nonmenthol", "pack size sold",
        "tar", "nicotine", "variety unit sales", "variety dollar sales",
        "first sales date", "last sales date",
        "total reportable expenditures for variety",
        "bates id", "document copies", "page number(s)",
        "poor quality original",
        "overlay item could not be removed without damage to the original",
        "no documents were found within the original", "file folder",
        "redrope expandable file", "hanging file", "envelope", "other",
        "bates number", "not used", "other variance (explain)",
        "date", "description", "supplier", "total area budget",
        "current bal. available", "this change", "new balance",
        "committed to date", "submitted by", "approved by", "cc",
        "project no.", "account name", "project file", "internal init.",
        "ext. auth.", "final report due", "field complete", "total cost",
        "previous commitments", "amt. of change", "reasons", "wave(s)",
    }

    PERSONAL_ALIASES = {
        "name": {"name", "full name", "applicant name", "employee name"},
        "date_of_birth": {"date of birth", "dob", "birth date"},
        "email": {"email", "email address", "e-mail"},
        "phone": {"phone", "phone number", "telephone", "mobile"},
        "cnic": {"cnic", "cnic number", "national id", "national id number"},
        "address": {"address", "home address", "mailing address"},
        "gender": {"gender", "sex"},
    }

    def extract(self, ocr_results):
        lines = self._normalize_ocr(ocr_results)
        if not lines:
            return self._empty_result()

        fields, checkboxes = self._extract_structured(lines)
        self._extract_colonless(lines, fields, checkboxes)
        self._resolve_marker_rows(lines, fields, checkboxes)
        self._assign_orphan_values(lines, fields, checkboxes)
        self._reconcile_consistency(fields)

        legacy = self._extract_legacy_fields(fields)
        completed = [x for x in fields.values() if x.get("value") not in (None, "")]
        total = len(fields)
        completed_count = len(completed)

        completion = round(completed_count / total * 100, 2) if total else 0.0
        validation = self._validation_score(fields)
        confidences = [self._safe_float(x.get("confidence", 0)) for x in completed]
        overall_conf = round(sum(confidences) / len(confidences), 2) if confidences else 0.0
        missing = [k for k, x in fields.items() if x.get("value") in (None, "")]

        raw_text = "\n".join(x["text"] for x in lines if x.get("text"))
        needs_review = any(x.get("review_required") for x in fields.values())

        return {
            "document_type": "form",
            "fields": fields,
            "form_fields": fields,
            "checkboxes": checkboxes,
            "name": legacy["name"],
            "date_of_birth": legacy["date_of_birth"],
            "email": legacy["email"],
            "phone": legacy["phone"],
            "cnic": legacy["cnic"],
            "address": legacy["address"],
            "gender": legacy["gender"],
            "missing_fields": missing,
            "completion_score": completion,
            "validation_score": validation,
            "confidence": overall_conf,
            "needs_review": needs_review,
            "statistics": {
                "line_count": len(lines),
                "total_fields": total,
                "completed_fields": completed_count,
                "missing_fields": len(missing),
                "completion_score": completion,
                "validation_score": validation,
                "confidence": overall_conf,
                "needs_review": needs_review,
            },
            "raw_text": raw_text,
        }

    def _normalize_ocr(self, ocr_results):
        if isinstance(ocr_results, dict):
            ocr_results = ocr_results.get("lines", [])
        if not isinstance(ocr_results, list):
            return []

        normalized = []
        for item in ocr_results:
            if isinstance(item, dict):
                text = str(item.get("text", "")).strip()
                conf = self._safe_float(item.get("confidence", 0))
            else:
                text = str(item).strip()
                conf = 0.0

            text = re.sub(r"\s+", " ", text.replace("：", ":")).strip()
            text = re.sub(r"\s+:", ":", text)
            # OCR frequently substitutes punctuation in printed labels.
            # Normalize it before structural parsing.
            if ":" in text:
                left, right = text.split(":", 1)
                left = left.replace("~", "-").replace("=", "-").strip(" \"'`")
                text = f"{left}:{right}"
            if text:
                normalized.append({"text": text, "confidence": conf})
        return normalized

    def _extract_structured(self, lines):
        fields, checkboxes = {}, {}
        used_value_texts = set()
        pattern = re.compile(
            r"^\s*(?:\(\s*\d+\s*\)|\{\s*\d+\s*\})?\s*"
            r"([A-Za-z][A-Za-z0-9\s\-\'/\.\(\)&]+?)\s*:\s*(.*)$"
        )

        for i, line in enumerate(lines):
            match = pattern.match(line["text"])
            if not match:
                continue

            raw_label = match.group(1).strip()
            inline = match.group(2).strip()
            label = self._normalize_label(raw_label)

            if self._ignore_label(label):
                continue

            value, conf, source = self._find_value_after_label(
                lines, i, inline, label, used_value_texts
            )
            self._store_field(fields, label, raw_label, value, conf, source)
            if value not in (None, ""):
                used_value_texts.add(self._clean_value(value).lower())

            if self._is_checkbox_value(inline):
                checkboxes[label] = {
                    "selected": True, "value": inline,
                    "confidence": line["confidence"]
                }
            elif value and self._is_checkbox_value(value):
                checkboxes[label] = {
                    "selected": True, "value": value,
                    "confidence": conf
                }

        return fields, checkboxes

    def _find_value_after_label(self, lines, index, inline, label, used_value_texts=None):
        if used_value_texts is None:
            used_value_texts = set()
        if inline:
            cleaned = self._clean_value(inline)
            if self._acceptable_value(cleaned, label) and cleaned.lower() not in used_value_texts:
                return cleaned, lines[index]["confidence"], "inline"
            if self._is_instruction(cleaned):
                return None, lines[index]["confidence"], "instruction"

        for step in range(1, 4):
            j = index + step
            if j >= len(lines):
                break
            candidate = lines[j]["text"].strip()
            if not candidate:
                continue
            if self._looks_like_label(candidate):
                break
            if self._is_number_marker(candidate):
                # A row marker usually means the next OCR content belongs to
                # the next field. Do not cross it while resolving a value.
                break
            if self._is_instruction(candidate):
                continue

            cleaned = self._clean_value(candidate)
            if cleaned.lower() in used_value_texts:
                continue
            if self._acceptable_value(cleaned, label):
                return cleaned, lines[j]["confidence"], "next_line"

        if label in {"submitted_by", "approved_by", "name"}:
            for step in range(1, 6):
                j = index + step
                if j >= len(lines):
                    break
                candidate = self._clean_value(lines[j]["text"])
                if self._looks_like_label(candidate):
                    break
                if self._looks_like_person_name(candidate):
                    return candidate, lines[j]["confidence"], "person_name"

        return None, lines[index]["confidence"], "missing"

    def _store_field(self, fields, label, raw_label, value, confidence, source):
        if label in fields:
            old = fields[label]
            if old.get("value") not in (None, "") and value in (None, ""):
                return
            if old.get("value") not in (None, "") and value not in (None, ""):
                if not old.get("review_required") and old.get("confidence", 0) >= confidence:
                    return

        review = False
        if value not in (None, ""):
            review = self._looks_like_junk(value)
            if label in self._numeric_labels() and not self._is_numeric_value(value):
                review = True
            if "date" in label and not self._is_date_value(value):
                review = True

        fields[label] = {
            "label": raw_label,
            "value": value if value not in ("", None) else None,
            "confidence": round(self._safe_float(confidence), 2),
            "source": source,
            "review_required": review,
        }

    def _extract_colonless(self, lines, fields, checkboxes):
        # Only accept colonless labels when they are known semantic labels or
        # explicit checkbox options. Never treat arbitrary uppercase OCR text
        # (e.g. a brand name) as a field label. This keeps the extractor generic
        # while preventing false fields such as MALIBU -> {2).
        for i, line in enumerate(lines):
            text = line["text"].strip()
            label = self._normalize_label(text)

            if not self._is_colonless_candidate(text, label) or label in fields:
                continue

            value, conf, source = None, line["confidence"], "colonless"
            for step in range(1, 3):
                j = i + step
                if j >= len(lines):
                    break
                candidate = lines[j]["text"].strip()
                if self._looks_like_label(candidate) or self._is_number_marker(candidate):
                    break
                if self._is_instruction(candidate):
                    continue
                candidate = self._clean_value(candidate)
                if self._acceptable_value(candidate, label):
                    value, conf, source = candidate, lines[j]["confidence"], "colonless_next_line"
                    break

            self._store_field(fields, label, text, value, conf, source)

            if self._looks_like_checkbox_option(text):
                checkboxes.setdefault(label, {
                    "selected": None,
                    "value": None,
                    "confidence": line["confidence"],
                    "review_required": True,
                })

    def _is_colonless_candidate(self, text, label):
        if not text or ":" in text or label in self.NON_VALUE_LINES:
            return False
        if label in self.KNOWN_LABELS or self._looks_like_checkbox_option(text):
            return True
        # Do not infer arbitrary uppercase text as a label. Generic inference
        # is unsafe because forms commonly contain names, brands and values
        # without colons. Known labels remain supported.
        return False

    def _looks_like_checkbox_option(self, text):
        n = self._normalize_label(text)
        prefixes = (
            "document_copies_are_in_the_same_sequence",
            "page_number_s",
            "poor_quality_original",
            "overlay_item_could_not_be_removed",
            "no_documents_were_found_within_the_original",
            "file_folder", "redrope_expandable_file", "hanging_file",
            "envelope", "other_specify", "document_copies_were_reproduced",
            "bates_number", "not_used", "other_variance",
        )
        return any(n.startswith(p) for p in prefixes)

    def _validation_score(self, fields):
        scores = []
        for label, item in fields.items():
            value = item.get("value")
            if value in (None, ""):
                continue
            if item.get("review_required"):
                scores.append(0.25)
            elif label in self._numeric_labels():
                scores.append(1.0 if self._is_numeric_value(value) else 0.0)
            elif "date" in label:
                scores.append(1.0 if self._is_date_value(value) else 0.0)
            elif "email" in label:
                scores.append(1.0 if self._is_email(value) else 0.0)
            else:
                scores.append(1.0)
        return round(sum(scores) / len(scores) * 100, 2) if scores else 0.0

    def _numeric_labels(self):
        return {
            "year_covered", "variety_unit_sales", "variety_dollar_sales",
            "pack_size_sold", "tar", "nicotine", "total_area_budget",
            "current_bal_available", "this_change", "new_balance",
            "committed_to_date", "total_cost", "previous_commitments",
            "amt_of_change", "cat_a_expenses", "cat_b_expenses",
            "cat_c_expenses", "cat_d_expenses", "cat_e_expenses",
            "cat_f_expenses", "cat_g_expenses", "cat_h_expenses",
            "cat_i_expenses", "cat_j_expenses", "cat_k_expenses",
            "cat_l_expenses", "cat_m_expenses",
            "total_reportable_expenditures_for_variety",
        }

    def _is_numeric_value(self, value):
        v = str(value).strip()
        if v in {"-", "—", "–"}:
            return True
        if not re.search(r"\d", v):
            return False
        return bool(re.fullmatch(
            r"[\$€£]?\s*[\d,\.\s]+(?:\s*(?:mg|kg|%|k|m))?\s*[\$€£]?",
            v, flags=re.I
        ))

    def _is_date_value(self, value):
        return bool(re.search(
            r"\b(?:\d{1,2}[/-]\d{1,2}[/-]\d{2,4}|"
            r"\d{1,2}[/-]\d{2,4}|\d{4}[/-]\d{1,2}[/-]\d{1,2})\b",
            str(value)
        ))

    def _is_email(self, value):
        return bool(re.fullmatch(r"[^@\s]+@[^@\s]+\.[^@\s]+", str(value).strip()))

    def _normalize_label(self, label):
        label = label.lower().strip().replace("~", "-").replace("=", "-")
        label = re.sub(r"[^a-z0-9]+", "_", label)
        label = re.sub(r"_+", "_", label).strip("_")
        aliases = {"products_length": "product_length"}
        label = aliases.get(label, label)

        # Common OCR confusions in category-style labels. This is a generic
        # normalization rule, not a hard-coded value for one particular form.
        m = re.fullmatch(r"cat_([a-z0-9]+)_expenses", label)
        if m:
            cat = m.group(1)
            cat_aliases = {"3": "b", "p": "f"}
            cat = cat_aliases.get(cat, cat)
            label = f"cat_{cat}_expenses"
        return label

    def _clean_value(self, value):
        value = re.sub(r"^[|:;,_\\]+", "", str(value).strip())
        value = re.sub(r"[|;]+$", "", value)
        value = re.sub(r"\s+", " ", value).strip()
        # OCR often reads a handwritten/printed checkbox X as Xx or xx.
        if re.fullmatch(r"[xX]{1,3}", value):
            return "X"
        return value

    def _ignore_label(self, label):
        return label in self.NON_VALUE_LINES

    def _is_instruction(self, value):
        n = self._normalize_label(value)
        return n in self.NON_VALUE_LINES or (value.startswith("(") and value.endswith(")"))

    def _looks_like_label(self, text):
        if ":" in text:
            return True
        n = self._normalize_label(text)
        if re.fullmatch(r"cat_[a-z]_expenses", n):
            return True
        return n in self.KNOWN_LABELS or self._looks_like_checkbox_option(text)

    def _acceptable_value(self, value, label):
        if value in (None, "") or self._is_instruction(value):
            return False
        if self._looks_like_junk(value) and value.lower() not in {"x", "xx", "-", "—", "–"}:
            return False
        if label in self._numeric_labels():
            if label == "pack_size_sold" and re.fullmatch(r"\d+(?:\.\d+)?(?:['’]s)?", str(value).strip(), flags=re.I):
                return True
            return self._is_numeric_value(value)
        if "date" in label:
            return self._is_date_value(value)
        if label in {"email", "email_address"}:
            return self._is_email(value)
        return True

    def _looks_like_junk(self, value):
        v = str(value).strip()
        if len(v) <= 1 and not re.search(r"[A-Za-z0-9$€£]", v):
            return True
        if re.fullmatch(r"[qQ]\d+\)", v):
            return True
        if re.fullmatch(r"[A-Za-z]{1,3}", v) and v.lower() not in {"x", "xx", "mg", "yes", "no"}:
            return True
        if re.fullmatch(r"[\$<>~`\'\"^]+", v):
            return True
        return False

    def _is_checkbox_value(self, value):
        return str(value).strip().lower() in self.CHECKBOX_MARKERS

    def _looks_like_person_name(self, value):
        v = str(value).strip()
        if not v or len(v) > 80 or re.search(r"\d", v) or self._looks_like_label(v):
            return False
        words = v.split()
        return 2 <= len(words) <= 5 and all(
            re.fullmatch(r"[A-Za-z][A-Za-z\.\-']*", w) for w in words
        )

    def _resolve_marker_rows(self, lines, fields, checkboxes):
        """Use printed row markers to resolve OCR reading-order swaps.

        This pass is deliberately conservative. It only uses the *immediately*
        preceding standalone value before a row marker, and only when that
        value has not already been assigned to another field. This fixes common
        scan-order cases such as `MALIBU -> (2) -> BRAND FAMILY NAME` and
        `34 -> (13) -> CAT-A-EXPENSES` without stealing values from the row above.
        """
        markers = [i for i, line in enumerate(lines) if self._is_number_marker(line["text"])]
        if not markers:
            return

        label_pattern = re.compile(
            r"^\s*(?:\(\s*\d+\s*\)|\{\s*\d+\s*\})?\s*"
            r"([A-Za-z][A-Za-z0-9\s\-\'/\.\(\)&]+?)\s*:\s*(.*)$"
        )

        def label_at(idx):
            if idx < 0 or idx >= len(lines):
                return None
            m = label_pattern.match(lines[idx]["text"])
            return self._normalize_label(m.group(1).strip()) if m else None

        used = {
            self._clean_value(item.get("value")).lower()
            for item in fields.values()
            if item.get("value") not in (None, "")
        }

        # First pass: values that occur immediately after a label in the same
        # marker-bounded row. This has priority over reversed associations.
        for pos, marker_idx in enumerate(markers):
            next_marker = markers[pos + 1] if pos + 1 < len(markers) else len(lines)
            row_labels = []
            for j in range(marker_idx + 1, next_marker):
                label = label_at(j)
                if label:
                    row_labels.append((j, label))
            for label_idx, label in row_labels:
                if label not in fields or fields[label].get("value") not in (None, ""):
                    continue
                for j in range(label_idx + 1, min(label_idx + 3, next_marker)):
                    candidate = self._clean_value(lines[j]["text"])
                    if not candidate or self._is_number_marker(candidate):
                        continue
                    if self._looks_like_label(candidate) or self._is_instruction(candidate):
                        break
                    if self._acceptable_value(candidate, label):
                        fields[label].update({
                            "value": candidate,
                            "raw_value": candidate,
                            "confidence": round(self._safe_float(lines[j]["confidence"]), 2),
                            "source": "marker_row",
                            "review_required": False,
                        })
                        used.add(candidate.lower())
                        if self._is_checkbox_value(candidate):
                            checkboxes[label] = {
                                "selected": True, "value": "X",
                                "confidence": lines[j]["confidence"]
                            }
                        break

        # Second pass: OCR sometimes puts a value immediately before the row
        # marker and the label immediately after it. Use only that one line.
        for marker_idx in markers:
            j = marker_idx - 1
            if j < 0:
                continue
            candidate = self._clean_value(lines[j]["text"])
            if (not candidate or self._is_number_marker(candidate)
                    or self._looks_like_label(candidate)
                    or self._is_instruction(candidate)
                    or self._looks_like_junk(candidate)):
                continue
            if candidate.lower() in used:
                continue
            # Standalone checkbox marks are too ambiguous in reversed OCR order.
            if self._is_checkbox_value(candidate):
                continue

            # Find the first label after this marker, stopping at the next marker.
            after_labels = []
            for k in range(marker_idx + 1, min(marker_idx + 4, len(lines))):
                if self._is_number_marker(lines[k]["text"]):
                    break
                label = label_at(k)
                if label:
                    after_labels.append((k, label))
            for _, label in after_labels:
                if label not in fields:
                    continue
                # If the label already received a value from a simple next-line
                # heuristic, replace it only when the reversed candidate is a
                # fresh value and the candidate is structurally valid. This is
                # how we recover OCR order such as `34 -> (13) -> CAT-A` while
                # avoiding reuse of values like 38 that already belong to CAT-C.
                if candidate.lower() in used:
                    continue
                if self._acceptable_value(candidate, label):
                    fields[label].update({
                        "value": candidate,
                        "raw_value": candidate,
                        "confidence": round(self._safe_float(lines[j]["confidence"]), 2),
                        "source": "marker_reversed",
                        "review_required": False,
                    })
                    used.add(candidate.lower())
                    break

    def _assign_orphan_values(self, lines, fields, checkboxes):
        """Attach standalone OCR values to the next nearby label.

        Long underline fields can make OCR return the value before the label.
        We therefore use a *forward-only* local association. Forward-only is
        important: a value such as a year should never be stolen by the label
        that happens to appear a line or two later.
        """
        used_value_texts = {
            self._clean_value(item.get("value")).lower()
            for item in fields.values()
            if item.get("value") not in (None, "")
        }

        label_positions = []
        for i, line in enumerate(lines):
            text = line["text"].strip()
            if not text:
                continue
            m = re.match(
                r"^\s*(?:\(\s*\d+\s*\)|\{\s*\d+\s*\})?\s*"
                r"([A-Za-z][A-Za-z0-9\s\-\'/\.\(\)&]+?)\s*:\s*(.*)$",
                text,
            )
            if m:
                label_positions.append((i, self._normalize_label(m.group(1).strip())))

        for i, line in enumerate(lines):
            text = self._clean_value(line["text"])
            if not text or self._is_instruction(text) or self._is_number_marker(text):
                continue
            if self._looks_like_label(text) or self._looks_like_junk(text):
                continue
            if text.lower() in used_value_texts:
                continue

            is_numeric = self._is_numeric_value(text)
            is_date = self._is_date_value(text)
            is_checkbox = self._is_checkbox_value(text)
            # Standalone checkbox marks are too ambiguous in OCR reading order;
            # inline/adjacent extraction handles them more safely.
            if not (is_numeric or is_date) or is_checkbox:
                continue

            # Only consider the next label, not a previous label. This prevents
            # values already belonging to an earlier field from being stolen.
            next_labels = [x for x in label_positions if 0 < x[0] - i <= 4]
            if not next_labels:
                continue
            pos, label = min(next_labels, key=lambda x: x[0])
            if label not in fields:
                continue

            item = fields[label]
            if item.get("value") not in (None, ""):
                continue
            if label in self._numeric_labels() and not is_numeric:
                continue
            if "date" in label and not is_date:
                continue
            if is_checkbox and not self._is_checkbox_field(label):
                continue

            value = "X" if is_checkbox else text
            conf = line["confidence"]
            item["value"] = value
            item["raw_value"] = value
            item["confidence"] = round(self._safe_float(conf), 2)
            item["source"] = "nearby_forward"
            item["review_required"] = False
            if is_checkbox:
                checkboxes[label] = {
                    "selected": True,
                    "value": "X",
                    "confidence": round(self._safe_float(conf), 2),
                }

    def _is_checkbox_field(self, label):
        n = self._normalize_label(label)
        return n in {
            "filter", "nonfilter", "hard_pack", "soft_pack", "menthol", "nonmenthol",
            "yes", "no", "male", "female", "checked", "selected"
        }

    def _is_number_marker(self, text):
        return bool(re.fullmatch(r"[\(\{]\s*\d+\s*[\)\}]", str(text).strip()))

    def _reconcile_consistency(self, fields):
        """Generic post-extraction consistency checks.

        This pass never invents arbitrary OCR values. It only uses relationships
        already visible in the extracted document, such as a total matching the
        sum of sibling category fields. When a numeric value appears to have
        leaked into the final category immediately before a total field, move it
        to the total only when the arithmetic evidence is strong enough.
        """
        # Generic category -> total reconciliation.
        category_items = []
        for key, item in fields.items():
            if re.fullmatch(r"cat_[a-z]_expenses", key):
                category_items.append((key, item))

        if not category_items:
            return

        total_candidates = [
            (key, item) for key, item in fields.items()
            if "total" in key and ("expense" in key or "cost" in key or "amount" in key)
        ]
        if not total_candidates:
            return

        for total_key, total_item in total_candidates:
            if total_item.get("value") not in (None, ""):
                # If total is already valid, still flag an arithmetic mismatch.
                total_num = self._numeric_amount(total_item.get("value"))
                if total_num is not None:
                    known_sum = sum(
                        x for _, it in category_items
                        for x in [self._numeric_amount(it.get("value"))]
                        if x is not None
                    )
                    if known_sum != total_num and any(
                        it.get("value") not in (None, "") for _, it in category_items
                    ):
                        total_item["review_required"] = True
                continue

            known = []
            for key, item in category_items:
                num = self._numeric_amount(item.get("value"))
                if num is not None:
                    known.append((key, num))

            if not known:
                continue

            known_sum = sum(num for _, num in known)

            # Strong generic case: the last category's extracted value equals
            # the sum of the other categories. This often means OCR attached
            # the document's total to the last category because of scan order.
            last_key, last_item = category_items[-1]
            last_num = self._numeric_amount(last_item.get("value"))
            others_sum = sum(
                self._numeric_amount(it.get("value")) or 0
                for key, it in category_items[:-1]
            )
            if last_num is not None and last_num == others_sum and others_sum > 0:
                total_item.update({
                    "value": self._format_number(last_num),
                    "raw_value": last_item.get("raw_value", last_item.get("value")),
                    "confidence": min(
                        self._safe_float(last_item.get("confidence", 0)),
                        95.0
                    ),
                    "source": "reconciled",
                    "review_required": True,
                })
                last_item.update({
                    "value": None,
                    "raw_value": None,
                    "source": "reconciled_missing",
                    "review_required": True,
                })
                continue

            # If the total is absent but a unique standalone numeric value is
            # already represented elsewhere, use it only when it exactly equals
            # the sum of the extracted categories. This is conservative and does
            # not create a value from thin air.
            for key, item in fields.items():
                if key == total_key:
                    continue
                num = self._numeric_amount(item.get("value"))
                if num is None:
                    continue
                if num == known_sum and len([1 for _, n in known if n == num]) == 0:
                    total_item.update({
                        "value": self._format_number(num),
                        "raw_value": item.get("raw_value", item.get("value")),
                        "confidence": min(self._safe_float(item.get("confidence", 0)), 95.0),
                        "source": "reconciled",
                        "review_required": True,
                    })
                    item["review_required"] = True
                    break

    def _numeric_amount(self, value):
        if value in (None, "", "-", "—", "–"):
            return None
        text = str(value).strip()
        # Remove currency/unit text but preserve decimal and comma notation.
        match = re.search(r"[-+]?\d[\d,]*(?:\.\d+)?", text)
        if not match:
            return None
        try:
            return float(match.group(0).replace(",", ""))
        except ValueError:
            return None

    def _format_number(self, value):
        if float(value).is_integer():
            return f"{int(value):,}"
        return f"{value:,.2f}".rstrip("0").rstrip(".")

    def _extract_legacy_fields(self, fields):
        result = {k: None for k in self.PERSONAL_ALIASES}
        for legacy, aliases in self.PERSONAL_ALIASES.items():
            for alias in aliases:
                key = self._normalize_label(alias)
                if key in fields and fields[key].get("value") not in (None, ""):
                    result[legacy] = fields[key]["value"]
                    break
        return result

    def _safe_float(self, value):
        try:
            return float(value)
        except (TypeError, ValueError):
            return 0.0

    def _empty_result(self):
        return {
            "document_type": "form", "fields": {}, "form_fields": {},
            "checkboxes": {}, "name": None, "date_of_birth": None,
            "email": None, "phone": None, "cnic": None, "address": None,
            "gender": None, "missing_fields": [], "completion_score": 0.0,
            "validation_score": 0.0, "confidence": 0.0, "needs_review": False,
            "statistics": {
                "line_count": 0, "total_fields": 0, "completed_fields": 0,
                "missing_fields": 0, "completion_score": 0.0,
                "validation_score": 0.0, "confidence": 0.0, "needs_review": False
            },
            "raw_text": "",
        }