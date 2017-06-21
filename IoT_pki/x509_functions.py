from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
import datetime
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def generateNewX509(data):
    
     
    makeCert()
    return "/home/jmm/myCA/certs/myPKIcert.pem"


  


def notUsedgenerateKey():
    key = rsa.generate_private_key(
     public_exponent=65537,
     key_size=2048,
     backend=default_backend()
     )
# Write our key to disk for safe keeping
    with open("/home/jmm/certs/myPKIkey.pem", "wb") as f:
        f.write(key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.TraditionalOpenSSL,
        encryption_algorithm=serialization.BestAvailableEncryption(b"passphrase"),
        ))
    return key
        
        
def notUsedcreateCSR(key):
    # Various details about who we are. For a self-signed certificate the
    # subject and issuer are always the same.
    # Generate a CSR
    csr = x509.CertificateSigningRequestBuilder().subject_name(x509.Name([
    # Provide various details about who we are.
    x509.NameAttribute(NameOID.COUNTRY_NAME, u"US"),
    x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"CA"),
    x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
    x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
    x509.NameAttribute(NameOID.COMMON_NAME, u"mysite.com"),
    ])).add_extension(
    x509.SubjectAlternativeName([
         # Describe what sites we want this certificate for.
        x509.DNSName(u"mysite.com"),
        x509.DNSName(u"www.mysite.com"),
        x509.DNSName(u"subdomain.mysite.com"),
        ]),
        critical=False,
 # Sign the CSR with our private key.
    ).sign(key, hashes.SHA256(), default_backend())
# Write our CSR out to disk.
    with open("/home/jmm/myCA/certs/myPKIcert.pem", "wb") as f:
        f.write(csr.public_bytes(serialization.Encoding.PEM))
    return csr



def notUsedsignCSR(csr,CA):
    
    
    myCsr = x509.load_pem_x509_csr(csr, default_backend())
    

def loadPEMCert(pathToCert):
    with open(pathToCert, 'rb') as f:
        crt_data = f.read()
        cert=x509.load_pem_x509_certificate(crt_data,default_backend())
        return cert
        

def loadPEMKey(pathToKey):
    with open(pathToKey, "rb") as key_file:
        private_key = serialization.load_pem_private_key(
        key_file.read(),
        password=None,
        backend=default_backend()
        )
    return private_key           

def makeCA(id):
    
    valid_days= datetime.timedelta(10000,0,0)    
    one_day = datetime.timedelta(1, 0, 0)
    logger.warning('creating private key')
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
        backend=default_backend()
        )
    #write private key to file
    with open(keyStorePath(id), "wb") as f:
        f.write (private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
            ))
    public_key = private_key.public_key()
    builder = x509.CertificateBuilder()
    subject=x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, u'cryptography.io'),
        x509.NameAttribute(NameOID.COUNTRY_NAME, u'US'),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
        ])
    
    builder = builder.subject_name(subject)
    builder = builder.issuer_name(subject)
    builder = builder.not_valid_before(datetime.datetime.today() - one_day)
    builder = builder.not_valid_after(datetime.datetime.today()+valid_days)
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.public_key(public_key)
    builder = builder.add_extension(
        x509.SubjectAlternativeName(
            [x509.DNSName(u'cryptography.io')]
            ),
            critical=False
        )
    builder = builder.add_extension(
        x509.BasicConstraints(ca=True, path_length=0), critical=True,
        )
    builder = builder.add_extension(x509.KeyUsage(digital_signature=True,content_commitment=True,key_encipherment=True,key_agreement=False,data_encipherment=False,crl_sign=True,encipher_only=False,decipher_only=False,key_cert_sign=True),critical=True) 
    
    certificate = builder.sign(
        private_key=private_key, algorithm=hashes.SHA256(),
        backend=default_backend()
        )
    #write certificate to pem file
    with open(certStorePath(id), "wb") as f:
        
        f.write(certificate.public_bytes(serialization.Encoding.PEM))
        
    return certStorePath(id)
    
 
def certStorePath(id):
    return settings.PKI['path_to_certstore']+str(id)+".pem"

def keyStorePath(id):
    return settings.PKI['path_to_keystore']+str(id)+".key"
    
        

def makeCert(clientID=600):
    
      
    valid_days= datetime.timedelta(settings.PKI['valid_days'],0,0)    
    one_day = datetime.timedelta(1, 0, 0)
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
        )
    public_key = private_key.public_key()
    
    
    
    
    
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, str(clientID)),
        x509.NameAttribute(NameOID.COUNTRY_NAME, u'US'),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"CA"),
        x509.NameAttribute(NameOID.LOCALITY_NAME, u"San Francisco"),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"My Company"),
        ]))
    builder = builder.issuer_name(loadPEMCert(settings.PKI['path_to_ca_cert']).subject)
    builder = builder.not_valid_before(datetime.datetime.today() - one_day)
    builder = builder.not_valid_after(datetime.datetime.today()+valid_days)
    builder = builder.serial_number(x509.random_serial_number())
    builder = builder.public_key(public_key)
    builder = builder.add_extension(
        x509.SubjectAlternativeName(
            [x509.DNSName(u'cryptography.io')]
            ),
            critical=False
        )
    builder = builder.add_extension(
        x509.BasicConstraints(ca=False, path_length=None), critical=True,
        )
    builder = builder.add_extension(x509.KeyUsage(digital_signature=True,content_commitment=True,key_encipherment=True,key_agreement=False,data_encipherment=False,crl_sign=False,encipher_only=False,decipher_only=False,key_cert_sign=False),critical=True) 
    
    certificate = builder.sign(
        private_key=loadPEMKey(settings.PKI['path_to_ca_key']), algorithm=hashes.SHA256(),
        backend=default_backend()
        )
    #write both private key and certificate to pem file
    with open("/home/jmm/myCA/certs/myPKIcert.pem", "wb") as f:
        f.write (private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
            ))
        f.write(certificate.public_bytes(serialization.Encoding.PEM))
        
    return certificate
    
 






    


    
    


    
    
    
      