from .ge_base import GEBaseSequence

class GEBasicSinglePLD(GEBaseSequence):
    @classmethod
    def matches(cls, dicom_header):
        return (
            dicom_header.get("Manufacturer", "").strip().upper() == "GE" and
            dicom_header.get("GESequenceName", "").strip().lower() != "easl"
        )

    def extract_bids_metadata(self):
        bids = self._extract_common_metadata()
        bids.update(self._extract_ge_common_metadata())
        d = self.dicom_header
        if "GELabelingDuration" in d:
            bids["LabelingDuration"] = d["GELabelingDuration"]
        if "InversionTime" in d:
            bids["PostLabelingDelay"] = d["InversionTime"]
        return bids 