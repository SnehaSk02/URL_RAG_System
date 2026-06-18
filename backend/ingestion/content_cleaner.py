import re

class ContentCleaner:

    def clean(self, text: str) -> str:

        if not text:
            return ""

        # 1. Normalize whitespace and newlines
        text = re.sub(r"\r", "\n", text)
        text = re.sub(r"\t+", " ", text)

        lines = text.splitlines()
        cleaned = []

        noise_patterns = [
            # Navigation & Menus
            r"^(home|menu|navigation|skip to content)$",
            r"^(previous|next)$",
            r"^(previous page|next page)$",
            r"^back to top$",
            # Footer & Legal
            r".*copyright.*",
            r".*all rights reserved.*",
            r".*privacy policy.*",
            r".*terms of service.*",
            r".*cookie.*",
            # Social Media
            r".*share on (facebook|twitter|linkedin|instagram).*",
            r".*follow us on.*",
            # Generic Clutter
            r"^related articles$",
            r"^read more$",
            r"^recommended.*",
            r"^you may also like.*",
            # Breadcrumbs (usually look like Home > Blog > Post)
            r".*\s>\s.*"
        ]

        for line in lines:

            line = line.strip()
            
            # Skip empty lines immediately
            if not line:
                continue

            remove = False

            # Check against noise patterns
            for pattern in noise_patterns:
                if re.match(pattern, line, flags=re.IGNORECASE):
                    remove = True
                    break

            if remove:
                continue

            # --- SAFETY CHECK FOR LISTS ---
            # We want to keep lines that start with numbers (e.g., "1. ", "2) ")
            # But remove standalone page numbers like " 123 " on a line by itself.
            
            # If line is just digits (page number)
            if re.match(r"^\d+$", line):
                # Exception: if it's very short, maybe it's a page number.
                # But if it's "1" or "2" it might be a list item? 
                # Usually list items have text after. A line with just "1" is noise.
                # A line with "1." is NOT matched by ^\d+$                 continue

            # Remove tiny fragments (unless it's a number like "1.")
            # Allow "1.", "A)", "-" but single words like "or" "and" are noise.
                if len(line) < 3 and not re.match(r"^\d+[.)]\s*$", line):
                    continue

            cleaned.append(line)

        # Rejoin text
        text = "\n".join(cleaned)

        # Collapse excessive newlines (but preserve list spacing slightly)
        text = re.sub(r"\n{3,}", "\n\n", text)

        return text.strip()