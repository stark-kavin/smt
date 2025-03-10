from django.db import models
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

class Party(models.Model):
    name        = models.CharField(max_length=50)
    location    = models.CharField(max_length=50,null=True,blank=True)
    phone       = models.CharField(max_length=10,null=True,blank=True)
    gst         = models.CharField(max_length=15,null=True,blank=True)

    def __str__(self):
        return f"{self.name} - {self.location}"
    
class Driver(models.Model):
    name        = models.CharField(max_length=50)
    phone       = models.CharField(max_length=10,null=True,blank=True)
    
    def __str__(self):
        return f"{self.name}"

class Vehicle(models.Model):
    name        = models.CharField(max_length=50)
    number      = models.CharField(max_length=10,null=True,blank=True)
    
    def __str__(self):
        return f"{self.name} - {self.number}"

class Item(models.Model):
    name    = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
class Entry(models.Model):
    date    = models.DateField()
    customer_from   = models.CharField(max_length=100)
    customer_to     = models.CharField(max_length=100)
    party           = models.ForeignKey(Party,on_delete=models.CASCADE)
    vehicle         = models.ForeignKey(Vehicle,on_delete=models.SET_NULL,null=True)
    driver          = models.ForeignKey(Driver,on_delete=models.SET_NULL,null=True)
    total           = models.CharField(max_length=100,null=True,blank=True)
    no_of_invoices  = models.IntegerField(default=0, null=True, blank=True)

    def __str__(self):
        return f"{self.party.name} - {self.date} - {self.total}"
    
class EntryItem(models.Model):
    entry   = models.ForeignKey(Entry,on_delete=models.CASCADE)
    item    = models.ForeignKey(Item,on_delete=models.CASCADE)
    quantity    = models.CharField(max_length=100)
    total = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.entry} - {self.item}"
    
class Invoice(models.Model):
    f_date = models.DateField()
    t_date = models.DateField()
    total = models.CharField(max_length=100,null=True,blank=True)

    def __str__(self):
        return str(self.f_date)

class InvoiceItem(models.Model):
    entry = models.ForeignKey(Entry,on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice,on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.entry} - {self.invoice}"

# Signal to increment no_of_invoices when an InvoiceItem is created
@receiver(post_save, sender=InvoiceItem)
def update_invoice_count_on_create(sender, instance, created, **kwargs):
    if created:
        entry = instance.entry
        entry.no_of_invoices = entry.invoiceitem_set.count()
        entry.save()

# Signal to update no_of_invoices when an InvoiceItem is deleted
@receiver(post_delete, sender=InvoiceItem)
def update_invoice_count_on_delete(sender, instance, **kwargs):
    if instance.entry_id:
        try:
            entry = Entry.objects.get(pk=instance.entry_id)
            entry.no_of_invoices = entry.invoiceitem_set.count()
            entry.save()
        except Entry.DoesNotExist:
            pass

# Signal to update invoice total when an InvoiceItem is created or updated
@receiver(post_save, sender=InvoiceItem)
def update_invoice_total_on_save(sender, instance, **kwargs):
    invoice = instance.invoice
    # Sum the total values of all entries linked to this invoice
    entries = Entry.objects.filter(invoiceitem__invoice=invoice)
    total_sum = sum(float(entry.total or 0) for entry in entries)
    invoice.total = str(total_sum)
    invoice.save(update_fields=['total'])

# Signal to update invoice total when an InvoiceItem is deleted
@receiver(post_delete, sender=InvoiceItem)
def update_invoice_total_on_delete(sender, instance, **kwargs):
    if instance.invoice_id:
        try:
            invoice = Invoice.objects.get(pk=instance.invoice_id)
            entries = Entry.objects.filter(invoiceitem__invoice=invoice)
            total_sum = sum(float(entry.total or 0) for entry in entries)
            invoice.total = str(total_sum)
            invoice.save(update_fields=['total'])
        except Invoice.DoesNotExist:
            pass

# Signal to update invoice totals when an Entry's total is updated
@receiver(post_save, sender=Entry)
def update_invoice_total_on_entry_update(sender, instance, **kwargs):
    # Find all invoices related to this entry
    invoices = Invoice.objects.filter(invoiceitem__entry=instance)
    for invoice in invoices:
        entries = Entry.objects.filter(invoiceitem__invoice=invoice)
        total_sum = sum(float(entry.total or 0) for entry in entries)
        invoice.total = str(total_sum)
        invoice.save(update_fields=['total'])

# Helper function to calculate Entry total
def calculate_entry_total(entry):
    entry_items = EntryItem.objects.filter(entry=entry)
    total_sum = sum(float(item.total or 0) for item in entry_items)
    return str(total_sum)

# Signal to update Entry total when an EntryItem is created or updated
@receiver(post_save, sender=EntryItem)
def update_entry_total_on_save(sender, instance, **kwargs):
    entry = instance.entry
    entry.total = calculate_entry_total(entry)
    entry.save(update_fields=['total'])

# Signal to update Entry total when an EntryItem is deleted
@receiver(post_delete, sender=EntryItem)
def update_entry_total_on_delete(sender, instance, **kwargs):
    if instance.entry_id:
        try:
            entry = Entry.objects.get(pk=instance.entry_id)
            entry.total = calculate_entry_total(entry)
            entry.save(update_fields=['total'])
        except Entry.DoesNotExist:
            pass