from django.db import models

# Create your models here.

class Pengguna(models.Model):
    id_pengguna = models.AutoField(primary_key=True)
    nama_pengguna = models.CharField(max_length=50)
    nama_lengkap = models.CharField(max_length=100)
    email = models.CharField(max_length=50,null=True)
    password = models.CharField(max_length=128)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.nama_pengguna    
    
class Gambar(models.Model):
    id_gambar = models.BigAutoField(primary_key=True)
    id_pengguna =models.ForeignKey(Pengguna, on_delete=models.CASCADE, db_column='id_pengguna')
    id_direktori = models.IntegerField()
    id_dataset = models.BigIntegerField()
    nama_file = models.CharField(max_length=50)
    ukuran_file = models.IntegerField()
    tanggal_dibuat = models.DateField()
    format_file = models.CharField(max_length=11)
    tanggal_pengambilan = models.DateField()
    model_kamera = models.IntegerField()
    lebar = models.IntegerField()
    tinggi = models.IntegerField()
    lokasi_pengambilan = models.IntegerField()
    id_pembuat = models.IntegerField()
    tanggal_buat = models.DateTimeField()

    def __str__(self):
        return self.nama_file

class ProfileJob(models.Model):
    id_profile_job = models.BigAutoField(primary_key=True)
    id_pengguna = models.ForeignKey(Pengguna, on_delete=models.CASCADE, db_column='id_pengguna')
    nama_profile_job = models.CharField(max_length=100)
    deskripsi = models.CharField(max_length=500)
    start_date = models.DateField()
    end_date = models.DateField()
    isu = models.CharField(max_length=500)

    def __str__(self):
        return self.nama_profile_job

class JobItem(models.Model):
    id_job_item = models.BigAutoField(primary_key=True)
    id_profile_job = models.ForeignKey(ProfileJob, on_delete=models.CASCADE, db_column='id_profile_job')
    id_gambar = models.ForeignKey(Gambar, on_delete=models.CASCADE, db_column='id_gambar')
    id_job_assignment_annotator = models.BigIntegerField()
    id_job_assignment_reviewer = models.BigIntegerField()
    status_pekerjaan = models.CharField(max_length=1)

    def __str__(self):
        return f"JobItem {self.id_job_item} - Status: {self.status_pekerjaan}"

class TipeSegmentasi(models.Model):
    id_tipe_segmentasi = models.IntegerField(primary_key=True)
    nama_tipe_segmentasi = models.CharField(max_length=50)

    def __str__(self):
        return self.nama_tipe_segmentasi

class Segmentasi(models.Model):
    id_segmentasi = models.BigAutoField(primary_key=True)
    id_tipe_segmentasi = models.ForeignKey(TipeSegmentasi, on_delete=models.CASCADE, db_column='id_tipe_segmentasi')
    label_segmentasi = models.CharField(max_length=20)
    warna_segmentasi = models.CharField(max_length=10)
    koordinat = models.IntegerField()
    id_job_item = models.ForeignKey(JobItem, on_delete=models.CASCADE, db_column='id_job_item')

    def __str__(self):
        return f"{self.label_segmentasi} ({self.warna_segmentasi})"
    
class Anotasi(models.Model):
    id_anotasi = models.BigAutoField(primary_key=True)
    id_segmentasi = models.ForeignKey(Segmentasi, on_delete=models.CASCADE, db_column='id_segmentasi')
    id_gambar = models.ForeignKey(Gambar, on_delete=models.CASCADE, db_column='id_gambar')
    koordinat_x = models.IntegerField()
    koordinat_y = models.IntegerField()
    lebar = models.IntegerField()
    tinggi = models.IntegerField()

    def __str__(self):
        return f"Anotasi {self.id_anotasi} - ({self.koordinat_x}, {self.koordinat_y})"
    
class PolygonTool(models.Model):
    id_polygon_tool = models.BigAutoField(primary_key=True)
    id_anotasi = models.ForeignKey('Anotasi', on_delete=models.CASCADE, db_column='id_anotasi')
    koordinat_xn = models.IntegerField()
    koordinat_yn = models.IntegerField()

    def __str__(self):
        return f"Titik ({self.koordinat_xn}, {self.koordinat_yn}) dari Anotasi {self.id_anotasi_id}"

# Isu
class IsuAnotasi(models.Model):
    id_isu_anotasi = models.BigAutoField(primary_key=True)
    id_anotasi = models.ForeignKey('Anotasi', on_delete=models.CASCADE, db_column='id_anotasi')
    message = models.CharField(max_length=200)
    id_pembuat = models.IntegerField()
    tanggal_buat = models.DateTimeField()
    nama_tipe_isu = models.IntegerField()
    id_parent_isu_anotasi = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"IsuAnotasi {self.id_isu_anotasi} - {self.message}"

class IsuImage(models.Model):
    id_isu_image = models.BigAutoField(primary_key=True)
    id_job_item = models.ForeignKey(JobItem, on_delete=models.CASCADE, db_column='id_job_item')
    message = models.CharField(max_length=200)
    id_pembuat = models.IntegerField()
    tanggal_buat = models.DateTimeField()
    nama_tipe_isu = models.IntegerField()
    id_parent_isu_image = models.BigIntegerField(null=True, blank=True)

    def __str__(self):
        return f"IsuImage {self.id_isu_image} - {self.message}"

# Member and Role
class Member(models.Model):
    id_member = models.BigAutoField(primary_key=True)
    id_pengguna = models.ForeignKey(Pengguna, on_delete=models.CASCADE, db_column='id_pengguna')
    email_member = models.CharField(max_length=50,null=True)
    no_hp_member = models.IntegerField(null=True)
    tanggal_registrasi = models.DateTimeField(auto_created=True)
    afiliasi = models.CharField(max_length=50,blank=True,null=True)
    peran = models.CharField(max_length=50)

class TipeRole(models.Model):
    id_tipe_role = models.BigIntegerField(primary_key=True)
    nama_tipe_role = models.CharField(max_length=10)

class MemberRole(models.Model):
    id_member_role = models.IntegerField(primary_key=True)
    id_member = models.ForeignKey(Member,on_delete=models.CASCADE, db_column='id_member')
    id_tipe_role = models.ForeignKey(TipeRole,on_delete=models.CASCADE,db_column='id_tipe_role')
    is_active = models.BooleanField(default=False)

