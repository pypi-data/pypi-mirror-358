import base64
from construct import Struct, Byte, Int16ub, Int64ub, Enum, Bytes, Int24ub, this, GreedyBytes, GreedyRange
from cryptography import x509
from cryptography.hazmat.backends import default_backend

MerkleTreeHeader = Struct(
	"Version"		 / Byte,
	"MerkleLeafType"  / Byte,
	"Timestamp"	   / Int64ub,
	"LogEntryType"	/ Enum(Int16ub, X509LogEntryType=0, PrecertLogEntryType=1),
	"Entry"		   / GreedyBytes
)

Certificate = Struct(
	"Length" / Int24ub,
	"CertData" / Bytes(this.Length)
)

CertificateChain = Struct(
	"ChainLength" / Int24ub,
	"Chain" / GreedyRange(Certificate),
)

PrecertChainEntry = Struct(
    "Precert"        / Certificate,
    "IssuerKeyHash"  / Bytes(32),  
    "ChainLength"    / Int24ub,           
    "Chain"          / GreedyRange(Certificate),
)

def extract_cert(leaf_input, extra_data):
    """ Extracts the certificated from leaf_input and extra_data from CT logs entry """
    
    raw_leaf = base64.urlsafe_b64decode(leaf_input + "===")
    hdr = MerkleTreeHeader.parse(raw_leaf)

    if hdr.LogEntryType == "X509LogEntryType":
        der = Certificate.parse(hdr.Entry).CertData
    else:
        raw_extra = base64.urlsafe_b64decode(extra_data + "===")
        precert_blob = PrecertChainEntry.parse(raw_extra)
        der = precert_blob.Precert.CertData
        
    cert = x509.load_der_x509_certificate(der, default_backend())
    return cert
