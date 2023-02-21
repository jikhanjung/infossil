from django.db import models
from django.urls import reverse
from simple_history.models import HistoricalRecords
from multiselectfield import MultiSelectField
from jamo import h2j, j2hcj, get_jamo_class
import hanja

def reference_upload_path(instance, filename): 
    # return f'posts/{instance.content}/{filename}'
    year = 1900
    if instance.year:
        year = int(instance.year)
    return 'references/{:4d}/{}.pdf'.format(year, instance.id)

# Create your models here.
class Author(models.Model):
    firstname_k = models.CharField(max_length=100,blank=True,null=True,default='',verbose_name="이름")
    lastname_k = models.CharField(max_length=100,blank=True,null=True,default='',verbose_name="성")
    firstname_e = models.CharField(max_length=100,blank=True,null=True,default='',verbose_name="Firstname")
    lastname_e = models.CharField(max_length=100,blank=True,null=True,default='',verbose_name="Lastname")
    affiliation = models.CharField(max_length=100,blank=True,null=True,verbose_name="소속")
    abbreviation_e = models.CharField(max_length=50, blank=True,null=True)
    abbreviation_k = models.CharField(max_length=50, blank=True,null=True)
    redirect_to = models.ForeignKey('self',on_delete=models.CASCADE,blank=True,null=True,related_name='also_known_as')
    is_primary = models.BooleanField(default=True)
    remarks = models.CharField(max_length=500,blank=True,null=True,verbose_name="비고")
    created_on = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    created_by = models.CharField(max_length=20,blank=True)
    modified_on = models.DateTimeField(blank=True,null=True,auto_now=True)
    modified_by = models.CharField(max_length=20,blank=True)
    history = HistoricalRecords()
    class Meta:
        ordering = ['abbreviation_k','abbreviation_e',]

    def generate_abbreviation(self):
        lastname_e = self.lastname_e or ''
        firstname_e = self.firstname_e or ''
        if lastname_e == '':
            self.abbreviation_e = firstname_e.replace(" ","")
        else:
            self.abbreviation_e = lastname_e + ", " + firstname_e.replace(" ","")
        if self.firstname_k and self.firstname_k != '':
            self.abbreviation_k = self.lastname_k + self.firstname_k

    @property
    def get_reference_count(self):
        count = ReferenceAuthor.objects.filter(author=self.id).count()
        return count

    @property
    def get_name(self):
        name = ''
        parens = ['','']
        if self.abbreviation_k and self.abbreviation_k != '':
            name += self.abbreviation_k
            parens = [ ' (', ')' ]
        if self.abbreviation_e and self.abbreviation_e != '':
            name += self.abbreviation_e.join(parens)
        #print(name)
        if name == '':
            name = "__"+str(self.id)+"__"
        return name
    def __str__(self):
        return self.abbreviation_e or self.abbreviation_k
    #def __str__(self):
    #    print( self.abbreviation_e, self.firstname_k )
    #    return ''
        # [ self.firstname_e, self.lastname_e ]

    def get_absolute_url(self):
        return reverse('author_detail', kwargs={'pk' : self.pk})


class Journal(models.Model):
    title_k = models.CharField(max_length=500,blank=True,null=True)
    title_e = models.CharField(max_length=500,blank=True,null=True)
    publisher = models.CharField(max_length=500,blank=True,null=True)
    since = models.IntegerField('started year',blank=True,null=True)
    issn = models.CharField(max_length=15,blank=True,null=True)
    created_on = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    created_by = models.CharField(max_length=20,blank=True)
    modified_on = models.DateTimeField(blank=True,null=True,auto_now=True)
    modified_by = models.CharField(max_length=20,blank=True)
    history = HistoricalRecords()
    def __str__(self):
        return self.title_e or self.title_k
    @property
    def get_title(self):
        if self.title_k and self.title_k != '':
            return self.title_k
        else:
            return self.title_e
    class Meta:
        ordering = ['title_k','title_e',]
class Reference(models.Model):
    REFERENCE_TYPE_CHOICES = [
        ( 'BK', 'Book' ),
        ( 'JN', 'Journal Article' ),
        ( 'RP', 'Report' ),
        ( 'TH', 'Thesis' ),
    ]
    REFERENCE_TYPE2_CHOICES = [
        ( 'TX', '분류학(표본번호 있음)' ),
        ( 'T2', '분류학(표본번호 없음)' ),
        ( 'RV', '비분류학' ),
        ( 'OS', '해외화석' ),
    ]
    FOSSIL_GROUP_CHOICES = [
        ( 'MA', '거화석' ),
        ( 'MI', '미화석' ),
        ( 'IC', '생흔화석' ),
    ]
    LANGUAGE_CHOICES = [
        ( 'EN', 'English' ),
        ( 'KO', 'Korean' ),
#        ( 'CN', 'Chinese' ),
#        ( 'SP', 'Spanish' ),
#        ( 'RU', 'Russian' ),
#        ( 'JP', 'Japanese' ),
    ]
    COMMON_NAME_CHOICES = [
        (u"삼엽충",u"삼엽충(trilobite)"),
        (u"곤충",u"곤충(insect)"),
        (u"개형충",u"개형충(ostracod)"),
        (u"이매패류",u"이매패류(bivalve)"),
        (u"복족류",u"복족류(gastropod)"),
        (u"두족류",u"두족류(cephalopod)"),
        (u"완족동물",u"완족동물(brachiopod)"),
        (u"해백합",u"해백합(sea lily)"),
        (u"성게",u"성게(sea urchin)"),
        (u"불가사리",u"불가사리(sea star)"),
        (u"산호",u"산호(coral)"),
        (u"해면동물",u"해면동물(sponge)"),
        (u"어류",u"어류(fish)"),
        (u"공룡",u"공룡(dinosaur)"),
        (u"포유류",u"포유류(mammals)"),
        (u"식물",u"식물(plant)"),
        (u"유공충",u"유공충(foraminifera)"),
        (u"코노돈트",u"코노돈트(conodont)"),
        (u"화분/포자",u"화분/포자(spore/pollen)"),
        (u"생흔화석",u"생흔화석(trace fossil)"),
        (u"기타",u"기타"),
    ]    
    title_e = models.CharField(max_length=1000,blank=True,null=True,verbose_name="영문제목")
    title_k = models.CharField(max_length=1000,blank=True,null=True,verbose_name="한글제목")
    year = models.CharField(max_length=4,blank=True,null=True,verbose_name="발표년도")
    publish_date = models.DateField(blank=True,null=True,verbose_name="출간연월일")
    volume = models.CharField(max_length=5,blank=True,null=True,verbose_name="권")
    issue = models.CharField(max_length=5,blank=True,null=True,verbose_name="호수")
    pages = models.CharField(max_length=20,blank=True,null=True,verbose_name="페이지")
    journal = models.ForeignKey(Journal, on_delete=models.CASCADE, blank=True, null=True,verbose_name="저널")
    journal_title = models.CharField(max_length=200,blank=True,null=True,verbose_name="저널제목")
    author = models.ManyToManyField(Author, through='ReferenceAuthor',verbose_name="저자")
    author_list = models.CharField(max_length=500, blank=True, null=True,verbose_name="저자")
    type = models.CharField(max_length=2,choices=REFERENCE_TYPE_CHOICES, blank=True,verbose_name="문헌종류",default='JN')
    type2 = models.CharField(max_length=2,choices=REFERENCE_TYPE2_CHOICES, blank=True,verbose_name="문헌종류",default='TX')
    data = models.FileField(upload_to=reference_upload_path, blank=True,verbose_name="파일",max_length=255)
    abstract = models.TextField(blank=True,null=True,verbose_name="초록")
    language = models.CharField(max_length=2,choices=LANGUAGE_CHOICES,blank=True,verbose_name="언어",default="EN")
    doi = models.CharField(max_length=200,blank=True,null=True,verbose_name="DOI")
    fossilgroup = models.CharField(max_length=200,blank=True,null=True,verbose_name="화석종류")
    fossilgroup_choice = models.CharField(max_length=20,choices=FOSSIL_GROUP_CHOICES,blank=True,null=True,verbose_name="화석종류")
    fossilgroup_macro = models.BooleanField(default=False,verbose_name="거화석")
    fossilgroup_micro = models.BooleanField(default=False,verbose_name="미화석")
    fossilgroup_ichno = models.BooleanField(default=False,verbose_name="생흔화석")
    commonname = models.CharField(max_length=200,blank=True,null=True,verbose_name="일반명")
    commonname_choice = models.CharField(max_length=20,choices=COMMON_NAME_CHOICES,blank=True,null=True,verbose_name="일반명")
    #commonname_multichoice = MultiSelectField(choices=COMMON_NAME_CHOICES,blank=True,null=True)
    remarks = models.CharField(max_length=500,blank=True,null=True,default='',verbose_name="비고")
    short_title = models.CharField(max_length=500,blank=True,null=True,verbose_name="색인")
    created_on = models.DateTimeField(blank=True,null=True,auto_now_add=True)
    created_by = models.CharField(max_length=20,blank=True)
    modified_on = models.DateTimeField(blank=True,null=True,auto_now=True)
    modified_by = models.CharField(max_length=20,blank=True)
    history = HistoricalRecords()
    def __str__(self):
        return self.title_e or self.title_k

    @property
    def get_fossilgroup(self):
        group_list = []
        if self.fossilgroup_macro:
            group_list.append("거화석")
        if self.fossilgroup_micro:
            group_list.append("미화석")
        if self.fossilgroup_ichno:
            group_list.append("생흔화석")
        if len(group_list) > 0:
            return "/".join(group_list)
        else:
            return ""
            
    @property
    def get_title(self):
        if self.language == 'EN':
            return self.title_e
        else:
            return self.title_k

    @property
    def get_authors(self):
        authors = self.author.all()
        print(authors)
        if len(authors) == 0:
            return self.author_list
        else:
            for a in authors:
                print(a.get_name)
            return ", ".join( [ a.get_name for a in authors ])

    def generate_short_title(self):
        language = 'KO'
        and_str = "과 "
        etal_str = " 외"
        year = '1900'#self.year
        if self.year:
            year = self.year
        author_list = [ str(a.abbreviation_k) for a in self.author.all().order_by('referenceauthor__author_order')]
        if self.language == 'EN':
            language = 'EN'
            and_str = " and "
            etal_str = " et al."
            author_list = [ str(a.lastname_e) for a in self.author.all().order_by('referenceauthor__author_order')]
        abbr_str = ""
        #print("generate_short_title", author_list, "reference id", self.id)
        if len(author_list) > 2:
            abbr_str += author_list[0] + etal_str + " (" + year + ")"
        elif len(author_list) == 2:
            if language == 'KO':
                first_author = author_list[0]
                if len(first_author) > 0:
                    last_syllable = first_author[-1]
                    if hanja.is_hanja(last_syllable):
                        last_syllable = hanja.translate(last_syllable,'substitution')
                    jamo_list = h2j(last_syllable)
                    #print(jamo_list)
                    if len(jamo_list) > 0:
                        last_jamo = jamo_list[-1]
                        try:
                            last_jamo_class = get_jamo_class(last_jamo)
                            if last_jamo_class != 'tail': # change to this 
                                and_str = "와 "
                        except:
                            print("can't get jamo class")
                            and_str = "와(과) "
            abbr_str += and_str.join(author_list) + " (" + year + ")"
        elif len(author_list) == 1:
            abbr_str += author_list[0] + " (" + year + ")"
        #print(author_list, abbr_str)
        self.author_list = ", ".join(author_list)
        self.short_title = abbr_str
        return abbr_str
        #ref.save()

    def save_without_historical_record(self, *args, **kwargs):
        self.skip_history_when_saving = True
        try:
            ret = self.save(*args, **kwargs)
        finally:
            del self.skip_history_when_saving
        return ret

class ReferenceAuthor(models.Model):
    reference = models.ForeignKey(Reference, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    author_order = models.IntegerField()
    class Meta:
        ordering = ["author_order"]

# Create your models here.
class TaxonRank(models.Model):
    rankcode = models.CharField(max_length=10)
    rankname = models.CharField(max_length=200)
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
        ( '71', 'Subkingdom' ),
        ( '72', 'Kingdom' ),
        ( '73', 'Superkingdom' ),
        ( 'UR', 'Unranked' ),
        #( 'CL', 'Clade' ),
    ]

    name = models.CharField(max_length=200)
    rank = models.CharField(max_length=20,choices=RANK_CHOICES, blank=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True)
    authorship = models.CharField(max_length=200, null=True, blank=True)
    author = models.CharField(max_length=200, null=True, blank=True)
    year = models.IntegerField(null=True, blank=True)
    sensu = models.CharField(max_length=200, null=True, blank=True)
    remarks = models.CharField(max_length=500, null=True, blank=True)
    def __str__(self):
        return self.name

class TaxonAuthor(models.Model):
    taxon = models.ForeignKey(Taxon, on_delete=models.CASCADE)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    author_order = models.IntegerField()
    class Meta:
        ordering = ["author_order"]
