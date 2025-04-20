# STUDENT MANAGEMENT

Đây là một ứng dụng bao gồm cả backend và frontend, được xây dựng để phục vụ mục đích quản lý sinh viên đơn giản.

## Cấu trúc source code

Dự án được tổ chức như saui:
```bash
├── src/                  # Thư mục chứa mã nguồn chương trình
│   ├── images/           # Thư mục chứa các file hình ảnh cho game
│   ├── sounds/           # Thư mục chứa các file âm thanh cho game
│   ├── ghosts.py         # File chứa lớp của Ghost và các thuật toán tìm đường đi
│   ├── maze.py           # File chứa lớp maze và các định nghĩa cho bản đồ trò chơi
│   ├── main.py           # File chính chạy chương trình
│   ├── pacman.py         # File chứa lớp Pacman
│   ├── utils.py          # File chứa các thông tin liên quan tới việc thử nghiệm chương trình
│   ├── requirements.txt  # File chứa các thông tin về các thư viện cần cho trò chơi
│   ├── README.md         # File hướng dẫn chạy project
│
└── Report.pdf            # File báo cáo project
```
## Hướng dẫn cài đặt & chạy chương trình

### Yêu cầu
- Python đã được cài đặt trên máy của bạn.
- Một trình để code (như vs code hoặc vs).

### Các bước cài đặt
1.  **Cách 1:**
    Sử dụng github, clone repository sau về 
    ```bash
    git clone https://github.com/22120139/introAI.git
    ```
    Sau đó, tìm tới thư mục chứa file main.py, tiến hành cài đặt các thư viện cần thiết bằng lệnh
    ```bash
    pip install requirements.txt
    ```
    Hoặc có thể cài đặt thủ công
    ```bash
    pip install pygame numpy matplotlib
    ```
    Sau đó chạy lệnh 
    ```bash
    python main.py  
    ```
    Để kiểm tra các test case chạy lệnh
     ```bash
    python main.py --test  
    ```

2.  **Cách 2:**
    Giải nén file zip được gửi trên moodle, sau đó, tìm tới thư mục chứa file main.py, tiến hành cài đặt các thư viện cần thiết bằng lệnh
    ```bash
    pip install requirements.txt
    ```
    Hoặc có thể cài đặt thủ công
    ```bash
    pip install pygame numpy matplotlib
    ```
    Sau đó chạy lệnh 
    ```bash
    python main.py  
    ```
    Để kiểm tra các test case chạy lệnh
     ```bash
    python main.py --test  
    ```
    
