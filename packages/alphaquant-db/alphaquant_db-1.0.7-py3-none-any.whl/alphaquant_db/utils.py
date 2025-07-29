from datetime import datetime

class DBUtils:
    def __init__():
        pass

    @staticmethod
    def _build_date_map(entries: list[dict]) -> dict:
        return {
            (
                entry["report_date"].isoformat()
                if isinstance(entry["report_date"], datetime)
                else entry["report_date"]
            ): entry
            for entry in entries
            if "report_date" in entry if entry["report_date"] is not None
        }
    
    @staticmethod
    def _merge_financials_by_date(
        primary: list[dict], 
        secondary: list[dict], 
        skip_zeros: bool = False
    ) -> list[dict]:
        """
        Merge two financial entry lists by date, preferring 'primary' over 'secondary' when both exist.
        
        Args:
            primary: Preferred financial entries (e.g., consolidated).
            secondary: Backup financial entries (e.g., standalone).
            skip_zeros: If True, skip entries with sales=0.
        
        Returns:
            A merged, date-sorted list of financial entries.
        """
        primary_map = DBUtils._build_date_map(primary)
        secondary_map = DBUtils._build_date_map(secondary)

        all_dates = sorted(set(primary_map) | set(secondary_map), reverse=True)
        merged = []

        for date in all_dates:
            primary_entry = primary_map.get(date)
            secondary_entry = secondary_map.get(date)

            primary_sales = primary_entry.get("sales") if primary_entry else None
            secondary_sales = secondary_entry.get("sales") if secondary_entry else None

            if primary_entry and primary_sales not in [0, None]:
                merged.append(primary_entry)
            elif secondary_entry and secondary_sales not in [0, None]:
                merged.append(secondary_entry)
            else:
                if skip_zeros:
                    continue
                merged.append(primary_entry if primary_entry else secondary_entry)

        return merged

    
    @staticmethod
    def _get_nested(doc: dict, dotted_key: str, default=None):
        keys = dotted_key.split(".")
        for key in keys:
            doc = doc.get(key)
            if doc is None:
                return default
        return doc
