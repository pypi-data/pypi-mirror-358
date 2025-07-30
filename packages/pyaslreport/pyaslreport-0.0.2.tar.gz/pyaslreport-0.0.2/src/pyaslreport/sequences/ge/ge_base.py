from pyaslreport.sequences.base_sequence import ASLSequenceBase

class GEBaseSequence(ASLSequenceBase):
    def _extract_ge_common_metadata(self) -> dict:
        d = self.dicom_header
        bids = {}
        # Direct GE-specific mappings
        if "AssetRFactor" in d:
            bids["AssetRFactor"] = d["AssetRFactor"]
        if "EffectiveEchoSpacing" in d:
            bids["EffectiveEchoSpacing"] = d["EffectiveEchoSpacing"]
        if "AcquisitionMatrix" in d:
            bids["AcquisitionMatrix"] = d["AcquisitionMatrix"]
        if "NumberOfExcitations" in d:
            bids["TotalAcquiredPairs"] = d["NumberOfExcitations"]
            
        # Derived fields
        # EffectiveEchoSpacing = EffectiveEchoSpacing * AssetRFactor * 1e-6
        if "EffectiveEchoSpacing" in d and "AssetRFactor" in d:
            try:
                eff_echo = float(d["EffectiveEchoSpacing"])
                asset = float(d["AssetRFactor"])
                bids["EffectiveEchoSpacing"] = eff_echo * asset * 1e-6
            except Exception:
                pass

        # TotalReadoutTime = (AcquisitionMatrix[0] - 1) * EffectiveEchoSpacing
        if (
            "AcquisitionMatrix" in d and
            isinstance(d["AcquisitionMatrix"], (list, tuple)) and
            len(d["AcquisitionMatrix"]) > 0 and
            "EffectiveEchoSpacing" in bids
        ):
            try:
                acq_matrix = d["AcquisitionMatrix"][0]
                eff_echo = bids["EffectiveEchoSpacing"]
                bids["TotalReadoutTime"] = (acq_matrix - 1) * eff_echo
            except Exception:
                pass
        
        # MRAcquisitionType default is 3D if not present
        if "MRAcquisitionType" in d:
            bids["MRAcquisitionType"] = d["MRAcquisitionType"]
        else:
            bids["MRAcquisitionType"] = "3D"

        # PulseSequenceType default is spiral if not present
        if "PulseSequenceType" in d:
            bids["PulseSequenceType"] = d["PulseSequenceType"]
        else:
            bids["PulseSequenceType"] = "spiral"

        return bids
