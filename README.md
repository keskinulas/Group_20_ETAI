# Group_20_ETAI

ETAI projesi — Grup 20, 2026/27 akademik yılı.

Amaç: bir satın alma için tekrar alışveriş olasılığını, sınıflandırma kararını ve harcama tahminini üretmek.

## Durum

Bu ilk commit yalnızca proje yapılandırmasını içerir. `src/` kodu ve notebook'lar henüz eklenmemiştir; aşağıdaki eğitim ve tahmin komutları planlanan arayüzdür ve şu anda çalışmaz. Handbook incelenmiştir; CSV şeması ve veri temizleme kararları dosyalar sağlandığında doğrulanacaktır.

## Kurulum

Python 3.11 önerilir. Repoyu indirdikten sonra repo klasöründe çalışın.

### macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
mkdir -p data/raw
```

### Windows (PowerShell)

```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
New-Item -ItemType Directory -Force data/raw
```

PowerShell etkinleştirmeyi engellerse sanal ortamı etkinleştirmeden `.\.venv\Scripts\python.exe -m pip install -r requirements.txt` kullanabilirsiniz; diğer komutlarda da `python` yerine bu yolu yazın.

## Veriler ve yapı

`train.csv`, `test.csv`, `sample_submission.csv` ve isteğe bağlı `clientes.csv` dosyalarını yerel `data/raw/` klasörüne koyun. Dosya adlarını ve sütunları `config.yaml` içinde ayarlayın. Ham veri, sanal ortamlar, modeller ve üretilen çıktılar Git'e eklenmez. Tüm yapılandırma yolları repo köküne göredir.

```text
notebooks/  # 01_data_exploration, 02_classification, 03_regression, 04_explainability
src/        # data.py, features.py, train.py, predict_batch.py, predict_one.py
data/raw/   # Yerel CSV'ler
models/     # Eğitim sırasında oluşturulacak kayıtlı pipeline'lar
outputs/    # Tahmin CSV'leri ve değerlendirmeler
```

Notebook'larda temizleme kararları, model karşılaştırmaları ve her iki modelin açıklanabilirlik analizi belgelenecektir. Eğitim ve her iki tahmin yolu aynı özellik üretimini kullanacaktır; kayıtlı modeller ön işlemeyi de içerecektir.

## Planlanan komutlar

Kod eklendikten ve yapılandırma tamamlandıktan sonra:

```bash
python -m src.train --config config.yaml
python -m src.predict_batch --config config.yaml
python -m src.predict_one --config config.yaml --input purchase.json
```

`purchase.json` tek satın alma özelliklerini içeren bir JSON nesnesi olacaktır; gerekli alanlar veri şeması kesinleşince belgelenecektir. Tekil tahmin tekrar alışveriş olasılığını, yapılandırmadaki eşikle verilen kararı ve harcama tahminini döndürecektir. Toplu tahmin tüm test satırları için `ID,repeat_purchase_90d` sütunlarıyla Kaggle CSV'sini, yalnızca geri döneceği tahmin edilen satırlar için `ID,repeat_purchase_90d,spend_next_90d` sütunlarıyla harcama CSV'sini yazacaktır. Kaggle çıktısı `sample_submission.csv` yapısıyla eşleşecektir.

## Teslim

Repo adı `Group_20_ETAI` olarak belirlenmiştir. Handbook teslim arşivi için `Group20_ETAI_2627.zip` adını gerektirir; repo adı bu arşiv kuralını değiştirmez. Teslim tarihi 22 Aralık 2026, 18:00 olarak belirtilmiştir (saat dilimi belgede belirtilmemiştir). Nihai Kaggle CSV'si teslim arşivine ayrıca eklenecek ve `predict_batch.py` ile üretilen dosyayla eşleştiği kontrol edilecektir.

## Handbook gereksinimleri

- Hedefler: `repeat_purchase_90d` ve sonraki 90 günlük harcama olan `spend_next_90d`. `ID` modelleme satırı/Kaggle kimliği, `customer_id` ise `clientes.csv` birleştirme anahtarıdır.
- Sınıflandırmada en az 5, regresyonda en az 4 algoritma karşılaştırılmalı; ön işleme, özellik üretimi/seçimi, hiperparametre araması ve değerlendirme stratejisi gerekçelendirilmelidir. Yapılandırmadaki Random Forest yalnızca başlangıç adayıdır.
- Regresyon ile sınıflandırma tutarlı olmalı; regresyon değerlendirmesinde gerçekten geri dönen müşteriler için RMSE, MAE ve R² raporlanmalıdır.
- Her iki model için genel ve tek müşteri düzeyinde açıklanabilirlik analizi yapılmalıdır. İstemci yeni ve mevcut müşterilerle çalışmalıdır.
- Özellikler satın alma anında hesaplanabilir olmalı. Her test satırının tahmini yalnızca o satır, eğitim verisi ve `clientes.csv` kullanmalı; diğer test satırlarını kullanmamalıdır. Regresyon hedefi sınıflandırma özelliği olarak kullanılmamalıdır.
- Tahmin kayıtlı pipeline'ı yüklemeli, yeniden eğitim yapmamalıdır. Değiştirilebilir seçimler yapılandırmada tutulmalıdır.
- Lazy Predict ve benzeri AutoML araçları yasaktır. Notebook ve kodda kullanılan her adım grup üyelerince savunulabilir olmalıdır.

Kaynak: ETAI Project - 2627, bölümler II–VI. PDF yerel olarak incelenmiştir; repoya kopyalanmamıştır.
