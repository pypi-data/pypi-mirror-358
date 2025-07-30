import os
import webview
from core.camera import CameraManager
from core.comfyui import ComfyUIManager
from core.server import run_server,get_server_state,get_input_img,get_output_img
from core.flow_api import gen_api_prompt,gen_test_api_prompt,gen_test2_api_prompt
from bridge import expose
from log import logger
from core.utils import open_resource_dir
from core.printer import PrinterManager
from core.gen_qrode import gen_qrcode_base64

INPUT_NAME = 'catch_photos'
OUTPUT_NAME = 'processed_photos'

# 应用程序数据目录
APP_DATA_DIR = os.getcwd() + '/.photostyle'
if not os.path.exists(APP_DATA_DIR):
    os.makedirs(APP_DATA_DIR)

# 拍照图片保存目录
PHOTO_DIR = APP_DATA_DIR + f'/{INPUT_NAME}'
if not os.path.exists(PHOTO_DIR):
    os.makedirs(PHOTO_DIR)

# ai处理后的图片保存目录
PROCESSED_PHOTO_DIR = APP_DATA_DIR + f'/{OUTPUT_NAME}'
if not os.path.exists(PROCESSED_PHOTO_DIR):
    os.makedirs(PROCESSED_PHOTO_DIR)

# 前端页面路径
LOCAL_UI_PATH = './asset/frontend/index.html'
DEV_UI_PATH = 'http://localhost:5173/'

# 是否是生产环境
IS_PROD = os.getenv("PHOTOSTYLE_ENV") == "prod"

out_ts_file=r'.\frontend\src\api.d.ts' if not IS_PROD else None
main_window_url = LOCAL_UI_PATH if IS_PROD else DEV_UI_PATH


main_window = webview.create_window('Photostyle', url=main_window_url,resizable=False,min_size=(1150, 700))
camera_manager = CameraManager(APP_DATA_DIR,PHOTO_DIR)
comfyui_manager = ComfyUIManager(APP_DATA_DIR,PHOTO_DIR,PROCESSED_PHOTO_DIR)
printer_manager = PrinterManager(APP_DATA_DIR,comfyui_manager)

# # 设置窗口为暗色标题栏
# import ctypes
# from ctypes import wintypes
# from webview.platforms.winforms import BrowserView
# dwmapi = ctypes.windll.LoadLibrary("dwmapi")
# main_window.events.shown += lambda: dwmapi.DwmSetWindowAttribute(
#     BrowserView.instances[main_window.uid].Handle.ToInt32(),
#     20,
#     ctypes.byref(ctypes.c_bool(True)),
#     ctypes.sizeof(wintypes.BOOL),
# )


def get_window_size():
    window = webview.active_window()
    width = window.width
    height = window.height
    
    logger.debug(f"窗口尺寸：{width} x {height}")
    return width, height


def set_fullscreen(fullscreen: bool):
    if fullscreen!=main_window.fullscreen:
        main_window.fullscreen = not main_window.fullscreen
        main_window.toggle_fullscreen()
        logger.debug(f"窗口全屏：{fullscreen}")


def get_fullscreen()->bool:
    return main_window.fullscreen


def get_all_catch_photos()->list[str]:
    """獲取所有拍照的图片名稱"""
    photos = [f for f in os.listdir(PHOTO_DIR) if f.endswith('.jpg')]
    return photos


def on_before_show(window):
    logger.debug('窗口即将显示，原生窗口对象：', window.native)

def on_closed():
    logger.debug('pywebview 窗口已关闭')

def on_closing():
    camera_manager.close_camera_streaming()
    comfyui_manager.close_comfyui_streaming()
    logger.debug('pywebview 窗口正在关闭')

def on_shown():
    logger.debug('pywebview 窗口已显示')

def on_minimized():
    logger.debug('pywebview 窗口最小化')

def on_restored():
    logger.debug('pywebview 窗口已还原')

def on_maximized():
    logger.debug('pywebview 窗口最大化')

def on_resized(width, height):
    logger.debug(
        'pywebview 窗口尺寸更改。新尺寸为 {width} x {height}'.format(
            width=width, height=height
        )
    )
    # 调用前端TerminalPage中的fit窗口自适应
    main_window.run_js(f'pywebview.pyapi_terminal_fit({width},{height})')


def start_func():
    camera_manager.open_camera_streaming()
    comfyui_manager.open_comfyui_streaming()
    run_server(APP_DATA_DIR,INPUT_NAME,OUTPUT_NAME)

def main():
    is_debug = not IS_PROD
    
    # 暴露api给前端的接口
    expose(
        main_window, 
        # camera
        camera_manager.switch_camera, 
        camera_manager.scan_camera,
        camera_manager.stop_camera,
        camera_manager.camera_is_stopped,
        camera_manager.get_camera_state,
        camera_manager.get_camera_resolution,
        camera_manager.set_camera_resolution,
        camera_manager.set_camera_face_box,
        camera_manager.set_camera_draw_gender,
        camera_manager.set_camera_face_model,
        camera_manager.set_camera_model_params,
        camera_manager.set_camera_face_box_color,
        camera_manager.set_camera_face_box_thickness,
        camera_manager.catch_photo,
        camera_manager.set_countdown,
        camera_manager.set_lock_screen,
        get_all_catch_photos,
        
        # comfyui
        comfyui_manager.get_comfyui_configs,
        comfyui_manager.get_comfyui_state,
        comfyui_manager.open_comfyui_streaming,
        comfyui_manager.close_comfyui_streaming,
        comfyui_manager.get_comfyui_start_failed_reason,
        comfyui_manager.comfyui_draw,
        comfyui_manager.comfyui_draw_test,
        comfyui_manager.comfyui_draw_test2,
        comfyui_manager.get_comfyui_draw_image,
        comfyui_manager.get_comfyui_output_image,
        comfyui_manager.set_comfyui_configs,
        comfyui_manager.comfyui_api_interrupt,
        comfyui_manager.set_watermark_config,
        comfyui_manager.get_watermark_config,
        comfyui_manager.comfyui_bat_runner,
        
        # printer
        printer_manager.print_photo,
        printer_manager.switch_printer,
        printer_manager.get_printers,
        printer_manager.get_cur_printer,
        printer_manager.get_print_num,
        printer_manager.set_print_num,
        printer_manager.get_img_print_num,
        
        # 本地文件
        open_resource_dir,
        get_server_state,
        get_input_img,
        get_output_img,
        get_window_size,
        set_fullscreen,
        get_fullscreen,
        gen_qrcode_base64,
        # ts
        out_ts_file=out_ts_file,
        )
    
    main_window.events.closed += on_closed
    main_window.events.closing += on_closing
    main_window.events.before_show += on_before_show
    main_window.events.shown += on_shown
    main_window.events.minimized += on_minimized
    main_window.events.maximized += on_maximized
    main_window.events.restored += on_restored
    main_window.events.resized += on_resized
    webview.start(start_func,debug=is_debug,gui='gtk',icon='./logo.ico')


if __name__ == "__main__":
    main()