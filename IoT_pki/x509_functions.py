from cryptography.hazmat.backends import default_backend
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography import x509
from cryptography.x509.oid import NameOID
from cryptography.hazmat.primitives import hashes
import datetime
from django.utils import timezone
from django.conf import settings
import random
import string
import logging
from .models import Certificate

logger = logging.getLogger(__name__)

def generateNewX509(cert_request):
    
    cert_data=prepareCert(cert_request) 
    streamedData=makeCert(cert_data)
    
    return streamedData
    #return "/home/jmm/myCA/certs/myPKIcert.pem"



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

def makeCA(data):
    
    
    id=100
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
        x509.NameAttribute(NameOID.COMMON_NAME, str(id)),
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
    
 

    
def copyAttrOrGetDefault(certificate, key,cert_request):
    #this function is used to copy cert request data to certificate object and if not available get defaults from settings
    try: 
        value=getattr(cert_request,key)
    except:
        #blank value will fail test below to look for default
        value=""
        
    #check also to see if value is blank
    if not value:
        try:
            value=settings.CERT_DEFAULTS[key]
            
        except:
            value="unknown"
    if not value:
        value="unknown"                 
    logger.info("value key%s value %s", key, value)
    setattr(certificate,key, value)
    return certificate
            

def prepareCert(cert_request):
    #copy data from cert_request or certificate ,add default data and save to certificates database
    #used for both New requests and renewals
    
    cert_data=Certificate()
    keys={'country_name','state_or_province_name','locality_name','organization_name','organization_unit_name','email_address','user_id','dns_name','common_name','dn_qualifier'}
    
    for key in keys:
        copyAttrOrGetDefault(cert_data,key,cert_request)
    
    cert_data.not_valid_before=timezone.now()-datetime.timedelta(1,0,0)
    cert_data.not_valid_after=timezone.now()+datetime.timedelta(settings.CERT_DEFAULTS['valid_days'])    
    cert_data.serial_number=x509.random_serial_number()
    logger.info("random serial %s",cert_data.serial_number)
    cert_data.save()
            
    return cert_data


    
    

def makeCert(cert_data):
    #given parameters for cert, returns bytes for certificate (private key and public key)
       
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=2048,
        backend=default_backend()
        )
    public_key = private_key.public_key()
        
    builder = x509.CertificateBuilder()
    builder = builder.subject_name(x509.Name([
        x509.NameAttribute(NameOID.COMMON_NAME, cert_data.common_name),
        x509.NameAttribute(NameOID.COUNTRY_NAME,cert_data.country_name),
        x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME,cert_data.state_or_province_name),
        x509.NameAttribute(NameOID.LOCALITY_NAME,cert_data.locality_name),
        x509.NameAttribute(NameOID.ORGANIZATION_NAME,cert_data.organization_name),
        x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME,cert_data.organization_unit_name),
        x509.NameAttribute(NameOID.USER_ID,cert_data.user_id),
        x509.NameAttribute(NameOID.EMAIL_ADDRESS,cert_data.email_address),
        
        ]))
    builder = builder.issuer_name(loadPEMCert(settings.PKI['path_to_ca_cert']).subject)
    builder = builder.not_valid_before(cert_data.not_valid_before)
    builder = builder.not_valid_after(cert_data.not_valid_after)
    builder = builder.serial_number(cert_data.serial_number)
    builder = builder.public_key(public_key)
    builder = builder.add_extension(
        x509.SubjectAlternativeName(
            [x509.DNSName(cert_data.dns_name)]
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
        
    dataStream=private_key.private_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PrivateFormat.TraditionalOpenSSL,
            encryption_algorithm=serialization.NoEncryption()
            )
    dataStream+=(certificate.public_bytes(serialization.Encoding.PEM))  
    
        
    return dataStream
    
 


def id_generator(size=20, chars=string.ascii_uppercase + string.digits):
    
    return ''.join(random.choice(chars) for _ in range(size))




    


    
    


    
    
    
      