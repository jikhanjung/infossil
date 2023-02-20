from django.db import models

# Create your models here.
class TaxonRank(models.Model):
    name = models.CharField(max_length=200)
    def __str__(self):
        return self.name

class Taxon(models.Model):
    RANK_CHOICES = [
        ( '11', 'Subspecies' ),
        ( '12', 'Species' ),
        ( '13', 'Superspecies' ),
        ( '21', 'Subgenus' ),
        ( '22', 'Genus' ),
        ( '23', 'Supergenus' ),
        ( '31', 'Subfamily' ),
        ( '32', 'Family' ),
        ( '33', 'Superfamily' ),
        ( '41', 'Suborder' ),
        ( '42', 'Order' ),
        ( '43', 'Superorder' ),
        ( '51', 'Subclass' ),
        ( '52', 'Class' ),
        ( '53', 'Superclass' ),
        ( '61', 'Subphylum' ),
        ( '62', 'Phylum' ),
        ( '63', 'Superphylum' ),
        ( '72', 'Kingdom' ),
        ( 'UR', 'Unranked' ),
        #( 'CL', 'Clade' ),
    ]

    name = models.CharField(max_length=200)
    rank = models.CharField(max_length=20,choices=RANK_CHOICES, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    author = models.CharField(max_length=200, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    sensu = models.CharField(max_length=200, null=True, blank=True)
    remarks = models.CharField(max_length=500, null=True, blank=True)
    def __str__(self):
        return self.name