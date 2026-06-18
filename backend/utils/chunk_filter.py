import re


class ChunkFilter:

    @staticmethod
    def is_low_quality(
        text: str
    ) -> bool:

        if not text:
            return True

        words = text.split()

        # Too small
        if len(words) < 20:
            return True

        # Mostly symbols/numbers
        alpha_chars = sum(
            c.isalpha()
            for c in text
        )

        ratio = alpha_chars / max(
            len(text),
            1
        )

        if ratio < 0.5:
            return True

        # TOC-like chunks

        toc_patterns = [

            r"modules\s*-\s*\d+",

            r"classes\s*-\s*\d+",

            r"appendix",

            r"table of contents",

            r"brief tour",

            r"interactive input editing"
        ]

        text_lower = text.lower()

        for pattern in toc_patterns:

            if re.search(
                pattern,
                text_lower
            ):
                return True

        return False