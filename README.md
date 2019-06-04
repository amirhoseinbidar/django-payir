# django-payir
  اپ اتصال به درگاه پرداخت پی دات ای ار
  
# نصب 
  این اپ هنوز در  <br /> 
  pip <br />
  معرفی نشده پس تنها راه استفاده ازش این هست که اون رو دانلود کنید و در پروژتون بزارید
  
  بعد نصبش کنید 
  ```
  INSTALLED_APPS = [
  ...
  'pay',
  ...
  ]
  ```
  
  .دامنه خود را مشخص کنید
  ```
  PAY_USED_DOMAIN ='http://www.mydomain.com'
  ```
  
  و در اخر هم کلید ای پی آی خودتون رو تنظیم کنید
  ``` 
  PAY_API_KEY = "your key"  
  ```
  در صورت که هیچ کلیدی تنظیم نکنید به صورت پیش فرض درگاه تست برای شما باز میشود
  
 # روش استفاده
  تنها کاری که شما باید بکنید این هست که یک فرم بسازید در صورتی که کاربر دکمه
  پرداخت را زد به درگاه پرداخت هدایت شده و در صورت پرداخت و یا کنسل کردن 
  پرداخت به شما اطلاع داده میشود 
  <br />
  مثال
  ```
    from pay.forms import PayForm
    ...
    
    def my_view(request):
      form = PayForm(initial = {
            'formName' : 'aabcd' ,   #  اسم فرم برای دسته بندی فرم ها استغاده میشه
            'extraData' : 'some_data' , # این فیلد به درگاه پرداخت فرستاده نمیشود برای فرستادن اطلاعات اضافه برای هر فرم است
            'amount' : 10000 ,  # مقدار پرداختی
            'mobile' : "0912345678991" , # برای نمایش درگاه موبایلی 
            'description' : 'this is a test transaction', #   توضیحاتی که به کاربر  هنگام وارد شدن به درگاه باید نشان داده شوند
            'factorNumber' : 1234345, # شماره فاکتور
            'cancel_url' : '/test/cancel' , # یو ار الی که در صورتی که کاربر پرداخت را کنسل کرد به انجا منتقل میشود
            'return_url' : '/test/retrun' , # یو ار الی که در صورتی که کاربر پرداخت را انجام داد به انجا منتقل میشود
      })
  ```
  در تمپلیت خود به این صورت مینویسیم
  ```
    ...
    
    <form action="{{form.pay_form_processor}}" method="post">
        {% csrf_token %}
        {{form}}
        <input type="submit" value="خرید" >
    </form> 
    
    ...
  
  ```
  نکته: هیچ کدام از آن مقادیر به کاربر نشان داده نمیشوند در واقع هیدن هستند
  همین بود همش  
  در صورت کلیک بر روی دکمه پرداخت کاربر به درگاه پرداخت هدایت میشود 
  
# حالت پیشرفته
  مقادیری که در مثال قبل به فرم میدادیم در واقع در تمپلیت نوشته میشوند اگه دوست ندارید که این اتفاق 
  بیفته یا اینکه نیاز به ارسال اطلاعات متفاوت بر اساس نوع کاربر و فرم هستید میتونید از  مثال ۲ استفاده کنید
  
  ```
    from pay.forms import PayForm , MethodField
    ...
    
    def my_view(request):
      form = PayForm(initial = {
            'form_name' : 'aabcd' ,  
            'amount' : MethodField(signal_method_name = 'test_amount') ,# اسم متدی که بعد از کلیک کردن کاربر بر روی دکمه پرداخت فراخوانی میشود  
            'mobile' : MethodField(signal_method_name = 'test_mobile') ,# اسم متدی که بعد از کلیک کردن کاربر بر روی دکمه پرداخت فراخوانی میشود   
            'description' : 'this is a test transaction', 
            'factorNumber' : 1234345, 
            'cancel_url' : '/test/cancel' , 
            'return_url' : MethodField('redirect_success_url'),
      })
    
    در فایل ستینگ پروژه مکان و نام متد ها را بنویسید
    ...
    PAY_SIGNAL_METHODS = {
      'test_amount' : 'myapp.somepath.signal_test_amount' ,
      'test_mobile' : 'myapp2.some_other_path.signal_test_mobile' ,
      'redirect_success_url' : 'myapp3.path.success_url',
    }
    ...
    
    و متدهای خود را به این صورت تعریف کنید
    # myapp.somepath
    def signal_test_amount(request,form_name):
      ... some stuff 
    return amount
    
    # myapp2.some_other_path
    def signal_test_mobile(request,form_name):
      ... some other stuff
    return mobile
    
   
    # myapp3.path
    def tender_success_url(request , description , cardNumber , 
        factorNumber , amount , traceNumber , mobile ,
        message , transId , extraData , status ):
          
          return redirect('/success/')
  ```
# نکته 
  در صورتی که
  ```MethodField```
  برای 
  ```cancel_url , return_url```
  تعریف کنید این ۲ متد بعد از فرستاده شدن به درگاه پرداخت فراخوانی میشوند و مقادیر فرستاده شده نیز متفاوت است
  
# سخن آخر  
 در صورت پیدا کردن باگ یا داشتن هرگونه پیشنهاد خوشحال میشم که مطرح کنید
  
  
  
  
  
  
  
 
  
