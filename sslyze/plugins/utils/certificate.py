from nassl.x509_certificate import X509Certificate
from typing import Dict


class Certificate(object):
    """Pick-able object for storing information contained within an nassl.X509Certificate.

    This is needed because we cannot directly send an X509Certificate to a different process (which would happen during
    a scan) as it is not pickable.
     """

    @classmethod
    def from_nassl(cls, nassl_x509_certificate):
        # type: (X509Certificate) -> Certificate

        cert_dict = nassl_x509_certificate.as_dict()
        for key, value in cert_dict.items():
            if 'subjectPublicKeyInfo' in key:
                # Remove the bit suffix so the element is just a number for the key size
                if 'publicKeySize' in value.keys():
                    value['publicKeySize'] = value['publicKeySize'].split(' bit')[0]

        return cls(nassl_x509_certificate.as_pem().strip(),
                   nassl_x509_certificate.as_text(),
                   cert_dict,
                   nassl_x509_certificate.get_SHA1_fingerprint(),
                   nassl_x509_certificate.get_hpkp_pin())

    @classmethod
    def from_pem(cls, pem_cert):
        # type: (unicode) -> Certificate
        # Somewhat convoluted
        return cls.from_nassl(X509Certificate.from_pem(pem_cert))

    def __init__(self, as_pem, as_text, as_dict, sha1_fingerprint, hpkp_pin):
        # type: (unicode, unicode, Dict, unicode, unicode) -> None
        self.as_pem = as_pem
        self.as_text = as_text
        self.as_dict = as_dict
        self.sha1_fingerprint = sha1_fingerprint
        self.hpkp_pin = hpkp_pin

    def __eq__(self, other):
        return isinstance(other, self.__class__) and self.as_pem == other.as_pem

    def __ne__(self, other):
        return not self.__eq__(other)

    def __hash__(self):
        return hash(self.as_pem)

    @property
    def printable_subject_name(self):
        try:
            # Extract the CN if there's one
            cert_name = self.as_dict['subject']['commonName']
        except KeyError:
            # If no common name, display the organizational unit instead
            try:
                cert_name = self.as_dict['subject']['organizationalUnitName']
            except KeyError:
                # Give up
                cert_name = u'No Common Name'
        return cert_name

    @property
    def printable_issuer_name(self):
        try:
            # Extract the CN from the issuer if there's one
            issuer_name = self.as_dict['subject']['commonName']
        except KeyError:
            # Otherwise show the whole Issuer field
            issuer_name = u' - '.join([u'{}: {}'.format(key, value) for key, value in self.as_dict['issuer'].items()])

        return issuer_name
