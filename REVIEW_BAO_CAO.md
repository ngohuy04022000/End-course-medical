# Review báo cáo — `Bao_cao_mon_hoc_da_cap_nhat_thong_tin_1.pdf`

**Ngày review:** 13/07/2026
**Phạm vi:** toàn bộ 96 trang, tập trung Chương 4 (Thực nghiệm) và Chương 5 (Thảo luận)
**Đối chiếu với:** `clinical_carotid_dataset_v3/carotid_multimodal_exploration.ipynb`,
`clinical_carotid_dataset_v3/outputs/splits.csv`, `outputs/manifest.csv`, `outputs/summary.json`

---

## Kết luận nhanh

Phần số học của báo cáo **chính xác**. Tôi đã tính lại toàn bộ các chỉ số dẫn xuất từ ma trận
nhầm lẫn được công bố (VLM, phát hiện trên Ar-PlaqSegm1, phân loại độ phản âm, Dice V2)
— tất cả đều khớp, không có số nào tự mâu thuẫn.

Các vấn đề tìm được đều thuộc nhóm **thiếu số liệu** hoặc **gán nhầm tập dữ liệu**, không phải
lỗi tính toán. Ba việc cần ưu tiên:

1. Xác định lại Bảng 4.1 được đánh giá trên tập validation hay tập test (bằng chứng thiên về **validation**).
2. Quyết định có đưa lần chạy notebook đa mô thức (kèm feature SCORE2) vào báo cáo hay không — hiện **hoàn toàn vắng mặt**.
3. Bổ sung khoảng tin cậy còn thiếu cho MMPFN, UCI và U-Net++.

---

## 1. 🔴 Nghiêm trọng — Bảng 4.1 có thể đang báo cáo trên tập validation, không phải test

Mục 4.2.3 (trang 33) tự ghi nhận mâu thuẫn:

> *"ma trận nhầm lẫn 31 TN và 14 TP tương ứng độ chính xác 1,0. Nhưng báo cáo ở một vị trí
> khác mô tả kiểm thử 30 âm và 15 dương. Sự khác biệt này cho thấy cần lưu trực tiếp danh
> sách mã bệnh nhân của mỗi cách chia tập."*

Tôi đã đếm trực tiếp từ `outputs/splits.csv` (chia 70/15/15, stratified, seed=42):

| Split | Âm tính (Control) | Dương tính (Plaque) | Tổng |
|---|---|---|---|
| train | 144 | 66 | 210 |
| **val** | **31** | **14** | **45** |
| **test** | **30** | **15** | **45** |

**Kết luận:** ma trận "31 TN + 14 TP" khớp **chính xác** với tập **validation**, không phải test.
Con số "30 âm / 15 dương" mới là tập test thật.

Điều này có nghĩa kết quả 1,0000 của *U-Net + Tích hợp đặc trưng* nhiều khả năng được đo
trên tập val — tức là trên chính tập đã dùng để chọn mô hình/ngưỡng. Đây là vấn đề nặng hơn
"ghi nhầm số": nó ảnh hưởng đến tính hợp lệ của toàn bộ Bảng 4.1 và Bảng 4.2.

**Hành động:** mở lại script sinh Bảng 4.1, xác nhận nó đọc split nào; nếu đúng là val thì phải
chạy lại trên test và cập nhật cả Bảng 4.1, 4.2, Hình 4.1, Bảng 4.9, Bảng 4.10 và Bảng 4.11 (câu hỏi 1).

---

## 2. 🔴 Toàn bộ lần chạy notebook đa mô thức không xuất hiện trong báo cáo

Grep toàn văn 96 trang: **không có** bất kỳ số nào dưới đây.

| Chỉ số (từ notebook) | Giá trị | Có trong báo cáo? |
|---|---|---|
| CV AUC 5 nếp (trung bình ± SD) | 0,7154 ± 0,0797 | ❌ |
| OOF AUC | 0,7054 | ❌ |
| OOF AUPRC | 0,6014 | ❌ |
| Test accuracy (ensemble 5 fold) | 0,7667 | ❌ |
| Test AUC | 0,7354 | ❌ |
| Test AUPRC | 0,6350 | ❌ |
| Ngưỡng chốt từ OOF | 0,470 | ❌ |
| **SCORE2 / SCORE2-OP** (feature) | corr = 0,214 với nhãn | ❌ (0 lần xuất hiện) |

Bảng 4.3 (đánh giá nghiêm ngặt) là một lần chạy **khác hẳn**: 3 lần lặp × 3 nếp, nhóm theo mã
băm ảnh IMT. Không thay thế được cho lần chạy 5-fold trong notebook.

Đáng chú ý nhất là **SCORE2** — điểm nguy cơ tim mạch 10 năm theo ESC, được tính trong
notebook (SCORE2 cho tuổi 40–69, SCORE2-OP cho ≥70), có tương quan 0,214 với nhãn,
đứng thứ 3 sau `IMT_mm` (0,354) và `Age` (0,332). Đây là đóng góp kỹ nghệ đặc trưng có căn
cứ y văn nhưng không được nhắc đến một dòng nào trong báo cáo.

**Hành động:** hoặc bổ sung một mục con vào §4.4 trình bày lần chạy này như một tầng bằng
chứng riêng, hoặc nêu rõ lý do nó bị thay thế bởi thiết lập nghiêm ngặt hơn.

---

## 3. 🟠 Các số liệu thiếu bên trong báo cáo

### 3.1 Mục 4.4.5 — thiếu khoảng tin cậy của MMPFN

CaroTAR được báo cáo đầy đủ: ∆AUROC = −0,0377, KTC 95% [−0,0939; −0,0040], p_bootstrap = 0,0098.

MMPFN thu gọn thì chỉ có: *"∆AUROC khoảng −0,0288 so với tổ hợp tham chiếu, nhưng khoảng
tin cậy vẫn chạm phía dương trong lần chạy trước"* — **không có con số KTC, không có p-value**.
Câu "trong lần chạy trước" cũng cho thấy số liệu chưa được cập nhật đồng bộ.

### 3.2 Mục 4.4.3 — thiếu bảng số theo nếp

Báo cáo tự viết: *"Việc chỉ báo cáo một giá trị AUC trung bình mà không trình bày phân bố theo
nếp có thể tạo ấn tượng chắc chắn quá mức."* Nhưng rồi chỉ đưa boxplot (Hình 4.6), **không có
bảng độ lệch chuẩn / min / max theo nếp cho từng mô hình**.

### 3.3 Bảng 4.4 — thiếu độ nhạy và độ đặc hiệu

Chỉ có Độ chính xác, Độ chính xác cân bằng, F1. Với bài toán sàng lọc, **độ nhạy là chỉ số quan
trọng nhất** và nó không có mặt. Cũng không nêu **ngưỡng phân loại** đã dùng để sinh bảng này.

### 3.4 Bảng 4.5 (UCI) — thiếu KTC và điểm Brier

Chỉ Logistic Regression có KTC (0,9149 [0,8803; 0,9422]). Extra Trees và RBF-SVM không có.
Mục 4.5 khẳng định *"hiệu chỉnh xác suất có thể vận hành trên dữ liệu lâm sàng thật"* nhưng
**không có điểm Brier hay ECE** để chứng minh.

Ngoài ra §4.5 chỉ có tiểu mục **4.5.1 Thiết lập** — không có tiểu mục kết quả, dù Bảng 4.5 tồn tại.
Lỗi cấu trúc mục lục.

### 3.5 Bảng 4.8 / 5.1 (U-Net++) — thiếu KTC bootstrap và thiếu kết quả từng bộ mã hóa

- **Không có KTC** cho Dice, IoU, tỷ lệ ảnh âm sạch. Chính danh mục kiểm tra ở **Bảng 5.2** của
  bạn đã liệt kê việc này ("Bổ sung KTC bootstrap cho Dice, IoU và tỷ lệ ảnh âm sạch của U-Net++")
  nhưng chưa thực hiện.
- **Chỉ có kết quả của tổ hợp**, không có ResNet34 riêng và EfficientNet-B3 riêng → không chứng
  minh được tổ hợp có ích. Đây đúng là thí nghiệm số 1 trong danh sách 5.6.2 "cần thực hiện".
- Không có siêu tham số huấn luyện (epoch, learning rate, loss, augmentation).

### 3.6 Mục 4.1 — thiếu thông tin tái lập

Báo cáo nói *"hạt giống ngẫu nhiên, cách chia tập và siêu tham số được lưu cùng kết quả"* nhưng
không in ra bất kỳ giá trị nào: **không có phiên bản thư viện, cấu hình GPU, số epoch, learning
rate, batch size, giá trị seed**. Với một báo cáo tham chiếu TRIPOD+AI / CLAIM (§5.7), đây là
thiếu sót đáng chú ý.

### 3.7 Phương trình 4.2 — ma trận độ phản âm không có nhãn hàng/cột

Ma trận `[[22,6,2],[3,30,2],[1,2,27]]` được in trần, không ghi thứ tự lớp. Tôi phải suy ngược từ
các giá trị F1 mới xác định được thứ tự hàng là **Thấp → Trung bình → Cao** (không phải thứ tự
trực giác Cao → Trung bình → Thấp):

| Lớp | TP | Precision | Recall | F1 | Khớp báo cáo? |
|---|---|---|---|---|---|
| Thấp (hàng 1) | 22 | 22/26 = 0,846 | 22/30 = **0,7333** | **0,7857** | ✅ "Thấp 78,57%", "độ nhạy 73,33%" |
| Trung bình (hàng 2) | 30 | 30/38 = 0,789 | 30/35 = 0,857 | **0,8220** | ✅ "Trung bình 82,20%" |
| Cao (hàng 3) | 27 | 27/31 = 0,871 | 27/30 = 0,900 | **0,8853** | ✅ "Cao 88,53%" |

Số liệu **đúng hoàn toàn**, nhưng người đọc sẽ hiểu ngược nếu không có nhãn. Cần thêm nhãn
hàng/cột và ghi rõ hàng = nhãn thật, cột = dự đoán.

### 3.8 VLM (§4.3) — thiếu AUC

Bảng 4.9 và §5.5.2 đã tự thừa nhận *"chưa có AUC và chỉ số ở cấp bệnh nhân"*. Chỉ số cấp bệnh
nhân thì đúng là không tính được (thiếu tệp ánh xạ ảnh → mã bệnh nhân), nhưng **AUC cấp ảnh
hoàn toàn tính được** từ xác suất đã lưu — không có lý do để thiếu.

---

## 4. 🟡 Hai chỗ nghi lỗi sao chép / trộn quy ước

### 4.1 Bảng 4.6 — hai dòng trùng số hệt nhau

| Phương pháp | AUROC | AUPRC |
|---|---|---|
| KNN toàn bộ k = 5 + SVM cổng điều phối | 0,8854 | 0,8836 |
| KNN dương k = 10 + cổng điều phối | **0,8854** | **0,8836** |

Nếu là do cả hai dùng chung cổng SVM để quyết định phát hiện (nên AUROC phát hiện giống
nhau là hợp lý), thì **phải ghi chú rõ**. Nếu không, trông như dán nhầm dòng.

### 4.2 Bảng 4.8 — trộn hai quy ước Dice trong cùng một bảng

- Cột **"Âm tính"**: Dice = 0,2083 và IoU = 0,2083. Nhưng 0,2083 = **5/24** = tỷ lệ ảnh âm sạch
  → đây là quy ước **V2**.
- Cột **"Toàn bộ Dice V1"** = 0,2853 = 24 × 0,5707 / 48 → tính ảnh âm bằng **0** → quy ước **V1**.

Một bảng đang dùng hai quy ước khác nhau mà không ghi chú. Cần tách rõ hoặc thêm chú thích.

- Ô **Độ chuẩn xác / Độ nhạy của ảnh âm = 0,0000**: thực chất là **không xác định** (ảnh âm không
  có điểm ảnh dương tham chiếu, mẫu số bằng 0). Việc đưa 0 này vào trung bình cột "Toàn bộ"
  (0,3147 = 0,6294 / 2) làm chỉ số **bị kéo xuống một cách nhân tạo**. Nên để dấu "—" và chỉ báo
  cáo giá trị trên ca dương.

---

## 5. Các chỉ số đã kiểm tra và xác nhận đúng

Để bạn yên tâm, đây là những phần tôi đã tính lại và **khớp hoàn toàn**:

| Mục | Kiểm tra | Kết quả |
|---|---|---|
| §4.3.2 VLM | TN=30, FP=11, FN=7, TP=88 → acc 86,76%; sens 92,63%; spec 73,17%; F1+ 90,72%; F1− 76,92%; bal-acc 82,90%; MCC 0,6785 | ✅ tất cả |
| §4.3.2 | Baseline "luôn dự đoán dương": acc 69,85% (95/136); F1+ 82,25% | ✅ |
| §4.3.3 | 136 ảnh = 19 BN dương × 5 ảnh + 41 BN âm × 1 ảnh = 60 bệnh nhân | ✅ |
| §4.3.4 | Ma trận độ phản âm → 3 giá trị F1 và độ nhạy 73,33% | ✅ (xem 3.7) |
| §4.6.2 | Ma trận [[17,7],[3,21]] → spec 0,7083; sens 0,8750; bal-acc 0,7917 | ✅ |
| §5.2.3 | Dice V2 = (24 × 0,5707 + 5 × 1 + 19 × 0) / 48 = 0,3895 | ✅ |
| §5.2.2 | Pixel accuracy 99,08–99,43% vs mảng xơ vữa chiếm 1,69% ảnh | ✅ lập luận đúng |
| Bảng 4.11 | AUROC 0,6706 cho CaroTAR + tổ hợp tham chiếu | ✅ khớp Bảng 4.3 |

Điểm mạnh đáng ghi nhận: báo cáo **tự phát hiện và tự công bố** nhiều điểm yếu của chính nó
(đường tắt thống kê từ số lượng góc chụp, ảnh trùng giữa train/test, nghịch lý AUC = 1 với độ
nhạy = 0, chuyển giao âm từ UCI). Đây là thái độ khoa học đúng và hiếm gặp ở báo cáo môn học.

---

## 6. Danh sách việc cần làm, xếp theo ưu tiên

| # | Việc | Mức độ | Mục liên quan |
|---|---|---|---|
| 1 | Xác nhận Bảng 4.1/4.2 chạy trên test hay val; chạy lại nếu cần | 🔴 | §4.2, §4.2.3 |
| 2 | Quyết định đưa lần chạy notebook 5-fold + SCORE2 vào báo cáo | 🔴 | §4.4 |
| 3 | Bổ sung KTC + p-value cho ∆AUROC của MMPFN | 🟠 | §4.4.5 |
| 4 | Bổ sung độ nhạy / độ đặc hiệu và ngưỡng vào Bảng 4.4 | 🟠 | §4.4.1 |
| 5 | Bổ sung KTC bootstrap cho Dice/IoU của U-Net++ | 🟠 | Bảng 4.8, 5.1 |
| 6 | Chạy ResNet34 và EfficientNet-B3 riêng để chứng minh giá trị của tổ hợp | 🟠 | §4.6.4, §5.6.2 |
| 7 | Bổ sung KTC cho Extra Trees, RBF-SVM và điểm Brier ở Bảng 4.5 | 🟠 | §4.5 |
| 8 | Thêm nhãn hàng/cột cho ma trận phương trình 4.2 | 🟡 | §4.3.4 |
| 9 | Tính AUC cấp ảnh cho VLM | 🟡 | §4.3.2 |
| 10 | Ghi chú hoặc sửa hai dòng trùng ở Bảng 4.6 | 🟡 | §4.6.3 |
| 11 | Tách quy ước V1/V2 và thay 0,0000 bằng "—" ở Bảng 4.8 | 🟡 | §4.6.4 |
| 12 | Bổ sung siêu tham số, seed, phiên bản thư viện, cấu hình GPU vào §4.1 | 🟡 | §4.1, §5.7 |
| 13 | Thêm tiểu mục kết quả cho §4.5 (hiện chỉ có 4.5.1 Thiết lập) | 🟡 | §4.5 |
