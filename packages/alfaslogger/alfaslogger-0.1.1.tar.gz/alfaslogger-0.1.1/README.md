# AlfasLogger

AlfasLogger, konsol, dosya ve SQLite veritabanı olmak üzere farklı hedeflere loglama yapabilen, ayrıca gerçek zamanlı log görüntüleme için bir web arayüzü ve WebSocket sunucusu içeren kapsamlı bir Python loglama çözümüdür.

## Özellikler

* **Çoklu Handler Desteği**: Logları aynı anda konsola, dosyaya ve bir SQLite veritabanına yazabilir.
* **Özelleştirilebilir Formatlama**: Log mesajlarının formatı tamamen özelleştirilebilir.
* **Log Seviyeleri**: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL` gibi log seviyeleri mevcuttur.
* **Renkli Konsol Çıktısı**: Konsol logları, log seviyesine göre renklendirilir.
* **Web Tabanlı GUI**: Logları gerçek zamanlı olarak görüntülemek, eski log dosyalarını indirmek ve logları temizlemek için bir web arayüzü sunar.
* **Gerçek Zamanlı Log Akışı**: WebSocket üzerinden web arayüzüne gerçek zamanlı log akışı sağlar.
* **Log Temizleme İşlevselliği**: Belirli handler'lar (konsol, dosya, veritabanı) veya tüm log dosyaları için temizleme işlevselliği mevcuttur.
* **Log Dosyası Silme**: Uzantıya göre veya tüm log dosyalarını silme yeteneği bulunur.
* **Tekil Logger Örneği**: Belirli bir isimle yalnızca tek bir `Logger` örneği oluşturulmasını sağlar (Singleton deseni).

## Kurulum

`pip` kullanarak paketi kurabilirsiniz:

```bash
pip install alfaslogger
