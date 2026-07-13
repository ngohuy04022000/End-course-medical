# Dự đoán mảng xơ vữa động mạch cảnh bằng mô hình đa mô thức

Bài tập cuối môn **Xử lý tín hiệu và hình ảnh y khoa**.

Dự án xây dựng mô hình dự đoán sự hiện diện của mảng xơ vữa (`Plaque_present`) trên 300 bệnh nhân,
kết hợp **ảnh siêu âm động mạch cảnh** (nhánh CNN) và **dữ liệu lâm sàng dạng bảng** (nhánh MLP).
Trọng tâm của bài là **phát hiện và loại bỏ rò rỉ dữ liệu (data leakage)** — nếu không xử lý,
mô hình đạt accuracy ~100% hoàn toàn giả tạo.

---

## 1. Dữ liệu

| Hạng mục | Giá trị |
|---|---|
| Số bệnh nhân | 300 |
| Không có mảng xơ vữa (Control) | 205 |
| Có mảng xơ vữa (Plaque) | 95 (mất cân bằng ~2.2:1) |
| Độ hồi âm mảng xơ vữa | Intermediate 40, Low 28, High 27 |
| Phân loại nguy cơ nền | Low 293, Moderate 7 |
| Ảnh siêu âm | 205 ca có 1 ảnh, 95 ca có 5 ảnh |

Các biến lâm sàng: `Age`, `Sex`, `Lp(a)`, `ApoB`, `LDL_C`, `Triglyceride`, `Total_Cholesterol`,
`Non_HDL`, `IMT_mm`.

**Feature bổ sung — SCORE2 / SCORE2-OP:** điểm nguy cơ tim mạch 10 năm theo ESC
(SCORE2 cho tuổi 40–69, SCORE2-OP cho tuổi ≥70, vùng nguy cơ thấp), tính từ tuổi, giới,
non-HDL cholesterol. SCORE2 trung bình ở nhóm Plaque là **0.340** so với **0.186** ở nhóm Control.

---

## 2. ⚠️ Kiểm tra tính toàn vẹn dữ liệu (Data Integrity Audit)

Đây là phát hiện quan trọng nhất của dự án. Bốn nguồn rò rỉ đã được xác định và loại bỏ:

| Nguồn rò rỉ | Vấn đề | Cách xử lý |
|---|---|---|
| **Số lượng ảnh** | Control có đúng 1 ảnh, Plaque có đúng 5 ảnh → **correlation với nhãn = 1.0000** | Chỉ dùng ảnh `_IMT.png` (mọi bệnh nhân đều có) |
| Ảnh `CCA_L/R` | Chỉ tồn tại ở ca Plaque → sự tồn tại của file ảnh chính là nhãn | Loại khỏi mô hình |
| `Plaque_echogenicity` | Chỉ có giá trị ở ca Plaque | Không dùng làm feature |
| `Baseline_Risk_Score` | Điểm nguy cơ tính sẵn, có thể chứa thông tin nhãn | Không dùng làm feature |

Sau khi sửa, phân tích cho thấy **ảnh IMT gần như là nhiễu**: phân phối pixel hai lớp gần trùng nhau
(mean 128.7 ± 16.4 ở Control so với 129.6 ± 17.0 ở Plaque). Tín hiệu dự đoán thực sự nằm ở dữ liệu bảng:

| Feature | Tương quan với nhãn |
|---|---|
| `IMT_mm` | 0.354 |
| `Age` | 0.332 |
| `SCORE2` | 0.214 |
| `Lp(a)` | 0.099 |
| Các lipid còn lại | < 0.09 |

---

## 3. Mô hình và thiết kế thí nghiệm

**Kiến trúc đa mô thức:** nhánh CNN nhẹ (3 block conv + BatchNorm + Dropout 0.5) xử lý ảnh IMT
128×128 grayscale, nhánh MLP xử lý 10 feature bảng, hai nhánh được nối (concatenate) trước lớp phân loại.

Các kỹ thuật chống overfit và đánh giá công bằng:

| Vấn đề | Giải pháp |
|---|---|
| Mất cân bằng lớp (2.2:1) | `pos_weight = neg/pos` trong `BCEWithLogitsLoss` |
| Overfit trên dữ liệu nhỏ | `weight_decay=3e-4`, BatchNorm, augmentation, early stopping (patience=30) |
| Optimizer | AdamW + `CosineAnnealingLR` + gradient clipping |
| Threshold cố định 0.5 | Threshold tối ưu F1 chọn trên validation fold / OOF |
| Đánh giá thiên lệch | **5-Fold Stratified CV** trên dev set + test set cố định 10% |
| Scaler fit trên toàn bộ dữ liệu | Scaler fit **riêng từng fold** |

Chia dữ liệu: **dev 270 mẫu** (184 control / 86 plaque) cho cross-validation, **test 30 mẫu**
(21 control / 9 plaque) giữ nguyên đến cuối. Huấn luyện trên GPU (CUDA).

---

## 4. Kết quả

### 5-Fold Cross-Validation (trên dev set)

| Metric | Trung bình ± độ lệch chuẩn |
|---|---|
| Accuracy | 0.685 ± 0.114 |
| F1 | 0.604 ± 0.092 |
| Precision | 0.558 ± 0.206 |
| Recall | 0.722 ± 0.138 |
| **AUC-ROC** | **0.715 ± 0.080** |

Out-of-fold (gộp 5 fold): **AUC = 0.705**, AUPRC = 0.601, best F1 = 0.561 tại threshold 0.470.
Threshold này được chốt từ OOF, **không nhìn vào test set**.

### Test set — ensemble 5 fold (threshold 0.470)

| | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| Control | 0.818 | 0.857 | 0.837 | 21 |
| Plaque | 0.625 | 0.556 | 0.588 | 9 |
| **Accuracy** | | | **0.767** | 30 |

**AUC-ROC = 0.735**, AUPRC = 0.635.

### So sánh với baseline tabular cổ điển

Tất cả dùng chung split CV để so sánh công bằng:

| Model | CV AUC (OOF) | Test AUC | Test AUPRC |
|---|---|---|---|
| **Multimodal (ensemble)** | **0.705** | **0.735** | **0.635** |
| Logistic Regression | 0.690 | 0.714 | 0.587 |
| Gradient Boosting | 0.668 | 0.476 | 0.495 |
| Random Forest | 0.649 | 0.651 | 0.585 |

### Nhận xét

- Mô hình đa mô thức **nhỉnh hơn** các baseline tabular, nhưng khoảng cách với Logistic Regression
  là nhỏ (CV AUC 0.705 so với 0.690) — đúng như dự đoán, vì ảnh IMT mang rất ít tín hiệu.
- **Fold-ensemble** (trung bình xác suất 5 model) tốt hơn chọn 1 fold tốt nhất: F1 test tăng từ 0.56 lên 0.63.
- AUC ~0.71–0.74 là mức **thực tế** cho bài toán này sau khi loại rò rỉ. Con số ~100% ban đầu
  chỉ phản ánh việc mô hình học được "bệnh nhân này có 5 ảnh hay 1 ảnh".
- Recall trên lớp Plaque (0.556 trên test) còn thấp — hạn chế chính là kích thước dữ liệu
  (chỉ 95 ca dương tính) và việc ảnh siêu âm không đóng góp tín hiệu phân biệt.

---

## 5. Cấu trúc dự án

```
clinical_carotid_dataset_v3/
├── carotid_clinical_dataset_300cases.csv    # Dữ liệu lâm sàng gốc (300 ca)
├── carotid_clinical_dataset_300cases.xlsx
├── CAROTID_IMAGES/                          # 680 ảnh siêu âm (*_IMT.png, *_CCA_L/R*.png)
├── carotid_multimodal_exploration.ipynb     # Notebook chính: EDA → audit → mô hình → biểu đồ
├── carotid_multimodal/                      # Package pipeline chuẩn hóa dữ liệu
│   ├── pipeline.py                          # load / validate / manifest / split / summary
│   └── __main__.py
├── outputs/                                 # Kết quả pipeline
│   ├── manifest.csv                         # 1 dòng / bệnh nhân, kèm đường dẫn ảnh
│   ├── splits.csv                           # Train 210 / Val 45 / Test 45 (stratified, seed=42)
│   └── summary.json                         # Thống kê + danh sách lỗi validation (0 lỗi)
└── notebook_outputs/                        # Checkpoint mô hình PyTorch
    ├── best_cv_ensemble.pt                  # Ensemble 5 fold (mô hình cuối)
    ├── best_cv_model.pt
    ├── best_improved_model.pt
    └── best_multimodal_model.pt
```

## 6. Cách chạy

**Notebook chính** (EDA, audit rò rỉ, huấn luyện, biểu đồ):

```powershell
Set-Location clinical_carotid_dataset_v3
jupyter notebook carotid_multimodal_exploration.ipynb
```

**Pipeline chuẩn hóa dữ liệu** (sinh lại `outputs/`):

```powershell
Set-Location clinical_carotid_dataset_v3
python -m carotid_multimodal
```

Tùy chọn đổi thư mục kết quả: `python -m carotid_multimodal --output-dir outputs_v2`

Yêu cầu: Python 3.11+, `torch`, `scikit-learn`, `pandas`, `numpy`, `matplotlib`, `pillow`.

---

## 7. Tài liệu tham khảo

- SCORE2 working group. *SCORE2 risk prediction algorithms.* Eur Heart J. 2021;42:2439–2454.
- SCORE2-OP working group. *SCORE2-OP risk prediction algorithms.* Eur Heart J. 2022;43:2444–2456.
