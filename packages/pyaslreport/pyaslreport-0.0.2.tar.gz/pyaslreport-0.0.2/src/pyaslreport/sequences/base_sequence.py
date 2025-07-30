from abc import ABC, abstractmethod
import os
from pyaslreport.io.writers import JSONWriter, TsvWriter
from pyaslreport.io.readers import NiftiReader
from pyaslreport.converters import DICOM2NiFTIConverter

class ASLSequenceBase(ABC):
    def __init__(self, dicom_header: dict):
        self.dicom_header = dicom_header

    @classmethod
    @abstractmethod
    def matches(cls, dicom_header: dict) -> bool:
        """Return True if this class can handle the given DICOM header."""
        pass

    @abstractmethod
    def extract_bids_metadata(self) -> dict:
        """Extract and convert DICOM metadata to BIDS fields."""
        pass

    @abstractmethod
    def generate_asl_context(self, nifti_path: str):
        """
        Generate the ASL context for the sequence.
        """
        pass

    def _extract_common_metadata(self) -> dict:
        """Extract and convert common DICOM metadata fields to BIDS fields, including ms->s conversion where needed."""
        d = self.dicom_header
        
        bids = {}

        # Direct mappings
        for dicom_key, bids_key in [
            ("Manufacturer", "Manufacturer"),
            ("ManufacturersModelName", "ManufacturersModelName"),
            ("SoftwareVersions", "SoftwareVersions"),
            ("MagneticFieldStrength", "MagneticFieldStrength"),
            ("MRAcquisitionType", "MRAcquisitionType"),
            ("FlipAngle", "FlipAngle"),
        ]:
            if dicom_key in d:
                bids[bids_key] = d[dicom_key]

        # ms->s conversion for EchoTime (can be array)
        if "EchoTime" in d:
            et = d["EchoTime"]
            if isinstance(et, (list, tuple)):
                bids["EchoTime"] = [v / 1000.0 for v in et]
            else:
                bids["EchoTime"] = et / 1000.0

        # ms->s conversion for RepetitionTimePreparation
        if "RepetitionTime" in d:
            bids["RepetitionTimePreparation"] = d["RepetitionTime"] / 1000.0

        return bids 


   
    def convert_to_bids(self, dicom_dir: str, output_dir: str, bids_basename: str = "sub-01_asl", overwrite: bool = False):
        """
        Orchestrate the conversion from DICOM series to BIDS (NIfTI, JSON, TSV).
        """
        
        # 1. Convert DICOM to NIfTI
        nifti_path = DICOM2NiFTIConverter.dir_to_nifti(dicom_dir, output_dir, bids_basename, overwrite)

        # 2. Extract metadata and write JSON
        metadata = self.extract_bids_metadata()
        JSONWriter.write(metadata, os.path.join(output_dir, f"{bids_basename}.json"))

        # 3. Generate aslcontext.tsv
        context = self.generate_asl_context(nifti_path)
        TsvWriter.write(context, os.path.join(output_dir, f"{bids_basename}_aslcontext.tsv"))

        return {
            "nifti": nifti_path,
            "json": os.path.join(output_dir, f"{bids_basename}.json"),
            "aslcontext": os.path.join(output_dir, f"{bids_basename}_aslcontext.tsv"),
        }