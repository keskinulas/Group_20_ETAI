# Group_20_ETAI

ETAI projesi — Grup 20, 2026/27 akademik yılı.

Amaç: bir satın alma için tekrar alışveriş olasılığını, sınıflandırma kararını ve harcama tahminini üretmek.

## Durum

Bu ilk commit yalnızca proje yapılandırmasını içerir. `src/` kodu ve notebook'lar henüz eklenmemiştir; aşağıdaki eğitim ve tahmin komutları planlanan arayüzdür ve şu anda çalışmaz. Veri şeması, hedef sütunlar ve teslim gereksinimleri handbook ve CSV'ler incelendikten sonra kesinleştirilecektir.

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

Ham CSV dosyalarını yerel `data/raw/` klasörüne koyun. Dosya adlarını ve sütunları `config.yaml` içinde ayarlayın. Ham veri, sanal ortamlar, modeller ve üretilen çıktılar Git'e eklenmez. Tüm yapılandırma yolları repo köküne göredir.

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

`purchase.json` tek satın alma özelliklerini içeren bir JSON nesnesi olacaktır; gerekli alanlar veri şeması kesinleşince belgelenecektir. Tekil tahmin tekrar alışveriş olasılığını, yapılandırmadaki eşikle verilen kararı ve harcama tahminini döndürecektir. Toplu tahmin Kaggle ve harcama CSV'lerini ayrı dosyalara yazacaktır.

## Teslim

Repo adı `Group_20_ETAI` olarak belirlenmiştir. Paylaşılan bilgiye göre handbook teslim arşivi için `Group20_ETAI_2627.zip` adını kullanır; repo adı bu arşiv kuralını değiştirmez. Handbook henüz bu repoya sağlanmamıştır ve adlandırma onunla doğrulanacaktır. Nihai Kaggle CSV'si teslim arşivine ayrıca eklenecek ve `predict_batch.py` ile üretilen dosyayla eşleştiği kontrol edilecektir.
