"""Main module."""

# from peewee import AutoField
from peewee import SqliteDatabase, Field, Model, CharField, TextField, IntegerField, FloatField, ForeignKeyField, DateField, DatabaseProxy, PostgresqlDatabase, ProgrammingError
from os import environ
from itertools import chain
from contextlib import contextmanager
from datetime import timedelta
from pathlib import Path
from sys import stderr

import logging

# from . import __version__


database_proxy = DatabaseProxy()
# database = MssqlDatabase('ORDSS_FACTS_GIMS', host=environ.get("DATONIUS_DB", 'csvcesrv014.fda.gov'), user=environ.get("DATONIUS_USER") or input("Enter username credential for Datonius DB:"), password=environ.get("DATONIUS_PASS") or input("Enter password:"))


class pseudoconstant:

    "Like, a 'row-enum'"

    def __init__(self, prop):
        self.prop = prop

    def __get__(self, obj, owner):
        return self.prop(owner)

class TimedeltaField(Field):
    field_type = "integer"

    def db_value(self, value):
        return value.days

    def python_value(self, value):
        if value is not None:
            return timedelta(days=value)
        return None

class BaseModel(Model):
    class Meta:
        database = database_proxy
        # schema = 'dbo'

class Country(BaseModel):
    # id = AutoField(column_name='Id')
    iso = CharField(column_name='Iso')
    iso3 = CharField(column_name='Iso3', null=True)
    name = CharField(column_name='Name', null=True)
    num_code = IntegerField(column_name='NumCode', null=True)
    phone_code = CharField(column_name='PhoneCode', null=True)

    class Meta:
        table_name = 'Countries'

    @pseudoconstant
    def USA(cls):
        return cls.get_or_create(
            iso="US",
            iso3="USA",
            name="United States of America (the)",
            num_code=840,
            phone_code=1
        )[0]
    
    @pseudoconstant
    def UK(cls):
        return cls.get_or_create(
            iso="GB",
            iso3="GBR",
            name="United Kingdom of Great Britain and Northern Ireland (the)",
            num_code=826
        )[0]
    
    @pseudoconstant
    def SOUTHKOREA(cls):
        return cls.get_or_create(
            iso="KR",
            iso3="KOR",
            name="Korea (the Republic of)",
            num_code=410
        )[0]
    
    @pseudoconstant
    def TAIWAN(cls):
        return cls.get_or_create(
            iso="TW",
            iso3="TWN",
            name="Taiwan (Republic of China)",
            num_code=158
        )

    @pseudoconstant
    def VIETNAM(cls):
        return cls.get_or_create(
            iso="VN",
            iso3="VNM",
            name="Viet Nam",
            num_code=704
        )

    @classmethod
    def of(cls, name):
        if name:
            return cls.get_or_create(name=name)[0] # return only the value, we don't care if we had to create it

    

# class LoadOrdssGims(BaseModel):
#     biosample_acc = CharField(column_name='Biosample_acc')
#     collection_date = DateField(column_name='Collection_Date')
#     collection_method = TextField(column_name='Collection_Method', null=True)
#     collection_remarks = TextField(column_name='Collection_Remarks', null=True)
#     consignee_fei = CharField(column_name='Consignee_FEI', null=True)
#     consignee_full_address = CharField(column_name='Consignee_Full_Address', null=True)
#     consignee_name = CharField(column_name='Consignee_Name', null=True)
#     fda_accession = CharField(column_name='FDA_Accession')
#     firm_city = CharField(column_name='Firm_City', null=True)
#     firm_country = CharField(column_name='Firm_Country', null=True)
#     firm_fei = CharField(column_name='Firm_FEI', null=True)
#     firm_full_address = CharField(column_name='Firm_Full_Address', null=True)
#     firm_legal_name = CharField(column_name='Firm_Legal_Name', null=True)
#     firm_line1_address = CharField(column_name='Firm_Line1_Address', null=True)
#     firm_line_2_address = CharField(column_name='Firm_Line_2_Address', null=True)
#     firm_mail_code = CharField(column_name='Firm_Mail_Code', null=True)
#     firm_state = CharField(column_name='Firm_State', null=True)
#     firm_type = CharField(column_name='Firm_Type', null=True)
#     firm_zip = CharField(column_name='Firm_Zip', null=True)
#     importer_fei = CharField(column_name='Importer_FEI', null=True)
#     importer_full_address = CharField(column_name='Importer_Full_Address', null=True)
#     importer_name = CharField(column_name='Importer_Name', null=True)
#     manufacturer_fei = CharField(column_name='Manufacturer_FEI', null=True)
#     manufacturer_full_address = CharField(column_name='Manufacturer_Full_Address', null=True)
#     manufacturer_name = CharField(column_name='Manufacturer_Name', null=True)
#     name_id = IntegerField(column_name='Name_ID')
#     ontologies = CharField(column_name='Ontologies', null=True)
#     organism_full_name = CharField(column_name='Organism_full_name')
#     product_description = CharField(column_name='Product_Description', null=True)
#     reason_for_collection = CharField(column_name='Reason_for_Collection', null=True)
#     responsible_firm_city = CharField(column_name='Responsible_Firm_City', null=True)
#     responsible_firm_country = CharField(column_name='Responsible_Firm_Country', null=True)
#     responsible_firm_fei = CharField(column_name='Responsible_Firm_FEI', null=True)
#     responsible_firm_full_address = CharField(column_name='Responsible_Firm_Full_Address', null=True)
#     responsible_firm_legal_name = CharField(column_name='Responsible_Firm_Legal_Name', null=True)
#     responsible_firm_line_1_adrs = CharField(column_name='Responsible_Firm_Line_1_Adrs', null=True)
#     responsible_firm_line_2_adrs = CharField(column_name='Responsible_Firm_Line_2_Adrs', null=True)
#     responsible_firm_mail_code = CharField(column_name='Responsible_Firm_Mail_Code', null=True)
#     responsible_firm_state = CharField(column_name='Responsible_Firm_State', null=True)
#     responsible_firm_type_code = CharField(column_name='Responsible_Firm_Type_Code', null=True)
#     responsible_firm_zip = CharField(column_name='Responsible_Firm_Zip', null=True)
#     sample_description = TextField(column_name='Sample_Description', null=True)
#     sample_number = CharField(column_name='Sample_Number')
#     shipper_fei = CharField(column_name='Shipper_FEI', null=True)
#     shipper_full_address = CharField(column_name='Shipper_Full_Address', null=True)
#     shipper_name = CharField(column_name='Shipper_Name', null=True)
#     serovar = CharField(null=True)

#     class Meta:
#         table_name = 'Load_ORDSS_GIMS'
#         schema = 'dbo'
#         primary_key = False


class State(BaseModel):
    abbr = CharField(column_name='Code', primary_key=True)
    name = CharField(column_name='State', null=True)
    # state_code_id = IntegerField(column_name='StateCodeID')

    class Meta:
        table_name = 'StateCode'





### Normalized data model ###

class Address(BaseModel):
    city = CharField()
    country = ForeignKeyField(Country)
    line1 = CharField()
    line2 = CharField(default="")
    mail_code = CharField(null=True)
    state = ForeignKeyField(State)
    zip_code = CharField(null=True)

    @property
    def full(self):
        "We can use properties to create convenience fields that are based on the other values"
        return f"""
{self.line1}
{self.line2}
{self.city}, {self.state}, {self.country.iso3} {self.zip_code}
"""

    def __repr__(self):
        return ", ".join(filter(lambda n: n, [self.line1, self.line2, self.city, self.state.code, self.country.iso3, self.zip_code]))




class Firm(BaseModel):

    fei = IntegerField(null=False, unique=True)
    name = CharField(null=True)
    legal_status = CharField(null=True)
    regulation_type = CharField(null=True)
    address = ForeignKeyField(Address, null=True)
    subsumed_by = ForeignKeyField('self', null=True, backref='firms_subsumed')



class TaxonomicName:
    "Non-model utility class"

    def __init__(self, *names):
        self.names = names

    def __str__(self):
        if len(self.names) == 4:
            genus, species, subsp, sero = self.names
            return f"{genus.name} {species.name} subsp. {subsp.name} {sero.rank} {sero.name}"
        elif len(self.names) == 3:
            genus, species, subsp = self.names
            return f"{genus.name} {species.name} {subsp.name}"
        elif len(self.names) == 2:
            genus, species = self.names
            return f"{genus.name} {species.name}"
        return f"{self.names[0].name} sp."

    def __repr__(self):
        return str(self)

    def __iter__(self):
        return iter(self.names)

class Taxon(BaseModel):

    class Meta:

        indexes = (
            (('rank', 'name', 'supertaxon'), True),
        )

    rank = CharField()
    name = CharField()
    supertaxon = ForeignKeyField('self', null=True, backref='subtaxa')

    @staticmethod
    def of(genus, species=None, *, subspecies=None, serovar=None, serotype=None, **other_terms):
        if serovar and serotype:
            raise ValueError("can't provide both serotype and serovar")
        subsubspecies = serovar or serotype
        genus, _ = Taxon.get_or_create(rank='genus', name=genus)
        if species and species != 'sp.':
            species, _ = Taxon.get_or_create(rank='species', name=species, supertaxon=genus)
        else:
            species = genus
        if subspecies:
            subspecies, _ = Taxon.get_or_create(rank='subspecies', name=subspecies, supertaxon=species)
        if subsubspecies:
            rank = ('serotype', 'serovar')[bool(serovar)]
            subsubspecies, _ = Taxon.get_or_create(rank=rank, name=subsubspecies, supertaxon=subspecies or species)
        parent = None
        if other_terms:
            parent = subsubspecies or subspecies or species
            for rank, name in other_terms.items():
                parent, _ = Taxon.get_or_create(rank=rank, name=name, supertaxon=parent)
        return parent or subsubspecies or subspecies or species

    def _recurse(self):
        "N+1 behavior, not ideal, should replace with a CTE"
        if not self.supertaxon:
            yield self
        else:
            yield from chain(self.supertaxon._recurse(), [self])

    def _recurse_to_genus(self):
        if self.rank == 'genus' or not self.supertaxon:
            yield self
        else:
            yield from chain(self.supertaxon._recurse(), [self])

    @property
    def binomial(self):
        return TaxonomicName(*self._recurse_to_genus())

    def __str__(self):
        return f"{self.rank} {self.name}"

    @property
    def isolates(self):
        "Inefficient, we'll want to replace with a CTE"
        yield from chain(*(subtaxon.isolates for subtaxon in self.subtaxa), self._isolates)

    # Important pseudoconstants

    @pseudoconstant
    def HUMAN(cls):
        return cls.of("Homo", "sapiens")
    
    @pseudoconstant
    def MOUSE(cls):
        return cls.of("Mus", "musculus")
    
    @pseudoconstant
    def COW(cls):
        return cls.of("Bos", "taurus")
    
    @pseudoconstant
    def PIG(cls):
        return cls.of("Sus", "domesticus")
    
    @pseudoconstant
    def CHICKEN(cls):
        return cls.of("Gallus", "gallus")
    
    @classmethod
    def significant_hosts(cls, host):
        if host.lower == 'human':
            return cls.HUMAN
        if host.lower == 'mouse':
            return cls.MOUSE
        if host.lower == 'cow':
            return cls.COW
        if host.lower == 'pig' or host.lower == 'pork' or host.lower == 'wild boar' or host.lower == 'domestic pig' or host.lower == 'swine':
            return cls.PIG
        if host.lower == 'chicken' or host.lower == 'broiler':
            return cls.CHICKEN
        return None


# +--------+
# | Text   |
# |--------|
# | CREATE FUNCTION traverse_parents (@start_pk int)
#         |
# | RETURNS TABLE
#         |
# | WITH SCHEMABINDING
#         |
# | AS
#         |
# | RETURN
#         |
# | (
#         |
# | WITH parent_CTE (cntn_pk, cntn_fk_originalContent, cntn_barCode) AS
#         |
# |       (SELECT cntn_pk, cntn_fk_originalContent, cntn_barCode from dbo.content WHERE cntn_pk = @start_pk
#         |
# |        UNION ALL
#         |
# |        SELECT C.cntn_pk, C.cntn_fk_originalContent, C.cntn_barCode FROM dbo.content C
#         |
# |        INNER JOIN parent_CTE pcte ON pcte.cntn_fk_originalContent = C.cntn_pk)
#         |
# | SELECT cntn_pk AS parent_pk FROM parent_CTE
#         |
# | );
#         |
# | 
#         |
# | 


class Sample(BaseModel):

    # oradss_id=IntegerField(unique=True)

    _row_checksum = TextField(index=True, unique=True, column_name='row_checksum')


    collection_date = DateField(null=True) # breaking my own rule, here, and not normalizing out a 'Collection' type
    collection_date_accuracy_mask = TimedeltaField(default=timedelta(0)) # an idea I've been kicking around with Nabil-Fareed Alikhan
    collection_method = CharField(null=True)
    collection_remarks = TextField(default="", null=True)
    collection_reason = TextField(default="", null=True)

    sample_description = TextField(null=True)
    product_description = TextField(null=True)

    country_of_origin = ForeignKeyField(Country, null=True)

    related_food = CharField(null=True)
    related_food_ontology_code = CharField(null=True)

    latitude = FloatField(null=True)
    longitude = FloatField(null=True)

    # if a Firm is just a name, an address, and an FEI then we can use the same entries in the table
    # to relate samples to firms in important ways, without duplicating information at all


    # responsible_firm = ForeignKeyField(Firm, backref='responsible_samples', null=True)
    # manufacturing_firm = ForeignKeyField(Firm, backref='manufactured_samples', null=True)
    # consignee = ForeignKeyField(Firm, backref='consigned_samples', null=True)
    # shipper = ForeignKeyField(Firm, backref='shipped_samples', null=True)
    # firm = ForeignKeyField(Firm, backref='owned_samples', null=True) # not sure if we need this

    # and we can follow these backreferences to see a firm's responsibility or origin
    # for its samples

    def name_in(self, namespace):
        name = SampleName.select().where(SampleName.namespace==namespace, SampleName.isolate==self).first()
        if name:
            return name.name

    @staticmethod
    def of(name):
        return SampleName.lookup(name)

    @property
    def collected_date_range(self):
        if self.isolation_date is not null:
            return self.collection_date - self.collection_date_accuracy_mask, self.collection_date + self.collection_date_accuracy_mask

    @property
    def barcode(self):
        return self.name_in(Namespace.GIMS_BARCODES)

    @property
    def firms(self):
        for relationship in self.firm_relationships:
            yield relationship.firm

    @property
    def responsible_firms(self):
        yield from Firm.select().join(FirmSampleRelationship).where(FirmSampleRelationship.sample == self, FirmSampleRelationship.responsibility == 1)

    @property
    def manufacturers(self):
        yield from Firm.select().join(FirmSampleRelationship).where(FirmSampleRelationship.sample == self, FirmSampleRelationship.relationship_code == 'M')

    @property
    def consignees(self):
        yield from Firm.select().join(FirmSampleRelationship).where(FirmSampleRelationship.sample == self, FirmSampleRelationship.relationship_code == 'C')

    @property
    def shippers(self):
        yield from Firm.select().join(FirmSampleRelationship).where(FirmSampleRelationship.sample == self, FirmSampleRelationship.relationship_code == 'S')

class ClinicalSample(BaseModel):

    _row_checksum = TextField(index=True, unique=True, column_name='row_checksum')

    host = TextField(null=True)
    host_organism = ForeignKeyField(Taxon, null=True, backref='specimens')

    country_of_origin = ForeignKeyField(Country, null=True)

    collection_date = DateField(null=True) # breaking my own rule, here, and not normalizing out a 'Collection' type
    collection_date_accuracy_mask = TimedeltaField(default=timedelta(0)) # an idea I've been kicking around with Nabil-Fareed Alikhan
    collection_method = CharField(null=True)
    collection_remarks = TextField(default="", null=True)
    collection_reason = TextField(default="", null=True)

    latitude = FloatField(null=True)
    longitude = FloatField(null=True)

    # TBD


class FirmSampleRelationship(BaseModel):

    # codes = (('',''), # figure permissable codes later
    #          ('',''),
    #         )

    sample = ForeignKeyField(Sample, null=False, backref='firm_relationships')
    firm = ForeignKeyField(Firm, null=False, backref='sample_relationships')
    relationship_code = CharField(null=True)
    responsibility = IntegerField(null=False, default=0)


class Isolate(BaseModel):

    gims_pk = IntegerField(null=True) # need to make this less than a key now
    _envsource = ForeignKeyField(Sample, null=True, column_name="envsample_fk", backref='isolates')
    _clisource = ForeignKeyField(ClinicalSample, null=True, column_name="clisample_fk", backref='isolates')
    _taxonomy = ForeignKeyField(Taxon, backref='_isolates', null=True) # this field is worth hiding a little

    isolation_date = DateField(null=True) # breaking my own rule, here, and not normalizing out a 'Collection' type
    isolation_date_accuracy_mask = TimedeltaField(default=timedelta(0)) # an idea I've been kicking around with Nabil-Fareed Alikhan

    @property
    def source(self):
        return self._envsource or self._clisource
    
    @source.setter
    def source(self, value):
        if isinstance(value, Sample):
            self._envsource = value
        elif isinstance(value, ClinicalSample):
            self._clisource = value

    @property
    def isolation_date_range(self):
        if self.isolation_date is not None:
            return self.isolation_date - self.isolation_date_accuracy_mask, self.isolation_date + self.isolation_date_accuracy_mask

    @property
    def binomial(self):
        return self._taxonomy.binomial

    #convenience property to expose an iterator over the taxonomic chain

    @property
    def taxonomy(self):
        yield from self._taxonomy._recurse()

    @taxonomy.setter
    def taxonomy(self, value):
        self._taxonomy = value

    #convenience properties to retreive important names

    def name_in(self, namespace):
        name = IsolateName.select().where(IsolateName.namespace==namespace, IsolateName.isolate==self).first()
        if name:
            return name.name

    @property
    def biosample(self):
        "Once we normalize over names, it's really easy to alias back to important types of names"
        return self.name_in(Namespace.BIOSAMPLE)

    @property
    def fda_accession(self):
        return self.name_in(Namespace.FDA_ACCESSION)

    @property
    def strain_name(self):
        return self.name_in(Namespace.STRAIN_NAME)

    @property
    def fda_pulse_net_key(self):
        return self.name_in(Namespace.FDA_PULSENET_KEY)

    @property
    def barcode(self):
        return self.name_in(Namespace.GIMS_BARCODE)

    # convenience properties to retreive taxonomic names

    @property
    def genus(self):
        return # query to recursively return genus from taxonomy chain
    
    @property
    def species(self):
        return # as above

    @property
    def subspecies(self):
        return

    @property
    def serovar(self):
        return

    @property
    def serotype(self):
        return 

    @staticmethod
    def of(name):
        return IsolateName.lookup(name)



class Namespace(BaseModel):

    #important pseudoconstants

    @pseudoconstant
    def BIOSAMPLE(cls):
        return cls.of("NCBI Biosample")

    @pseudoconstant
    def FDA_ACCESSION(cls):
        return cls.of("FDA CFSAN Accession Numbers")

    @pseudoconstant
    def ORADSS_SAMPLE_NUMBER(cls):
        return cls.of("ORADSS Sample Numbers")

    @pseudoconstant
    def FDA_RUN_ACCESSION(cls):
        return cls.of("FDA CFSAN Run Accession Numbers")

    @pseudoconstant
    def ISOLATE_ID(cls):
        return cls.of("FDA Isolate IDs")

    @pseudoconstant
    def STRAIN_NAME(cls):
        return cls.of("Publicly-Unique Strain Names")

    @pseudoconstant
    def FDA_PULSENET_KEY(cls):
        return cls.of("FDA PulseNet Keys")

    @pseudoconstant
    def GIMS_SAMPLE_NUMBER(cls):
        return cls.of("GIMS Sample Numbers")

    @pseudoconstant
    def GIMS_BARCODE(cls):
        return cls.of("GIMS Barcodes")
    
    @pseudoconstant
    def FREEZER_ID(cls):
        return cls.of("FDA CFSAN Freezer IDs")


    name = CharField()

    @classmethod
    def of(cls, name):
        return cls.get_or_create(name=name)[0] # return only the value, we don't care if we had to create it



class SampleName(BaseModel):
    "Normalizing over names means we can look up any name in a simple, single-table search"

    class Meta:
        indexes = (
            (('name', 'namespace', 'sample'), True),
        )

    name = CharField()
    sample = ForeignKeyField(Sample, backref='names')
    namespace = ForeignKeyField(Namespace, backref='sample_names')

    def __str__(self):
        return f"{self.name} ({self.sample} in {self.namespace.name})"

    @classmethod
    def lookup(cls, name):
        "Really easy to implement a universal name lookup this way."
        name = cls.get_or_none(cls.name == name)
        if name:
            return name.sample
        
class ClinicalSampleName(BaseModel):
    "Normalizing over names means we can look up any name in a simple, single-table search"

    class Meta:
        indexes = (
            (('name', 'namespace', 'sample'), True),
        )

    name = CharField()
    sample = ForeignKeyField(ClinicalSample, backref='names')
    namespace = ForeignKeyField(Namespace, backref='sample_names')

    def __str__(self):
        return f"{self.name} ({self.sample} in {self.namespace.name})"

    @classmethod
    def lookup(cls, name):
        "Really easy to implement a universal name lookup this way."
        name = cls.get_or_none(cls.name == name)
        if name:
            return name.sample

class IsolateName(BaseModel):

    class Meta:
        indexes = (
            (('name', 'namespace', 'isolate'), True),
        )

    name = CharField()
    isolate = ForeignKeyField(Isolate, backref='names')
    namespace = ForeignKeyField(Namespace, backref='isolate_names')
    

    @classmethod
    def lookup(cls, name):
        "Really easy to implement a universal name lookup this way."
        name = cls.get_or_none(cls.name == name)
        if name:
            return name.isolate

@contextmanager
def make_connection(path=None):
    log = logging.getLogger("datonius")
    if path:
        log.info(f"Found path {path}")
        if ":memory:" not in path:
            path = str(Path(path).absolute())
        database = SqliteDatabase(path, pragmas=dict(journal_mode='wal', foreign_keys=1, cache_size=10000))
    else:
        # database = MssqlDatabase('ORDSS_FACTS_GIMS', 
        #                          host=environ.get("DATONIUS_DB", 'csvcesrv014.fda.gov'), 
        #                          user=environ.get("DATONIUS_USER") or input("Enter username credential for Datonius DB:"), 
        #                          password=environ.get("DATONIUS_PASS") or input("Enter password:")
        #                          )

        host = environ.get('DATONIUS_DB', 'localhost').strip()
        user = environ.get('DATONIUS_USER', '').strip()
        passwd = environ.get('DATONIUS_PASS', '').strip()
        port = environ.get('DATONIUS_PORT', 5432)

        log.info(f"Found host={host}, user={user}, port={port}, and password of length {len(passwd)}")

        if False: # "amazonaws" in host:
            region = environ.get('DATONIUS_AWS_REGION' or 'us-east-1a')
            cert = environ.get('DATONIUS_SSL_CERTIFICATE' or False)
            if not cert:
                raise ValueError('''can't connect to AWS RDS; path to SSL certificate not set (see 'https://docs.aws.amazon.com/AmazonRDS/latest/UserGuide/UsingWithRDS.SSL.html'.)''')
            try:
                import boto3
                session = boto3.Session(profile_name = 'RDSCreds')
                client = session.client('rds')
                passwd = client.generate_db_auth_token(DBHostname=host, Port=port, DBUsername=user, Region=region)
            except ImportError:
                print("Boto3 required for connection to AWS RDS databases.", file=stderr)
                quit()
            finally:
                database = PostgresqlDatabase(
                    'Datonius',
                    host=host,
                    user=user,
                    password=passwd,
                    port=port,
                    ssl_ca=cert
                )
        else:
            database = PostgresqlDatabase(
                    'datoniusdb',
                    host=host,
                    user=user,
                    password=passwd,
                    port=port,
                )

    try:
        database_proxy.initialize(database)
        database_proxy.connect()
        database_proxy.session_start()
        try:
            database_proxy.create_tables([Address, Country, Firm, Taxon, Isolate, State, Sample, ClinicalSample, ClinicalSampleName, Namespace, SampleName, IsolateName, FirmSampleRelationship])
        except ProgrammingError as e:
            try:
                import psycopg2
                if hasattr(e, '__context__') and isinstance(e.__context__, psycopg2.errors.InsufficientPrivilege):
                    log.getChild("psycopg").warning(e.__context__)
            except ImportError:
                pass
            log.getChild("peewee").warning("Wasn't able to ensure table creation, but they may already be created")
            database_proxy.session_rollback()
            database_proxy.session_start()
        yield database_proxy
    finally:
        database_proxy.session_commit()
        database_proxy.close()

# Set up fixtures and constants

# Taxon.of('Listeria', 'monocytogenes')
# sal = Taxon.of('Salmonella', 'enterica', subspecies='enterica', serovar='Javiana')
# sal = Taxon.of('Salmonella', 'enterica', subspecies="enterica")
# print(sal.binomial)
# print(list(sal._recurse()))
# print(Taxon.of('Escherichia', 'coli', serotype="O157:H7"))




# # Some examples


# from datonius import make_connection, Isolate, Firm, Taxon

# with make_connection('/path/to/metadata.db'):

#     Isolate.of("CFSAN001992") # lookup a name in all namespaces
#     Isolate.of('CFSAN001992').biosample # get an important name for an isolate
#     [print(firm.legal_name) for firm in Isolate.of("CFSAN001992").responsible_firms]

#     Firm.get(Firm.name == "Sal Monella's Diner").samples

#     print(len(Taxon.select().where(Taxon.rank == 'genus'))) # print number of genera in database

#     for isolate in Taxon.of('Salmonella', 'enterica').isolates:
#         for firm in isolate.responsible_firms:
#             print(firm.addess.state.name)

#     IsolateName.select() # get biosamples of all isolates from firms in Minnesota
#                .join(Isolate)
#                .join(Sample)
#                .join(FirmSampleRelationship)
#                .join(Firm)
#                .join(Address)
#                .join(State)
#                .switch(IsolateName)
#                .join(Namespace)
#                .where(
#                 State.name == 'Minnesota',
#                 Namespace == Namespace.BIOSAMPLE
#                )
    
#     for firm in Firm.select():
#         for rel in firm.sample_relationships:
#             for isolate in rel.sample.isolates:
#                 yield (isolate.taxon.binomial, rel.sample.collection_date, rel.sample.related_food, rel.relationship_code, firm.name, firm.address)
    



# sample.save()


# sample = Sample...
# firm 

# row = (firm.name, sample.biosample .... )

# rows.append(row)

# pd.from_list(rows)

# digraph G {
#     graph [
#       rankdir = "LR"
#       ];
      
#     sample [
#     label = "<h> Sample | collection_date | collection_date_accuracy_mask | collection_method | collection_remarks | collection_reason | sample description | product_description | <f0> country_of_origin | related_food | related_food_ontology_code"
#     shape = "record"
#       ]
#     isolate [
#       label = "<h> Isolate | <f0> sample | <f1> taxonomy"
#       shape = "record"
#       ]
#     country [
#       label = "<h> Country | iso | iso3 | name | num_code | phone_code"
#       shape = "record"
#       ]
#     state [
#       label = "<h> StateCode | code | state"
#       shape = "record"
#         ]
#     address [
#         label = "<h> Address | city | <f0> country | line1 | line2 | mail_code | <f1> state  | zip_code"
#         shape = "record"
#         ]
#     firm [
#         label = "<h> Firm | name | fei | <f0> address"
#         shape = "record"
#         ]
#     FirmSampleRel [
#         label = "<h> FirmSampleRel | <f0> sample | relationship_code | responsibility | <f1> firm"
#         shape = "record"
#         ]
#     taxon [
#         label = "<h> Taxon | rank | name | <f0> supertaxon"
#         shape = "record"
#         ]
#     namespace [
#         label = "<h> Namespace | name"
#         shape = "record"
#         ]
#     SampleName [
#         label = "<h> SampleName | <f0> namespace | name | <f1> sample"
#         shape = "record"
#         ]
#     IsolateName [
#         label = "<h> IsolateName | <f1> isolate | <f0> namespace | name"
#         shape = "record"
#         ]
#     sample:f0 -> country:h
#     FirmSampleRel:f0 -> sample:h
#     FirmSampleRel:f1 -> firm:h
#     isolate:f0 -> sample:h
#     isolate:f1 -> taxon:h
#     address:f0 -> country:h
#     address:f1 -> state:h
#     firm:f0 -> address:h
#     taxon:f0 -> taxon:h
#     SampleName:f0 -> namespace:h
#     SampleName:f1 -> sample:h
#     IsolateName:f0 -> namespace:h
#     IsolateName:f1 -> isolate:h
    
# }