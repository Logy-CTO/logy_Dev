from cx_Freeze import setup, Executable
import os

# 이미지 파일이 위치한 경로를 지정합니다.
image_dir = 'C:\\logy\\Mediapipe-VR-Fullbody-Tracking\\bin\\assets'

# include_files 옵션을 위해 (source, destination) 튜플의 리스트를 생성합니다.
include_files = [(os.path.join(image_dir, f), f) for f in os.listdir(image_dir)]

buildOptions = dict(
    packages=[],
    excludes=[],
    include_files=include_files  # include_files 옵션을 설정합니다.
)

exe = [Executable('C:\\logy\\Mediapipe-VR-Fullbody-Tracking\\bin\\mediapipepose.py')]

setup(
    name='vrlogy',
    version='0.0.1',
    author='kook',
    description='description',
    options={'build_exe': buildOptions},
    executables=exe,
)