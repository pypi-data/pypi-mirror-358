from .ge import GEBasicSinglePLD, GEMultiPLD

SEQUENCE_CLASSES = [GEBasicSinglePLD, GEMultiPLD]

def get_asl_sequence(dicom_header: dict):
    for cls in SEQUENCE_CLASSES:
        if cls.matches(dicom_header):
            return cls(dicom_header)
    raise ValueError("No matching ASL sequence class found for this DICOM header.") 