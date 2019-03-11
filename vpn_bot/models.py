from django.db import models
'''
All VPN models are here
'''


class Customer(models.Model):
    wechat_id = models.CharField(max_length=255)
    name = models.CharField(max_length=255)

class Order(models.Model):
    PENDING = 'PENDING'
    EXPIRED = 'EXPIRED'
    COMPLETED = 'COMPLETED'
    STATE_CHOICES = ((PENDING, PENDING), (EXPIRED,EXPIRED),(COMPLETED,COMPLETED))
    state = models.CharField(max_length=60, choices = STATE_CHOICES)
    # assume that payment_code is issued at object creation time
    payment_code_issued_at = models.DateTimeField(auto_now=True)
    payment_code = models.CharField(max_length=10, null=True)
    payment_value = models.DecimalField(max_digits=28, decimal_places=4, null=True)
    transaction_id = models.CharField(max_length=255, null=True)
    WECHAT = 'WECHAT'
    transaction_type_choices = [(WECHAT, WECHAT)]
    transaction_type = models.CharField(max_length=64, choices=transaction_type_choices, null=True)
    customer_id = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    ONE_WEEK = 'ONE_WEEK'
    ONE_MONTH = 'ONE_MONTH'
    THREE_MONTH = 'THREE_MONTH'
    ITEM_CHOICES = ((ONE_WEEK,ONE_WEEK),(ONE_MONTH,ONE_MONTH),(THREE_MONTH,THREE_MONTH))
    item_type = models.CharField(max_length=64, choices=ITEM_CHOICES)
    comment = models.TextField(null=True)

class Dialog(models.Model):
    customer_id = models.ForeignKey(Customer, on_delete=models.SET_NULL, null=True)
    ACTIVE = 'ACTIVE'
    SLEEP = 'SLEEP'
    STATE_CHOICES = ((ACTIVE, ACTIVE),(SLEEP,SLEEP))
    state = models.CharField(max_length=64,choices=STATE_CHOICES)
    #  timestamp when object is updated
    update_time = models.DateTimeField(auto_now=True)


class VPN_service(models.Model):
    start_time = models.DateTimeField()
    order_id = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL)
    expire_on = models.DateTimeField()
    is_active = models.SmallIntegerField()
    ip = models.CharField(max_length=255)
    port=models.CharField(max_length=10)
    password=models.CharField(max_length=64)


class issue(models.Model):
    OPEN = 'OPEN'
    CLOSED = 'CLOSED'
    STATE_CHOICES = ((OPEN,OPEN),(CLOSED,CLOSED))
    state = models.CharField(max_length=10, choices=STATE_CHOICES, default=OPEN)
    order_id = models.ForeignKey(Order, null=True, on_delete=models.SET_NULL)
    customer_id = models.ForeignKey(Customer, null=True, on_delete=models.SET_NULL)
    payment_id = models.CharField(max_length=255, null=True)
    additional_info = models.TextField(null=True)
