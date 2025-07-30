from .ge_base import GEBaseSequence
import math

class GEMultiPLD(GEBaseSequence):
    @classmethod
    def matches(cls, dicom_header):
        return (
            dicom_header.get("Manufacturer", "").strip().upper() == "GE" and
            dicom_header.get("GESequenceName", "").strip().lower() == "easl"
        )

    def extract_bids_metadata(self):
        bids = self._extract_common_metadata()
        bids.update(self._extract_ge_common_metadata())
        d = self.dicom_header
        # eASL-specific tags
        for dicom_key, bids_key in [
            ("GEPrivateCV4", "GEPrivateCV4"),
            ("GEPrivateCV5", "GEPrivateCV5"),
            ("GEPrivateCV6", "GEPrivateCV6"),
            ("GEPrivateCV7", "GEPrivateCV7"),
            ("GEPrivateCV8", "GEPrivateCV8"),
            ("GEPrivateCV9", "GEPrivateCV9"),
        ]:
            if dicom_key in d:
                bids[bids_key] = d[dicom_key]

        # ArterialSpinLabelingType is always 'PCASL'
        bids["ArterialSpinLabelingType"] = "PCASL"

        # Calculate LabelingDuration and PostLabelingDelay arrays
        npld = d.get("GEPrivateCV6")
        if npld is not None:
            try:
                npld = int(npld)
            except Exception:
                npld = None
        if npld == 1:
            # Single-PLD
            bids["LabelingDuration"] = d.get("GEPrivateCV5")
            bids["PostLabelingDelay"] = d.get("GEPrivateCV4")
        elif npld and npld > 1:
            # Multi-PLD
            cv4 = float(d.get("GEPrivateCV4", 0))
            cv5 = float(d.get("GEPrivateCV5", 0))
            cv7 = float(d.get("GEPrivateCV7", 1))
            magnetic_field_strength = float(d.get("MagneticFieldStrength", 3))
            
            # T1 for blood
            T1 = 1.65 if magnetic_field_strength == 3 else 1.4
            LD_lin = [cv5 / npld] * npld
            PLD_lin = [cv4 + i * LD_lin[0] for i in range(npld)]
            LD_exp = []
            PLD_exp = [cv4]
            Starget = npld * (1 - math.exp(-cv5 / T1)) * math.exp(-cv4 / T1)
            for i in range(npld):
                if i == 0:
                    LD_exp.append(-T1 * math.log(1 - Starget * math.exp(PLD_exp[0] / T1)))
                else:
                    PLD_exp.append(PLD_exp[i-1] + LD_exp[i-1])
                    LD_exp.append(-T1 * math.log(1 - Starget * math.exp(PLD_exp[i] / T1)))
            if cv7 == 1:
                bids["LabelingDuration"] = LD_lin
                bids["PostLabelingDelay"] = PLD_lin
            elif cv7 == 0:
                bids["LabelingDuration"] = LD_exp
                bids["PostLabelingDelay"] = PLD_exp
            else:
                # Linear combination
                bids["LabelingDuration"] = [ld_lin * cv7 + ld_exp * (1 - cv7) for ld_lin, ld_exp in zip(LD_lin, LD_exp)]
                bids["PostLabelingDelay"] = [pld_lin * cv7 + pld_exp * (1 - cv7) for pld_lin, pld_exp in zip(PLD_lin, PLD_exp)]
        # ASLcontext: all deltaM, last one is m0scan
        bids["ASLContext"] = ["deltaM"] * (npld - 1) + ["m0scan"] if npld and npld > 1 else ["deltaM", "m0scan"]
        return bids 