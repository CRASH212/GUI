import os
from time import sleep
from ftplib import FTP

# 打开文本文件
with open('/home/ppg32/Desktop/11.25版本5图形界面/UploadConfig.txt', 'r') as file:
    # 逐行读取文本内容
    for line in file:
        # 分割每行的键值对
        key, value = line.strip().split(' = ')

        # 根据键名将值赋给对应的变量
        if key == 'ftp_server':
            ftp_server = value
        elif key == 'ftp_port':
            ftp_port = int(value)
        elif key == 'ftp_username':
            ftp_username = value
        elif key == 'ftp_password':
            ftp_password = value
        elif key == 'local_ppg_path':
            local_ppg_path = value
        elif key == 'remote_ppg_path':
            remote_ppg_path = value
        elif key == 'local_radar_path':
            local_radar_path = value
        elif key == 'remote_radar_path':
            remote_radar_path = value


def upload_new_files(ftp, local_path, remote_path):
    # 获取远程文件夹中的文件列表
    ftp.cwd(remote_path)
    remote_files = ftp.nlst(remote_path)
    # 获取本地文件夹中的文件列表
    local_files = os.listdir(local_path)
    # 找出本地新增的文件
    new_files = set(local_files) - set(remote_files)
    # 逐一上传新增的文件
    for file_name in new_files:
        local_file_path = os.path.join(local_path, file_name)
        if os.path.isfile(local_file_path) and file_name not in remote_files:
            # 如果是文件，则上传文件
            encoded_filename = file_name#.encode('utf-8')#.decode("latin1")
            with open(local_file_path, 'rb') as f:
                # ftp.storbinary('STOR ' + file_name, f)
                response = ftp.storbinary(f'STOR {encoded_filename}', f)
                if response == '226 Transfer complete.':
                    f.close()

                    os.remove(local_file_path)
                    print(f"文件 {file_name} 上传成功")

    # 上传完文件后返回上级目录
    ftp.cwd('..')

# 连接 FTP 服务器
print("连接服务器...")
ftp = FTP()
ftp.connect(ftp_server, ftp_port)
ftp.login(ftp_username, ftp_password)
print("连接服务器成功")
# 切换到 FTP 上的目标文件夹
ftp.cwd('radar_ppg')
# 上传新增的子文件
# remote_path = '/path/to/remote/folder'
# ftp_folder =
# 上传新增的ppg文件
#local_ppg_path = 'C:\\1\\ppg'
#remote_ppg_path = 'ppg'
upload_new_files(ftp, local_ppg_path, remote_ppg_path)

# 上传新增的radar文件
#local_radar_path = 'C:\\1\\radar'
#remote_radar_path = 'radar'
upload_new_files(ftp, local_radar_path, remote_radar_path)

# 关闭 FTP 连接
ftp.quit()
