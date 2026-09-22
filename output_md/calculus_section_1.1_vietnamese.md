# GIẢI TÍCH: CALCULUS (EARLY TRANSCENDENTALS - 9TH EDITION)

Tác giả: James Stewart, Daniel K. Clegg, Saleem Watson

Bản dịch tiếng Việt sư phạm - Tái hiện chuẩn xác bố cục, công thức LaTeX & đồ thị minh họa

---

<!-- ===== TRANG PDF 43 ===== -->

**8** $\qquad$ **CHƯƠNG 1** $\quad$ Hàm số và Mô hình

---

## 1.1 Bốn cách biểu diễn một hàm số

### ■ Hàm số

Hàm số xuất hiện bất cứ khi nào một đại lượng này phụ thuộc vào một đại lượng khác. Hãy xem xét bốn tình huống sau:

**A.** Diện tích $A$ của một hình tròn phụ thuộc vào bán kính $r$ của hình tròn đó. Mối liên hệ giữa $r$ và $A$ được xác định bởi công thức $A = \pi r^2$. Ứng với mỗi số dương $r$, ta luôn xác định được duy nhất một giá trị $A$ tương ứng, và ta nói rằng $A$ là một *hàm số* của $r$.

**B.** Dân số thế giới $P$ phụ thuộc vào thời gian $t$. Bảng 1 cung cấp số liệu ước tính về dân số thế giới $P$ tại các mốc thời gian $t$ trong một số năm nhất định. Chẳng hạn,
$$P \approx 2{,}560{,}000{,}000 \quad \text{khi } t = 1950$$
Ứng với mỗi giá trị của thời gian $t$, luôn có một giá trị tương ứng của $P$, và ta nói rằng $P$ là một hàm số của $t$.

##### Bảng 1: Dân số thế giới

| Năm | Dân số (triệu người) |
| :---: | :---: |
| 1900 | 1650 |
| 1910 | 1750 |
| 1920 | 1860 |
| 1930 | 2070 |
| 1940 | 2300 |
| 1950 | 2560 |
| 1960 | 3040 |
| 1970 | 3710 |
| 1980 | 4450 |
| 1990 | 5280 |
| 2000 | 6080 |
| 2010 | 6870 |

**C.** Cước phí bưu điện $C$ để gửi một phong bì phụ thuộc vào trọng lượng $w$ của nó. Dù không có một công thức toán học đơn giản nào biểu diễn trực tiếp mối quan hệ giữa $w$ và $C$, bưu điện vẫn có một bảng quy tắc rõ ràng để xác định giá trị của $C$ khi biết trước $w$.

**D.** Gia tốc thẳng đứng $a$ của mặt đất đo được bởi một địa chấn kế trong suốt một trận động đất là một hàm số theo thời gian trôi qua $t$. Hình 1 thể hiện đồ thị ghi lại hoạt động địa chấn trong trận động đất Northridge làm rung chuyển Los Angeles vào năm 1994. Với một giá trị thời gian $t$ cho trước, đồ thị cung cấp cho ta một giá trị gia tốc $a$ tương ứng.

![Gia tốc thẳng đứng của mặt đất trong trận động đất Northridge](images/page_0008_figure_1.png)
**HÌNH 1** Gia tốc thẳng đứng của mặt đất trong trận động đất Northridge.  
*(Nguồn: Cục Địa chất và Mỏ California - Calif. Dept. of Mines and Geology)*

> **[Mô tả trực quan của đồ thị]:**  
> Đồ thị địa chấn biểu diễn dao động với trục hoành là thời gian $t$ (tính bằng giây, từ $0$ đến hơn $30\text{ s}$) và trục tung là gia tốc thẳng đứng $a$ (đơn vị $\text{cm/s}^2$, từ $-50$ đến trên $100\text{ cm/s}^2$). Trong 5 giây đầu, đường ghi nhận dao động nhẹ quanh mức 0. Từ giây thứ 8 đến giây thứ 22, các xung chấn bùng nổ dữ dội với mật độ sóng dày đặc, đạt đỉnh xung cực đại vượt mốc $100\text{ cm/s}^2$ ở khoảng giây thứ 17–18, sau đó biên độ sóng suy giảm dần khi thời gian tiến về sau mốc 30 giây.

Mỗi ví dụ trên đều mô tả một quy tắc sao cho khi cho trước một số ($r$ trong Ví dụ A), một giá trị số khác ($A$) sẽ được xác định tương ứng. Trong mỗi trường hợp, ta nói rằng số thứ hai là một hàm số của số thứ nhất. Nếu dùng chữ cái $f$ để đại diện cho quy tắc liên hệ giữa $A$ và $r$ trong Ví dụ A, ta biểu diễn mối liên hệ này bằng **ký hiệu hàm số** là $A = f(r)$.

> [!NOTE] **ĐỊNH NGHĨA**
> Một **hàm số** $f$ là một quy tắc đặt tương ứng mỗi phần tử $x$ thuộc một tập hợp $D$ với duy nhất một phần tử, ký hiệu là $f(x)$, thuộc một tập hợp $E$.

Chúng ta thường khảo sát các hàm số mà các tập hợp $D$ và $E$ đều là tập hợp các số thực. Tập hợp $D$ được gọi là **tập xác định** (*domain*) của hàm số. Số $f(x)$ được gọi là **giá trị của $f$ tại $x$** và được đọc là "$f$ của $x$" (hay "$f$ tại $x$"). **Tập giá trị** (*range*) của $f$ là tập hợp tất cả các giá trị có thể có của $f(x)$ khi $x$ biến thiên trên toàn bộ tập xác định...

---

<!-- ===== TRANG PDF 44 ===== -->

**MỤC 1.1** Bốn cách biểu diễn một hàm số | **9**

---

...trên toàn bộ tập xác định. Một ký hiệu đại diện cho một số tùy ý thuộc *tập xác định* của hàm số $f$ được gọi là một **biến độc lập** (*independent variable*). Một ký hiệu đại diện cho một số thuộc *tập giá trị* của $f$ được gọi là một **biến phụ thuộc** (*dependent variable*). Chẳng hạn, trong Ví dụ A, $r$ là biến độc lập và $A$ là biến phụ thuộc.

![Sơ đồ máy móc cho một hàm số f](images/figure_2.png)
**HÌNH 2** Sơ đồ cỗ máy cho một hàm số $f$  
> **[Mô tả trực quan của đồ thị]:** Sơ đồ khối mô tả hàm số dưới dạng một cỗ máy hình hộp mang nhãn $f$. Mũi tên bên trái đưa dữ liệu đầu vào $x$ (input) vào cỗ máy, và mũi tên bên phải đưa ra kết quả đầu ra $f(x)$ (output).

Sẽ rất trực quan và hữu ích nếu ta xem một hàm số như một **cỗ máy** (xem Hình 2). Nếu $x$ thuộc tập xác định của hàm số $f$, thì khi $x$ đi vào cỗ máy, nó được tiếp nhận như một **đầu vào** (*input*) và cỗ máy sẽ tạo ra một **đầu ra** (*output*) là $f(x)$ tuân theo quy tắc xác định của hàm số đó. Do vậy, ta có thể hình dung tập xác định là tập hợp của tất cả các đầu vào khả dĩ, còn tập giá trị là tập hợp của tất cả các đầu ra có thể nhận được. Các hàm được lập trình sẵn trong máy tính cầm tay là những ví dụ điển hình cho mô hình cỗ máy này. Chẳng hạn, nếu bạn nhập một số rồi nhấn phím bình phương, máy tính sẽ hiển thị kết quả đầu ra là bình phương của số vừa nhập.

![Sơ đồ mũi tên cho f](images/figure_3.png)
**HÌNH 3** Sơ đồ mũi tên cho hàm số $f$  
> **[Mô tả trực quan của đồ thị]:** Sơ đồ ánh xạ gồm hai tập hợp dạng hình oval: tập xác định $D$ ở bên trái chứa các phần tử $x, a$ và tập $E$ ở bên phải chứa các phần tử $f(x), f(a)$. Các mũi tên hướng từ $x$ sang $f(x)$ và từ $a$ sang $f(a)$, với mũi tên lớn $f$ ở phía dưới nối từ tập $D$ sang tập $E$.

Một cách khác để hình dung về hàm số là sử dụng **sơ đồ mũi tên** (*arrow diagram*) như trong Hình 3. Mỗi mũi tên nối một phần tử thuộc $D$ với một phần tử thuộc $E$. Mũi tên chỉ ra rằng $f(x)$ tương ứng với $x$, $f(a)$ tương ứng với $a$, và cứ tiếp tục như vậy.

Có lẽ phương pháp hữu ích nhất để trực quan hóa một hàm số là vẽ đồ thị của nó. Nếu $f$ là một hàm số với tập xác định $D$, thì **đồ thị** (*graph*) của hàm số là tập hợp các cặp có thứ tự:

$$\{ (x, f(x)) \mid x \in D \}$$

(Lưu ý rằng đây chính là các cặp giá trị đầu vào – đầu ra.) Nói cách khác, đồ thị của $f$ bao gồm tất cả các điểm $(x, y)$ trên mặt phẳng tọa độ sao cho $y = f(x)$ và $x$ thuộc tập xác định của $f$.

Đồ thị của một hàm số $f$ đem lại cho ta một bức tranh trực quan hữu ích về hành vi hay "tiến trình biến thiên" của hàm số đó. Do tọa độ $y$ của bất kỳ điểm $(x, y)$ nào trên đồ thị đều là $y = f(x)$, ta có thể đọc giá trị của $f(x)$ từ đồ thị bằng chính độ cao của đồ thị nằm phía trên điểm $x$ (xem Hình 4). Đồ thị của $f$ cũng cho phép ta hình dung trực quan tập xác định của $f$ trên trục hoành ($x$) và tập giá trị của nó trên trục tung ($y$) như minh họa trong Hình 5.

---

| ![Độ cao của đồ thị biểu thị giá trị f(x)](images/figure_4.png) | ![Tập xác định và tập giá trị trên đồ thị](images/figure_5.png) |
| :--- | :--- |
| **HÌNH 4** | **HÌNH 5** |
| **[Mô tả trực quan của đồ thị]:** Đồ thị một đường cong $y = f(x)$ uốn lượn trên góc phần tư thứ nhất. Các đoạn thẳng đứng hạ từ đường cong xuống trục hoành tại $x = 1, 2, x$ minh họa độ dài đại số tương ứng là $f(1), f(2), f(x)$, với điểm trên đồ thị có tọa độ $(x, f(x))$. | **[Mô tả trực quan của đồ thị]:** Đường cong $y = f(x)$ nằm giữa hai điểm đầu mút. Đoạn giới hạn bởi các đường dóng nét đứt xuống trục $x$ biểu thị tập xác định (*domain*), và đoạn giới hạn bởi các đường dóng nét đứt sang trục $y$ biểu thị tập giá trị (*range*). |

---

### 📌 VÍ DỤ 1
Đồ thị của một hàm số $f$ được cho trong Hình 6.
- (a) Tìm các giá trị của $f(1)$ và $f(5)$.
- (b) Tập xác định và tập giá trị của $f$ là gì?

![Đồ thị hàm số f trên lưới tọa độ vuông](images/figure_6.png)  
**HÌNH 6**  
> **[Mô tả trực quan của đồ thị]:** Hệ lưới tọa độ vuông với gốc $O(0,0)$ và các vạch chia đơn vị. Đồ thị hàm số bắt đầu từ điểm $(0, 1)$, đi lên đạt đỉnh tại điểm $(1, 3)$, uốn cong đi xuống cắt trục hoành tại khoảng $x \approx 4{,}2$, chạm đáy cực tiểu tại $(6, -2)$, rồi đi lên và kết thúc tại điểm có hoành độ $x = 7$, tung độ $y = 1$.

> [!NOTE]
> *Ghi chú bên lề:* Ký hiệu các khoảng, đoạn được trình bày trong Phụ lục A.

**Lời giải:**

**(a)** Từ Hình 6, ta thấy điểm $(1, 3)$ nằm trên đồ thị của $f$, do đó giá trị của $f$ tại $1$ là $f(1) = 3$. (Nói cách khác, điểm trên đồ thị nằm thẳng phía trên $x = 1$ cách trục $x$ một khoảng bằng $3$ đơn vị.)

Khi $x = 5$, đồ thị nằm bên dưới trục $x$ khoảng $0{,}7$ đơn vị, vì vậy ta ước lượng được $f(5) \approx -0{,}7$.

**(b)** Ta thấy $f(x)$ được xác định khi $0 \le x \le 7$, do đó tập xác định của $f$ là đoạn đóng $[0, 7]$. Lưu ý rằng $f$ nhận tất cả các giá trị từ $-2$ đến $4$, vì thế tập giá trị của $f$ là

$$\{ y \mid -2 \le y \le 4 \} = [-2, 4] \quad \blacksquare$$

---

<!-- ===== TRANG PDF 45 ===== -->

**10** &emsp; **CHƯƠNG 1** &emsp; Hàm số và Mô hình

---

Trong giải tích, phương pháp phổ biến nhất để xác định một hàm số là thông qua một phương trình đại số. Ví dụ, phương trình $y = 2x - 1$ xác định $y$ là một hàm số theo $x$. Ta có thể biểu diễn hàm này dưới dạng ký hiệu hàm số là $f(x) = 2x - 1$.

### 📌 VÍ DỤ 2
Vẽ đồ thị, đồng thời tìm tập xác định và tập giá trị của mỗi hàm số sau:
**(a)** $f(x) = 2x - 1$  
**(b)** $g(x) = x^2$

**Lời giải:**

**(a)** Phương trình của đồ thị là $y = 2x - 1$, và ta dễ dàng nhận ra đây là phương trình của một đường thẳng có hệ số góc bằng $2$ và tung độ gốc bằng $-1$. (Hãy nhớ lại dạng phương trình đường thẳng theo hệ số góc và tung độ gốc: $y = mx + b$. Xem Phụ lục B.) Điều này cho phép chúng ta phác thảo một phần đồ thị của hàm số $f$ như trong Hình 7. Biểu thức $2x - 1$ xác định với mọi số thực, do đó tập xác định của $f$ là tập hợp tất cả các số thực, ký hiệu là $\mathbb{R}$. Đồ thị cũng cho thấy tập giá trị của hàm số là $\mathbb{R}$.

![Đồ thị hàm số y = 2x - 1](images/figure_7.png)  
*HÌNH 7*  
> **[Mô tả trực quan của đồ thị]:** Đồ thị là một đường thẳng đi lên từ góc phần tư thứ ba sang góc phần tư thứ nhất, cắt trục tung tại điểm $(0, -1)$ và cắt trục hoành tại điểm $\left(\frac{1}{2}, 0\right)$.

**(b)** Vì $g(2) = 2^2 = 4$ và $g(-1) = (-1)^2 = 1$, ta có thể chấm các điểm $(2, 4)$ và $(-1, 1)$ cùng với một vài điểm khác trên hệ trục tọa độ, sau đó nối các điểm lại để tạo thành đồ thị (Hình 8). Phương trình của đồ thị là $y = x^2$, biểu diễn một đường parabol (xem Phụ lục C). Tập xác định của $g$ là $\mathbb{R}$. Tập giá trị của $g$ bao gồm tất cả các giá trị của $g(x)$, tức là tất cả các số có dạng $x^2$. Nhưng $x^2 \ge 0$ với mọi số $x$, và mọi số dương $y$ đều là bình phương của một số nào đó. Do đó, tập giá trị của hàm số $g$ là $\{y \mid y \ge 0\} = [0, \infty)$. Điều này cũng được thể hiện trực quan trên Hình 8. $\blacksquare$

![Đồ thị parabol y = x^2](images/figure_8.png)  
*HÌNH 8*  
> **[Mô tả trực quan của đồ thị]:** Đồ thị là một đường cong parabol có đỉnh tại gốc tọa độ $(0, 0)$, bề lõm quay lên trên, đối xứng qua trục tung $y$. Trên đồ thị thể hiện rõ các điểm $(-1, 1)$, $(0, 0)$, $(1, 1)$ và $(2, 4)$.

---

### 📌 VÍ DỤ 3
Nếu $f(x) = 2x^2 - 5x + 1$ và $h \ne 0$, hãy tính giá trị của biểu thức $\dfrac{f(a + h) - f(a)}{h}$.

> [!NOTE] **GHI CHÚ BÊN LỀ**  
> Biểu thức
> $$\frac{f(a + h) - f(a)}{h}$$
> trong Ví dụ 3 được gọi là **thương sai phân** (*difference quotient*) và xuất hiện rất thường xuyên trong giải tích. Như chúng ta sẽ thấy trong Chương 2, nó biểu thị tốc độ biến thiên trung bình của hàm số $f(x)$ giữa $x = a$ và $x = a + h$.

**Lời giải:**  
Trước tiên, ta tính $f(a + h)$ bằng cách thay $x$ bởi $a + h$ vào biểu thức của $f(x)$:

$$
\begin{aligned}
f(a + h) &= 2(a + h)^2 - 5(a + h) + 1 \\
&= 2(a^2 + 2ah + h^2) - 5(a + h) + 1 \\
&= 2a^2 + 4ah + 2h^2 - 5a - 5h + 1
\end{aligned}
$$

Sau đó, ta thế vào biểu thức đã cho và rút gọn:

$$
\begin{aligned}
\frac{f(a + h) - f(a)}{h} &= \frac{(2a^2 + 4ah + 2h^2 - 5a - 5h + 1) - (2a^2 - 5a + 1)}{h} \\
&= \frac{2a^2 + 4ah + 2h^2 - 5a - 5h + 1 - 2a^2 + 5a - 1}{h} \\
&= \frac{4ah + 2h^2 - 5h}{h} = 4a + 2h - 5 \quad \blacksquare
\end{aligned}
$$

---

### ■ Các biểu diễn của hàm số

Chúng ta xem xét bốn phương pháp khác nhau để biểu diễn một hàm số:

* **bằng lời** (mô tả bằng câu chữ)
* **bằng số liệu** (bằng một bảng giá trị)
* **bằng hình ảnh trực quan** (bằng đồ thị)
* **bằng đại số** (bằng một công thức giải tích tường minh)

Nếu một hàm số có thể được biểu diễn bằng cả bốn phương pháp trên, việc chuyển đổi linh hoạt qua lại giữa các cách biểu diễn sẽ mang lại cái nhìn sâu sắc hơn về bản chất của hàm số đó. (Chẳng hạn, trong Ví dụ 2, chúng ta đã xuất phát từ công thức đại số rồi sau đó vẽ được đồ thị.) Tuy nhiên, một số hàm số nhất định lại được mô tả tự nhiên hơn bằng phương pháp này thay vì phương pháp khác. Với tinh thần đó, chúng ta hãy cùng xem xét lại bốn tình huống đã nêu ở phần mở đầu của mục này.

---

<!-- ===== TRANG PDF 46 ===== -->

**MỤC 1.1** Bốn cách biểu diễn một hàm số &emsp;|&emsp; **Trang 11**

---

**A.** Cách biểu diễn hữu ích nhất cho diện tích của một hình tròn theo bán kính có lẽ là công thức đại số $A = \pi r^2$ hoặc, theo ký hiệu hàm số, $A(r) = \pi r^2$. Ta cũng có thể lập một bảng giá trị hoặc phác họa đồ thị (một nhánh của parabol). Vì một hình tròn bắt buộc phải có bán kính dương, nên tập xác định là $\{r \mid r > 0\} = (0, \infty)$ và tập giá trị cũng là $(0, \infty)$.

**B.** Ta xét một hàm số được mô tả bằng lời: $P(t)$ là dân số của thế giới tại thời điểm $t$. Hãy chọn mốc đo thời gian $t$ sao cho $t = 0$ ứng với năm 1900. Bảng 2 cung cấp một cách biểu diễn thuận tiện cho hàm số này. 

##### **Bảng 2** Dân số thế giới

| $t$ (năm tính từ 1900) | Dân số (triệu người) |
| :---: | :---: |
| $0$ | $1650$ |
| $10$ | $1750$ |
| $20$ | $1860$ |
| $30$ | $2070$ |
| $40$ | $2300$ |
| $50$ | $2560$ |
| $60$ | $3040$ |
| $70$ | $3710$ |
| $80$ | $4450$ |
| $90$ | $5280$ |
| $100$ | $6080$ |
| $110$ | $6870$ |

Nếu ta biểu diễn các cặp giá trị có thứ tự trong bảng lên hệ tọa độ, ta thu được đồ thị (gọi là *biểu đồ phân tán* hay *scatter plot*) như ở Hình 9. Đây cũng là một cách biểu diễn rất hữu ích; đồ thị giúp chúng ta nắm bắt trực quan toàn bộ dữ liệu cùng một lúc. 

Thế còn việc biểu diễn bằng một công thức thì sao? Tất nhiên, ta không thể tìm ra một công thức tường minh hoàn hảo biểu diễn chính xác tuyệt đối dân số thế giới $P(t)$ tại mọi thời điểm $t$. Tuy nhiên, ta hoàn toàn có thể tìm được một biểu thức hàm số dùng để *xấp xỉ* $P(t)$. Thực tế, sử dụng các phương pháp được giải thích ở Mục 1.4, ta thu được một hàm số xấp xỉ cho dân số $P$:

$$P(t) \approx f(t) = (1.43653 \times 10^9) \cdot (1.01395)^t$$

Hình 10 cho thấy hàm số này "khớp" (fit) khá tốt với dữ liệu thực tế. Hàm số $f$ được gọi là một *mô hình toán học* (mathematical model) mô tả sự tăng trưởng dân số. Nói cách khác, đây là một hàm số có công thức tường minh giúp mô phỏng lại xu hướng biến thiên của hàm số đã cho. Tuy nhiên, sau này ta sẽ thấy rằng các ý tưởng của giải tích vẫn có thể áp dụng trực tiếp lên một bảng giá trị mà không nhất thiết phải có một công thức tường minh.

---

| ![Biểu đồ phân tán dân số](images/figure_9.png) | ![Đường cong mô hình khớp với dữ liệu](images/figure_10.png) |
| :---: | :---: |
| **HÌNH 9** | **HÌNH 10** |

> **[Mô tả trực quan của đồ thị Hình 9]:** Biểu đồ phân tán với trục hoành biểu diễn thời gian $t$ (số năm tính từ 1900, chia vạch từ 0 đến 120) và trục tung biểu diễn dân số $P$ (vạch mốc $5 \times 10^9$). Các điểm dữ liệu màu xanh rải rác tăng dần theo thời gian với độ dốc ngày càng lớn.
>
> **[Mô tả trực quan của đồ thị Hình 10]:** Cùng hệ trục tọa độ và các điểm dữ liệu như Hình 9, nhưng có thêm một đường cong màu đỏ biểu diễn hàm số mũ $f(t)$. Đường cong này bám sát quỹ đạo phân bố của các điểm dữ liệu, thể hiện xu hướng tăng trưởng nhanh của dân số.

---

> [!NOTE]
> Một hàm số được xác định bởi một bảng giá trị được gọi là một *hàm dạng bảng* (tabular function).

Hàm số $P$ là một ví dụ điển hình cho các loại hàm thường gặp khi chúng ta áp dụng giải tích vào thế giới thực. Ban đầu, ta xuất phát từ việc mô tả hàm số bằng lời. Kế tiếp, ta có thể lập bảng giá trị của hàm, chẳng hạn từ các số liệu đo đạc thực nghiệm khoa học. Mặc dù không có được sự hiểu biết toàn diện về mọi giá trị của hàm số, nhưng xuyên suốt cuốn sách này, bạn sẽ thấy rằng ta vẫn có thể thực hiện các phép toán của giải tích trên một hàm số như vậy.

##### **Bảng 3**

| $w$ (ounce) | $C(w)$ (đô la) |
| :---: | :---: |
| $0 < w \le 1$ | $1.00$ |
| $1 < w \le 2$ | $1.15$ |
| $2 < w \le 3$ | $1.30$ |
| $3 < w \le 4$ | $1.45$ |
| $4 < w \le 5$ | $1.60$ |
| $\vdots$ | $\vdots$ |

**C.** Một lần nữa, hàm số lại được mô tả bằng lời: Gọi $C(w)$ là chi phí gửi một phong bì lớn có khối lượng $w$. Quy định của Bưu điện Hoa Kỳ áp dụng từ năm 2019 như sau: Chi phí là $1$ đô la cho phong bì có khối lượng đến $1\text{ oz}$, cộng thêm $15\text{ cent}$ cho mỗi ounce (hoặc phần dư của ounce) tăng thêm cho đến tối đa $13\text{ oz}$. Một bảng giá trị là cách biểu diễn thuận tiện nhất cho hàm số này (xem Bảng 3), mặc dù ta cũng có thể phác họa đồ thị của nó (xem Ví dụ 10).

**D.** Đồ thị thể hiện ở Hình 1 là cách biểu diễn tự nhiên nhất cho hàm gia tốc thẳng đứng $a(t)$. Đúng là ta có thể lập một bảng giá trị và thậm chí có thể tìm một công thức xấp xỉ. Nhưng tất cả những gì một nhà địa chất học cần...

---

<!-- ===== TRANG PDF 47 ===== -->

**12** CHƯƠNG 1 &nbsp;|&nbsp; Hàm số và Mô hình

---

biết—chẳng hạn như biên độ và chu kỳ dao động—đều có thể quan sát một cách trực quan từ đồ thị. (Điều này cũng hoàn toàn đúng với các dạng sóng trên điện tâm đồ của bệnh nhân tim mạch hoặc máy phát hiện nói dối.)

Trong ví dụ tiếp theo, chúng ta sẽ phác họa đồ thị của một hàm số được mô tả bằng lời.

---

### 📌 VÍ DỤ 4
Khi bạn mở một vòi nước nóng được nối với bình nước nóng, nhiệt độ $T$ của nước chảy ra phụ thuộc vào thời gian vòi nước đã chảy. Hãy vẽ đồ thị phác thảo của nhiệt độ $T$ theo biến thời gian $t$ tính từ thời điểm bắt đầu mở vòi.

![Đồ thị biểu diễn nhiệt độ nước $T$ theo thời gian $t$](images/figure_11.png)
**HÌNH 11**  
> **[Mô tả trực quan của đồ thị]:** Đồ thị nằm trong góc phần tư thứ nhất trên hệ trục tọa độ với trục hoành là thời gian $t$ và trục tung là nhiệt độ $T$. Đường cong bắt đầu tại thời điểm $t = 0$ từ một giá trị $T > 0$ (nhiệt độ phòng), sau đó tăng vọt lên nhanh chóng, đạt tới một đoạn nằm ngang bằng phẳng ở mức nhiệt độ cao nhất (nhiệt độ nước nóng trong bình). Sau một khoảng thời gian, đường cong uốn cong đi xuống dốc rồi lại nằm ngang ở một mức nhiệt độ thấp hơn (nhiệt độ của nguồn cấp nước lạnh vào bình).

**Lời giải:**  
Nhiệt độ ban đầu của dòng nước chảy ra xấp xỉ bằng nhiệt độ phòng do lượng nước này vốn đọng lại trong đường ống từ trước. Khi nước từ bình nước nóng bắt đầu chảy tới vòi, nhiệt độ $T$ sẽ tăng lên rất nhanh. Ở giai đoạn kế tiếp, $T$ giữ ở mức ổn định ứng với nhiệt độ của nước đã được làm nóng trong bình. Khi lượng nước nóng trong bình cạn kiệt, $T$ giảm dần về bằng nhiệt độ của nguồn nước cấp vào. Phân tích này cho phép chúng ta vẽ phác thảo đồ thị của $T$ theo biến $t$ như minh họa trong **Hình 11**. $\blacksquare$

---

Trong ví dụ dưới đây, chúng ta xuất phát từ mô tả bằng lời về một tình huống vật lý để thiết lập nên một công thức đại số tường minh. Kỹ năng thiết lập hàm số này là một công cụ đặc biệt hữu ích khi giải quyết các bài toán vi tích phân yêu cầu tìm giá trị lớn nhất hoặc giá trị nhỏ nhất của các đại lượng.

---

> [!TIP]
> **PS** Khi thiết lập các hàm số ứng dụng thực tế như trong Ví dụ 5, việc xem lại các nguyên tắc giải quyết vấn đề ở cuối chương này là rất hữu ích, đặc biệt là *Bước 1: Hiểu bài toán*.

### 📌 VÍ DỤ 5
Một thùng chứa hình hộp chữ nhật không có nắp đậy có thể tích bằng $10\text{ m}^3$. Chiều dài đáy gấp đôi chiều rộng đáy. Chi phí vật liệu làm đáy là $\$10$ cho mỗi mét vuông; chi phí vật liệu làm các mặt bên là $\$6$ cho mỗi mét vuông. Hãy biểu diễn tổng chi phí vật liệu dưới dạng một hàm số theo chiều rộng của đáy.

![Hình hộp chữ nhật đáy có kích thước $w$, $2w$ và chiều cao $h$](images/figure_12.png)
**HÌNH 12**  
> **[Mô tả trực quan của hình học]:** Khối hộp chữ nhật không có nắp trên. Đáy hộp nằm ngang có chiều rộng được ký hiệu là $w$, chiều dài là $2w$. Chiều cao thẳng đứng của hình hộp là $h$. Các đường nét đứt biểu diễn các cạnh khuất bên trong hộp.

**Lời giải:**  
Ta vẽ hình minh họa như trong **Hình 12** và đưa vào các ký hiệu: gọi $w$ và $2w$ lần lượt là chiều rộng và chiều dài của mặt đáy, và $h$ là chiều cao của thùng chứa.

Diện tích của đáy là $(2w)w = 2w^2$, do đó chi phí (tính bằng đô la) của vật liệu làm đáy là $10(2w^2)$. Hai mặt bên đối diện có diện tích là $wh$ và hai mặt bên còn lại có diện tích là $2wh$, vì thế chi phí vật liệu làm bốn mặt bên là $6[2(wh) + 2(2wh)]$. Tổng chi phí vật liệu do đó bằng:

$$C = 10(2w^2) + 6[2(wh) + 2(2wh)] = 20w^2 + 36wh$$

Để biểu diễn chi phí $C$ chỉ theo một biến duy nhất là $w$, ta cần khử biến $h$. Ta thực hiện điều này bằng cách sử dụng giả thiết thể tích của khối hộp là $10\text{ m}^3$:

$$w(2w)h = 10$$

Suy ra:

$$h = \frac{10}{2w^2} = \frac{5}{w^2}$$

Thay biểu thức của $h$ vào biểu thức của $C$, ta được:

$$C = 20w^2 + 36w\left(\frac{5}{w^2}\right) = 20w^2 + \frac{180}{w}$$

Như vậy, phương trình:

$$C(w) = 20w^2 + \frac{180}{w} \quad (w > 0)$$

biểu diễn chi phí $C$ dưới dạng một hàm số của chiều rộng $w$. $\blacksquare$

---

Trong ví dụ tiếp theo, chúng ta sẽ tìm tập xác định của một hàm số được xác định bởi biểu thức đại số. Nếu một hàm số được cho bởi một công thức mà tập xác định không được nêu rõ ràng, chúng ta sẽ áp dụng quy ước...

---
